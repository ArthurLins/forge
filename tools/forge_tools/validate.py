#!/usr/bin/env python3
"""forge-validate — static integrity gate for a Forge-BUILT project.

DISTRIBUTABLE. Unlike ``selfcheck`` (which guards Forge's own constitution and is
self-only), this validator ships to adopters: it asserts that the *project they
built with Forge* is structurally intact, so a broken state machine, a dangling
traceability tag, a malformed Conventions Map, an invalid config, or stale
derived docs are caught before they merge.

It is **deterministic** and **stack-neutral**: every path and knob is read from
``forge.config.json`` (never hardcoded), and it runs on Python 3 alone — the same
neutral runtime the prompt-suite engine already requires. It must PASS trivially
on an empty / pre-genesis project: with no prompts and no requirements there is
nothing to violate.

Checks
------
  state-integrity          (hard) prompts/state.json: unique ids; every `file`
                                  exists; every `dependsOn` id exists; the
                                  dependency graph has no cycles; statuses are
                                  valid; `prompts/next_prompt.py` runs cleanly.
  claims-integrity         (hard) only if prompts/claims/ exists: each claim file
                                  references a declared prompt and does NOT claim
                                  a `done` prompt (a stale/leaked claim → fail);
                                  the OPTIONAL `heartbeatAt`/`attempts` fields are
                                  shape-checked when present (malformed → fail); a
                                  very old claim, an expired heartbeat, an
                                  over-`maxAttempts` claim, or more ACTIVE claims
                                  than `claims.maxConcurrent` (the WIP limit) →
                                  WARNING. No dir → skip.
  requirement-tag-integrity (hard) every `@requirement`/`@rule` id referenced in
                                  source is DECLARED in docs/requirements/. A
                                  dangling tag fails; a declared requirement with
                                  no implementing tag is a WARNING, not a failure.
  conventions-integrity    (hard) only if docs/requirements/conventions.md exists:
                                  each `EC-` entry has the required fields and ids
                                  are unique.
  config-integrity         (hard) forge.config.json is valid JSON with the
                                  expected top-level keys.
  docs-freshness           (hard) derived docs are not stale (reuses the sync-docs
                                  --check logic).
  source-of-truth-integrity (hard/warn) the human-edited source of truth
                                  (docs/requirements/*.md, prompts/state.json,
                                  forge.config.json) carries NO git conflict
                                  markers (a silently mis-merged spec → hard
                                  fail); every prompt `ref` resolves to an existing
                                  requirement doc → WARNING otherwise (skipped
                                  pre-genesis).

Usage
-----
  python3 -m forge_tools.validate            # human-readable report (PASS/FAIL)
  python3 -m forge_tools.validate --check     # same, exit non-zero on hard fail

Warnings never fail the build. ``--check`` returns non-zero only on a hard
failure.
"""

import datetime
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

from . import common
from . import sync_docs as sync_docs_mod
from .requirements import parse_requirements
from .traceability import scan as scan_tags

STATE_REL = "prompts/state.json"
NEXT_PROMPT_REL = "prompts/next_prompt.py"
PROMPTS_DIR = "prompts"
CLAIMS_DIR = "prompts/claims"
CONFIG_REL = "forge.config.json"
CONVENTIONS_REL = "docs/requirements/conventions.md"
REQ_DIR_REL = "docs/requirements"

# Unambiguous git conflict markers (exactly 7 chars at line start, then a space
# or EOL). The middle `=======` is intentionally NOT matched alone — it collides
# with markdown setext-heading underlines and table rules; a real conflict always
# carries `<<<<<<<` and `>>>>>>>`, so matching those (plus the diff3 `|||||||`)
# detects it without false positives on prose.
CONFLICT_MARKER = re.compile(r"^(?:<{7}|>{7}|\|{7})(?:\s|$)")

VALID_STATUSES = {"pending", "in_progress", "blocked", "done"}

# A claim older than this is flagged (WARNING, never a hard fail): a long-lived
# claim usually means a worker crashed or forgot to release it. Tune to taste —
# the value is advisory, not a gate.
STALE_CLAIM_AGE_DAYS = 7

# Self-healing defaults for the optional heartbeat/attempts claim fields. A
# project overrides these in forge.config.json -> claims.ttlSeconds /
# claims.maxAttempts; both are optional and fall back to these constants. They
# MUST match the selector's defaults in prompts/next_prompt.py.
CLAIM_TTL_SECONDS = 1800
CLAIM_MAX_ATTEMPTS = 3

# Top-level keys a Forge stack profile is expected to carry (the placeholder
# ships all of them; genesis fills their values). Documentation-hint keys
# beginning with "_" are ignored.
EXPECTED_CONFIG_KEYS = [
    "forgeVersion",
    "project",
    "stack",
    "conventions",
    "requirementTiers",
    "compliance",
    "docs",
    "traceability",
    "ci",
]

# Fields every EC entry in the Conventions Map must declare, matched against the
# bullet labels in the entry block (see templates/requirements/conventions.md).
REQUIRED_EC_FIELDS = ["Category", "Rule", "Applies to", "Status"]


# --------------------------------------------------------------------------- #
# Result model (mirrors selfcheck's CheckResult so the report reads the same)
# --------------------------------------------------------------------------- #

class CheckResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.failures: List[str] = []   # hard failures
        self.warnings: List[str] = []   # soft warnings (never fail)
        self.skipped: Optional[str] = None

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def skip(self, msg: str) -> None:
        self.skipped = msg

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        if self.skipped is not None:
            return "SKIP  {0}: {1}".format(self.name, self.skipped)
        status = "PASS" if self.ok else "FAIL"
        lines = ["{0}  {1}".format(status, self.name)]
        for f in self.failures:
            lines.append("        - FAIL: {0}".format(f))
        for w in self.warnings:
            lines.append("        - warn: {0}".format(w))
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _load_state() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Return (state, error). A missing file is NOT an error (pre-genesis)."""
    path = common.repo_path(STATE_REL)
    if not os.path.isfile(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except json.JSONDecodeError as exc:
        return None, "{0} is not valid JSON: {1}".format(STATE_REL, exc)


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_state_integrity() -> CheckResult:
    res = CheckResult("state-integrity")
    state, err = _load_state()
    if err:
        res.fail(err)
        return res
    prompts: List[Dict[str, Any]] = (state or {}).get("prompts") or []

    # Empty / pre-genesis suite: trivially intact.
    if not prompts:
        return res

    ids: List[str] = []
    id_set: Set[str] = set()
    for p in prompts:
        pid = p.get("id")
        if pid is None:
            res.fail("a prompt entry is missing its `id`")
            continue
        pid = str(pid)
        if pid in id_set:
            res.fail("duplicate prompt id: {0}".format(pid))
        id_set.add(pid)
        ids.append(pid)

    # Statuses must be valid.
    for p in prompts:
        pid = str(p.get("id", "?"))
        status = p.get("status")
        if status not in VALID_STATUSES:
            res.fail(
                "prompt {0} has invalid status {1!r} (valid: {2})".format(
                    pid, status, ", ".join(sorted(VALID_STATUSES))
                )
            )

    # Every `file` must exist (relative to prompts/).
    for p in prompts:
        pid = str(p.get("id", "?"))
        rel = (p.get("file") or "").strip()
        if not rel:
            res.fail("prompt {0} has no `file`".format(pid))
            continue
        abs_path = common.repo_path(PROMPTS_DIR, rel)
        if not os.path.isfile(abs_path):
            res.fail(
                "prompt {0} -> file does not exist: {1}/{2}".format(
                    pid, PROMPTS_DIR, rel
                )
            )

    # Every `dependsOn` id must exist; collect edges for the cycle check.
    edges: Dict[str, List[str]] = {pid: [] for pid in id_set}
    for p in prompts:
        pid = str(p.get("id", "?"))
        for dep in p.get("dependsOn") or []:
            dep = str(dep)
            if dep not in id_set:
                res.fail(
                    "prompt {0} dependsOn unknown id: {1}".format(pid, dep)
                )
            elif pid in edges:
                edges[pid].append(dep)

    # Detect a cycle in the dependency graph (DFS with a recursion stack).
    cycle = _find_cycle(edges)
    if cycle:
        res.fail(
            "dependency cycle detected: {0}".format(" -> ".join(cycle))
        )

    # next_prompt.py must run without error.
    next_script = common.repo_path(NEXT_PROMPT_REL)
    if os.path.isfile(next_script):
        try:
            proc = subprocess.run(
                [sys.executable, next_script],
                cwd=common.REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
            )
        except OSError as exc:
            res.fail("could not run {0}: {1}".format(NEXT_PROMPT_REL, exc))
        else:
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "").strip()
                res.fail(
                    "{0} exited {1}: {2}".format(
                        NEXT_PROMPT_REL, proc.returncode, detail
                    )
                )
    return res


def _find_cycle(edges: Dict[str, List[str]]) -> Optional[List[str]]:
    """Return one cycle as a node list, or None. Deterministic (sorted order)."""
    WHITE, GREY, BLACK = 0, 1, 2
    color: Dict[str, int] = {n: WHITE for n in edges}

    def visit(node: str, stack: List[str]) -> Optional[List[str]]:
        color[node] = GREY
        stack.append(node)
        for nxt in sorted(edges.get(node, [])):
            if color.get(nxt, BLACK) == GREY:
                # Found a back-edge — slice the stack from nxt to close the loop.
                idx = stack.index(nxt)
                return stack[idx:] + [nxt]
            if color.get(nxt, BLACK) == WHITE:
                found = visit(nxt, stack)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for start in sorted(edges):
        if color[start] == WHITE:
            found = visit(start, [])
            if found:
                return found
    return None


def check_claims_integrity() -> CheckResult:
    """Validate the sharded prompt claims (parallel-execution safety).

    A claim is `prompts/claims/<promptId>.json` written by the orchestrator while
    a prompt is in flight, so a second worker won't grab the same prompt. This
    check keeps claims honest:

      - the claims dir is OPTIONAL — skip cleanly if it is absent;
      - each claim must reference a prompt that EXISTS in state.json (a dangling
        claim → hard fail);
      - a claim must NOT reference a `done` prompt (a stale/leaked claim that
        would never be released → hard fail);
      - a malformed claim file (bad JSON / mismatched id) → hard fail;
      - the OPTIONAL new fields must be well-shaped when present: `heartbeatAt`
        a parseable ISO-8601 string, `attempts` a non-negative integer — a
        malformed value → hard fail (consistent with the malformed-claim fail);
      - a very old claim (`claimedAt` > STALE_CLAIM_AGE_DAYS) → WARNING;
      - an EXPIRED claim (heartbeat older than the TTL — the selector
        auto-releases it) → WARNING;
      - `attempts` >= maxAttempts on a non-`blocked` prompt → WARNING;
      - more ACTIVE (non-expired) claims than `claims.maxConcurrent` (the
        optional WIP limit; absent / `0` = unlimited) → WARNING.
    """
    res = CheckResult("claims-integrity")
    claims_dir = common.repo_path(CLAIMS_DIR)
    if not os.path.isdir(claims_dir):
        res.skip("no {0}/ (claims are optional)".format(CLAIMS_DIR))
        return res

    files = sorted(
        f
        for f in os.listdir(claims_dir)
        if f.endswith(".json") and f != ".gitkeep"
    )
    if not files:
        # Dir present but empty (only .gitkeep) — nothing claimed, nothing wrong.
        return res

    state, err = _load_state()
    if err:
        res.fail(err)
        return res
    prompts: List[Dict[str, Any]] = (state or {}).get("prompts") or []
    id_to_status: Dict[str, Optional[str]] = {
        str(p.get("id")): p.get("status") for p in prompts if p.get("id") is not None
    }

    ttl_seconds, max_attempts, max_concurrent = _claims_config()
    now = datetime.datetime.now(datetime.timezone.utc)
    active_claims = 0  # non-expired claims, for the optional WIP-limit warning
    for fname in files:
        claim_id = fname[: -len(".json")]
        path = os.path.join(claims_dir, fname)
        try:
            with open(path, encoding="utf-8") as fh:
                claim = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            res.fail("claim {0} is not readable JSON: {1}".format(fname, exc))
            continue

        # The in-file promptId, when present, must match the file name.
        declared = str(claim.get("promptId")) if isinstance(claim, dict) else None
        if declared and declared != claim_id:
            res.fail(
                "claim {0} declares promptId {1!r} — it must match the file "
                "name".format(fname, declared)
            )

        # The claimed prompt must exist in the state machine.
        if claim_id not in id_to_status:
            res.fail(
                "claim {0} references an unknown prompt id — remove the stale "
                "claim or fix it".format(fname)
            )
            continue

        # A claim on a `done` prompt is a leak: it would never be released and
        # would silently hide the prompt from selection.
        if id_to_status[claim_id] == "done":
            res.fail(
                "claim {0} references a `done` prompt — a stale/leaked claim; "
                "remove prompts/claims/{0}".format(fname)
            )
            continue

        # An old claim is suspicious (crashed/forgotten worker) but not fatal.
        claimed_at = (claim.get("claimedAt") or "").strip() if isinstance(claim, dict) else ""
        age = _claim_age_days(claimed_at, now)
        if age is not None and age > STALE_CLAIM_AGE_DAYS:
            res.warn(
                "claim {0} is {1} day(s) old (claimedAt {2}) — verify the worker "
                "is still active or release it".format(fname, age, claimed_at)
            )

        # OPTIONAL self-healing fields. Validate their SHAPE when present (a
        # malformed value is a hard fail, like a malformed claim), then surface
        # the lifecycle WARNINGs (expired heartbeat / over-attempt).
        # A claim is ACTIVE (counts toward the WIP limit) unless it has a
        # parseable `heartbeatAt` older than the TTL — the same active/expired
        # rule the selector applies (no heartbeat → active; expired → released).
        is_active = True
        if "heartbeatAt" in claim:
            heartbeat = _parse_iso(claim.get("heartbeatAt"))
            if heartbeat is None:
                res.fail(
                    "claim {0} has a malformed `heartbeatAt` — it must be a "
                    "parseable ISO-8601 string".format(fname)
                )
            else:
                age_seconds = (now - heartbeat).total_seconds()
                if age_seconds > ttl_seconds:
                    is_active = False
                    res.warn(
                        "claim {0} heartbeat expired ({1:.0f}s > ttl {2}s, "
                        "heartbeatAt {3}) — the selector auto-releases it; remove "
                        "it if the worker is gone".format(
                            fname, age_seconds, ttl_seconds, claim.get("heartbeatAt")
                        )
                    )
        if is_active:
            active_claims += 1

        if "attempts" in claim:
            attempts = claim.get("attempts")
            if not _is_non_negative_int(attempts):
                res.fail(
                    "claim {0} has a malformed `attempts` — it must be a "
                    "non-negative integer".format(fname)
                )
            elif attempts >= max_attempts and id_to_status.get(claim_id) != "blocked":
                res.warn(
                    "claim {0} reached maxAttempts ({1} >= {2}) — move the prompt "
                    "to `blocked` or reset attempts".format(
                        fname, attempts, max_attempts
                    )
                )

    # OPTIONAL WIP limit (claims.maxConcurrent). A WARNING, never a hard fail:
    # bounded WIP keeps queues short and feedback fast, but it is advisory. Only
    # ACTIVE (non-expired) claims count; absent / `0` maxConcurrent = unlimited
    # (no warning — today's behavior).
    if max_concurrent > 0 and active_claims > max_concurrent:
        res.warn(
            "{0} active claims exceed claims.maxConcurrent={1} — WIP limit "
            "exceeded; finish or release in-flight prompts before claiming "
            "more".format(active_claims, max_concurrent)
        )
    return res


def _claims_config() -> Tuple[int, int, int]:
    """Return ``(ttlSeconds, maxAttempts, maxConcurrent)`` from config -> claims.

    All three are optional. ``ttlSeconds`` / ``maxAttempts`` fall back to the
    module constants on an absent / non-positive value (same defaults the
    selector uses). ``maxConcurrent`` is the OPTIONAL WIP limit: a non-negative
    integer cap on active claims; absent / `0` / invalid = `0` = unlimited (no
    WIP warning — today's behavior).
    """
    cfg = common.load_config()
    claims = cfg.get("claims") if isinstance(cfg, dict) else None
    claims = claims if isinstance(claims, dict) else {}

    ttl = CLAIM_TTL_SECONDS
    try:
        candidate = int(claims.get("ttlSeconds"))
        if candidate > 0:
            ttl = candidate
    except (TypeError, ValueError):
        pass

    max_attempts = CLAIM_MAX_ATTEMPTS
    try:
        candidate = int(claims.get("maxAttempts"))
        if candidate > 0:
            max_attempts = candidate
    except (TypeError, ValueError):
        pass

    max_concurrent = 0  # 0 = unlimited (no WIP limit configured).
    try:
        candidate = int(claims.get("maxConcurrent"))
        if candidate > 0:
            max_concurrent = candidate
    except (TypeError, ValueError):
        pass

    return ttl, max_attempts, max_concurrent


def _is_non_negative_int(value: Any) -> bool:
    """True only for a real non-negative integer (rejects bool, str, float)."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _parse_iso(text: Any) -> Optional[datetime.datetime]:
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None.

    Handles a trailing ``Z`` and explicit offsets; a naive timestamp is treated
    as UTC. A non-string or unparseable value returns None (the caller treats
    that as a malformed shape).
    """
    if not isinstance(text, str) or not text.strip():
        return None
    cleaned = text.strip()
    if cleaned[-1] in ("Z", "z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def _claim_age_days(claimed_at: str, now: datetime.datetime) -> Optional[int]:
    """Age of a claim in whole days, or None if `claimedAt` is unparseable.

    Accepts an ISO-8601 timestamp (with or without a trailing ``Z``) or a bare
    ``YYYY-MM-DD`` date. A missing/garbled value is simply not aged (returns
    None) — the claim is still validated for existence and `done`-status.
    """
    if not claimed_at:
        return None
    text = claimed_at.replace("Z", "+00:00")
    parsed: Optional[datetime.datetime] = None
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.datetime.strptime(claimed_at[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    delta = now - parsed
    return max(delta.days, 0)


def check_requirement_tag_integrity() -> CheckResult:
    res = CheckResult("requirement-tag-integrity")
    config = common.load_config()
    globs = common.traceability_globs(config)
    aliases = common.tag_aliases(config)

    declared = parse_requirements()
    declared_ids = {r.id for r in declared}

    raw_index = scan_tags(globs, aliases)
    referenced = set(raw_index.keys())

    # A tagged id is OK if it (or a declared ancestor, for dotted sub-ids) is
    # declared. Roll a dotted sub-id up to its nearest declared ancestor.
    def resolves(rid: str) -> bool:
        if rid in declared_ids:
            return True
        parent = rid
        while "." in parent:
            parent = parent.rsplit(".", 1)[0]
            if parent in declared_ids:
                return True
        return False

    dangling = sorted(rid for rid in referenced if not resolves(rid))
    for rid in dangling:
        res.fail(
            "tag references an undeclared requirement: {0} — declare it in "
            "docs/requirements/ or fix the tag".format(rid)
        )

    # A declared requirement with no implementing tag is a WARNING, not a fail.
    def is_covered(rid: str) -> bool:
        if rid in referenced:
            return True
        # A parent is covered if any dotted child id rolls up to it.
        for ref in referenced:
            cur = ref
            while "." in cur:
                cur = cur.rsplit(".", 1)[0]
                if cur == rid:
                    return True
        return False

    untagged = sorted(rid for rid in declared_ids if not is_covered(rid))
    for rid in untagged:
        res.warn("declared requirement has no implementing tag yet: {0}".format(rid))
    return res


def check_conventions_integrity() -> CheckResult:
    res = CheckResult("conventions-integrity")
    path = common.repo_path(CONVENTIONS_REL)
    if not os.path.isfile(path):
        res.skip("no {0} (Conventions Map not present)".format(CONVENTIONS_REL))
        return res

    text = common.read_text(path)
    lines = text.splitlines()

    # Each EC entry starts with a heading "### EC-01 — Title". Collect the body
    # up to the next heading and check the required field bullets are present.
    heading = re.compile(r"^#{2,6}\s+(EC-\d+)\b\s*[—-]\s*(.*)$")
    entries: List[Tuple[str, int]] = []  # (id, start line index)
    for i, line in enumerate(lines):
        m = heading.match(line.strip())
        if m:
            entries.append((m.group(1), i))

    if not entries:
        res.warn(
            "{0} exists but declares no EC- entries".format(CONVENTIONS_REL)
        )
        return res

    seen: Dict[str, int] = {}
    for idx, (ec_id, start) in enumerate(entries):
        if ec_id in seen:
            res.fail(
                "duplicate convention id {0} (first at line {1}, again at line "
                "{2})".format(ec_id, seen[ec_id] + 1, start + 1)
            )
        else:
            seen[ec_id] = start

        end = entries[idx + 1][1] if idx + 1 < len(entries) else len(lines)
        body = "\n".join(lines[start + 1:end])
        for field in REQUIRED_EC_FIELDS:
            # Match a bolded field label, e.g. "- **Category:**" / "**Rule (...)**".
            pattern = re.compile(
                r"\*\*\s*" + re.escape(field) + r"\b[^*]*:?\s*\*\*", re.IGNORECASE
            )
            if not pattern.search(body):
                res.fail(
                    "convention {0} is missing required field '{1}'".format(
                        ec_id, field
                    )
                )
    return res


def check_config_integrity() -> CheckResult:
    res = CheckResult("config-integrity")
    path = common.repo_path(CONFIG_REL)
    if not os.path.isfile(path):
        res.fail("{0} is missing".format(CONFIG_REL))
        return res
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        res.fail("{0} is not valid JSON: {1}".format(CONFIG_REL, exc))
        return res
    if not isinstance(data, dict):
        res.fail("{0} top-level value must be a JSON object".format(CONFIG_REL))
        return res
    for key in EXPECTED_CONFIG_KEYS:
        if key not in data:
            res.fail(
                "{0} is missing expected top-level key '{1}'".format(
                    CONFIG_REL, key
                )
            )
    return res


def check_docs_freshness() -> CheckResult:
    res = CheckResult("docs-freshness")
    # Reuse the sync-docs --check logic. Capture its stdout/stderr so the report
    # stays a single clean PASS/FAIL line; surface a short diagnostic on failure.
    import io
    from contextlib import redirect_stderr, redirect_stdout

    out_buf, err_buf = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = sync_docs_mod.main(["--check"])
    except Exception as exc:  # pragma: no cover - defensive
        res.fail("sync-docs --check raised: {0}".format(exc))
        return res
    if rc != 0:
        res.fail(
            "derived docs are stale — run `make forge-sync-docs` and commit "
            "the diff (run `make forge-sync-docs-check` to see it)"
        )
    return res


def _iter_source_of_truth_files() -> List[str]:
    """Repo-relative source-of-truth files to scan for conflict markers: every
    `*.md` under docs/requirements/, plus state.json and forge.config.json."""
    files: List[str] = []
    for rel in (STATE_REL, CONFIG_REL):
        if os.path.isfile(common.repo_path(rel)):
            files.append(rel)
    req_dir = common.repo_path(REQ_DIR_REL)
    if os.path.isdir(req_dir):
        for dirpath, _dirnames, filenames in os.walk(req_dir):
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    files.append(
                        common.rel_to_repo(os.path.join(dirpath, fn))
                    )
    return files


def _requirement_doc_basenames() -> Set[str]:
    """Basenames (without `.md`) of the requirement docs that exist."""
    out: Set[str] = set()
    req_dir = common.repo_path(REQ_DIR_REL)
    if not os.path.isdir(req_dir):
        return out
    for fn in os.listdir(req_dir):
        if fn.endswith(".md"):
            out.add(fn[: -len(".md")])
    return out


def check_source_of_truth_integrity() -> CheckResult:
    """Guard the human-edited source of truth against silent merge damage.

    The requirement docs and `prompts/state.json` are NOT union-merged (they are
    source, not derived — see docs/guides/teams.md), so a parallel merge can
    conflict. forge-validate runs as a required merge-queue check (when
    `ci.strictValidation` is on), so enforcing two protections here stops a
    broken spec from landing:

      - HARD FAIL on any git conflict marker (`<<<<<<<`, `>>>>>>>`, `|||||||`) in
        the source of truth — a silently mis-merged spec would otherwise ship;
      - WARNING when a prompt `ref` does not resolve to an existing requirement
        doc under docs/requirements/ (skipped pre-genesis, when none exists).
    """
    res = CheckResult("source-of-truth-integrity")

    # 1) Conflict markers in the source of truth (hard fail).
    for rel in _iter_source_of_truth_files():
        try:
            with open(
                common.repo_path(rel), encoding="utf-8", errors="replace"
            ) as fh:
                for lineno, line in enumerate(fh, 1):
                    if CONFLICT_MARKER.match(line):
                        res.fail(
                            "{0}:{1} contains a git conflict marker — resolve "
                            "the merge before landing".format(rel, lineno)
                        )
        except OSError:
            continue

    # 2) ref -> requirement-doc consistency (warning). Only meaningful once
    #    genesis has produced requirement docs; skip cleanly otherwise.
    doc_names = _requirement_doc_basenames()
    if doc_names:
        state, err = _load_state()
        if not err and state:
            for p in state.get("prompts") or []:
                pid = str(p.get("id", "?"))
                for ref in p.get("refs") or []:
                    ref_s = str(ref).strip()
                    if not ref_s:
                        continue
                    base = ref_s[:-3] if ref_s.endswith(".md") else ref_s
                    if base not in doc_names:
                        res.warn(
                            "prompt {0} references `{1}`, which is not a "
                            "requirement doc under {2}/ — fix the ref or add "
                            "the doc".format(pid, ref_s, REQ_DIR_REL)
                        )
    return res


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def run_all() -> List[CheckResult]:
    return [
        check_state_integrity(),
        check_claims_integrity(),
        check_requirement_tag_integrity(),
        check_conventions_integrity(),
        check_config_integrity(),
        check_docs_freshness(),
        check_source_of_truth_integrity(),
    ]


def _render_report(results: List[CheckResult]) -> Tuple[str, bool, int]:
    """Return (report_text, all_hard_passed, warning_count)."""
    lines: List[str] = []
    lines.append("forge-validate — project integrity gate")
    lines.append("=" * 42)
    lines.append("")
    hard_ok = True
    warn_count = 0
    for r in results:
        lines.append(r.render())
        if not r.ok:
            hard_ok = False
        warn_count += len(r.warnings)
    lines.append("")
    lines.append("-" * 42)
    if hard_ok:
        summary = "RESULT: PASS"
        if warn_count:
            summary += " ({0} warning(s) to review)".format(warn_count)
    else:
        failing = [r.name for r in results if not r.ok]
        summary = "RESULT: FAIL — {0}".format(", ".join(failing))
    lines.append(summary)
    return "\n".join(lines) + "\n", hard_ok, warn_count


def main(argv: List[str]) -> int:
    check = "--check" in argv
    results = run_all()
    report, hard_ok, _warn = _render_report(results)
    sys.stdout.write(report)
    if check and not hard_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
