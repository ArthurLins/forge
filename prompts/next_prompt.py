#!/usr/bin/env python3
"""Select the next eligible prompt from prompts/state.json.

Output (stdout), TAB-separated:
  <ID>\t<file>     -> next prompt to run (pending or in_progress with deps satisfied)
  DONE             -> everything done (or no prompts yet)
  BLOCKED\t<ids>   -> there are pending prompts but none has its dependsOn satisfied

Usage: python3 prompts/next_prompt.py [--by-impact]

The engine is stack- and domain-neutral: eligibility is pure topological order
over `dependsOn`, with no project-specific logic. `state.json` lives next to this
file (path-relative); nothing about the host project is hardcoded.

Impact-aware ordering (`--by-impact`)
-------------------------------------
By DEFAULT the selector returns the first eligible prompt in file order — the
historical behavior, unchanged. With the optional `--by-impact` flag it instead
returns, AMONG the same already-eligible set, the prompt that unblocks the MOST
directly-dependent still-pending work: the one whose id appears in the most
`dependsOn` lists of pending/in_progress prompts. Ties fall back to file order
(stable). This is a pure reordering of the eligible set — it never returns an
ineligible or actively-claimed prompt, reads no config, and leaves the output
contract (`<id>\t<file>` / `DONE` / `BLOCKED\t<ids>`) untouched. An orchestrator
running with parallelism uses it to pick high-impact work first, keeping the
dependency frontier wide.

Sharded claims (parallel-execution safety)
------------------------------------------
When several contributors run the suite at once, two of them must not pick the
same prompt. A *claim* is a small file `prompts/claims/<promptId>.json` written
by the orchestrator before it delegates a prompt to a subagent. This selector
**skips any prompt that has a claim file**, so a second worker selects the next
free prompt instead (or reports BLOCKED/DONE). The mechanism is fully backward
compatible: if `prompts/claims/` is absent or holds only `.gitkeep`, behavior is
identical to before. Reading claims uses the standard library only — no extra
dependency.

Heartbeat / TTL self-healing
----------------------------
A claim MAY carry an optional `heartbeatAt` (ISO-8601) that the orchestrator
refreshes while the prompt is in flight. If a worker crashes it stops refreshing,
so the claim's heartbeat goes stale; once `now - heartbeatAt` exceeds the TTL
(`CLAIM_TTL_SECONDS`, overridable via `forge.config.json -> claims.ttlSeconds`)
the selector treats the claim as **expired** and the prompt becomes eligible
again — no manual deletion needed (the file is left in place, non-destructively).

This is strictly backward compatible:
  - a claim WITHOUT `heartbeatAt` is NEVER auto-released (it stays active, exactly
    as before — legacy claims are honored);
  - a malformed claim (bad JSON / unparseable timestamp) is treated as ACTIVE, so
    a prompt is never wrongly released on bad input;
  - a missing claims dir behaves exactly as before.
The selector never raises on bad claim input.
"""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
CLAIMS_DIR = os.path.join(HERE, "claims")

# Self-healing defaults (seconds / count). A project overrides these in
# forge.config.json -> claims.ttlSeconds / claims.maxAttempts; both are optional,
# and an absent/unreadable/invalid config falls back to these constants.
CLAIM_TTL_SECONDS = 1800
CLAIM_MAX_ATTEMPTS = 3


def _find_config() -> str:
    """Walk up from HERE to the nearest `forge.config.json`, or "" if none."""
    cur = HERE
    while True:
        candidate = os.path.join(cur, "forge.config.json")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            return ""
        cur = parent


def claim_ttl_seconds() -> int:
    """TTL in seconds: `claims.ttlSeconds` if valid, else CLAIM_TTL_SECONDS.

    Defensive: an absent, unreadable or invalid config (or a non-numeric /
    non-positive value) falls back to the constant. Stdlib `json` only.
    """
    path = _find_config()
    if not path:
        return CLAIM_TTL_SECONDS
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        value = (cfg.get("claims") or {}).get("ttlSeconds")
        ttl = int(value)
        if ttl > 0:
            return ttl
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return CLAIM_TTL_SECONDS


def _parse_iso(text):
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None.

    Handles a trailing `Z` and explicit offsets; a naive timestamp is treated as
    UTC. Returns None on any unparseable input (the caller decides what that
    means — here, a missing/garbled heartbeat means "active").
    """
    if not isinstance(text, str) or not text.strip():
        return None
    cleaned = text.strip()
    if cleaned.endswith("Z") or cleaned.endswith("z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _claim_is_active(path: str, now: datetime, ttl_seconds: int) -> bool:
    """True if a claim file marks its prompt as still in flight (skip it).

    A claim is ACTIVE unless it is *expired*: expired ⇔ it has a parseable
    `heartbeatAt` AND `now - heartbeatAt > ttl`. A claim without a heartbeat is
    never auto-released (active). Any error reading/parsing the claim → active
    (never wrongly release on bad input). Expiry is non-destructive: the file is
    left untouched so the prompt simply becomes eligible again.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            claim = json.load(fh)
        if not isinstance(claim, dict):
            return True
        heartbeat = _parse_iso(claim.get("heartbeatAt"))
        if heartbeat is None:
            # No (or unparseable) heartbeat -> legacy/active, never released.
            return True
        age = (now - heartbeat).total_seconds()
        return age <= ttl_seconds
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return True


def claimed_ids() -> set:
    """Prompt ids whose claim is still ACTIVE in prompts/claims/.

    A claim is a file named `<promptId>.json`. The directory is optional: if it
    does not exist (or contains only `.gitkeep`), no prompt is claimed and the
    selector behaves exactly as it did before claims existed. A claim whose
    `heartbeatAt` has gone stale (older than the TTL) is treated as expired and
    is *omitted* here, so the prompt is selectable again (self-healing). Reading
    is stdlib-only and never raises.
    """
    if not os.path.isdir(CLAIMS_DIR):
        return set()
    now = datetime.now(timezone.utc)
    ttl = claim_ttl_seconds()
    ids = set()
    for name in os.listdir(CLAIMS_DIR):
        if name == ".gitkeep" or not name.endswith(".json"):
            continue
        path = os.path.join(CLAIMS_DIR, name)
        if _claim_is_active(path, now, ttl):
            ids.add(name[: -len(".json")])
    return ids


def _impact_score(prompt_id, pending) -> int:
    """How many still-pending prompts directly depend on `prompt_id`.

    Counts pending/in_progress prompts (the `pending` set already excludes
    `done`/`blocked`/claimed) that list `prompt_id` in their `dependsOn`. Higher
    score = unblocks more work. Pure count over the already-eligible universe; no
    config, no project assumptions.
    """
    score = 0
    for other in pending:
        if other["id"] == prompt_id:
            continue
        if prompt_id in (other.get("dependsOn", []) or []):
            score += 1
    return score


def main(argv=None) -> int:
    # Minimal stdlib argv parsing: `--by-impact` may appear in any position; any
    # other token is ignored so the selector never raises on stray input.
    args = sys.argv[1:] if argv is None else argv
    by_impact = "--by-impact" in args

    with open(STATE, encoding="utf-8") as fh:
        data = json.load(fh)

    prompts = data["prompts"]
    done = {p["id"] for p in prompts if p.get("status") == "done"}
    claimed = claimed_ids()
    runnable_status = {"pending", "in_progress"}

    # A prompt being actively worked on carries a live claim; skip it so a second
    # worker won't grab it. (Claims never touch `done` prompts.) An expired claim
    # is not in `claimed`, so its prompt is eligible again.
    pending = [
        p
        for p in prompts
        if p.get("status") in runnable_status and p["id"] not in claimed
    ]
    if not pending:
        print("DONE")
        return 0

    # The eligible set: pending prompts whose dependencies are all satisfied.
    # File order is already topological (by phase/sequence), so it is the stable
    # tie-break for `--by-impact` and the sole order for the default path.
    eligible = [
        p
        for p in pending
        if all(d in done for d in (p.get("dependsOn", []) or []))
    ]

    if eligible:
        if by_impact:
            # Reorder the SAME eligible set: most-unblocking first, file order as
            # a stable tie-break (max() keeps the first max on equal scores).
            chosen = max(eligible, key=lambda p: _impact_score(p["id"], pending))
        else:
            chosen = eligible[0]
        print(f"{chosen['id']}\t{chosen.get('file', '')}")
        return 0

    # Nothing eligible: pending prompts have unsatisfied dependencies.
    ids = ",".join(p["id"] for p in pending)
    print(f"BLOCKED\t{ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
