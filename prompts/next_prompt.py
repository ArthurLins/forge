#!/usr/bin/env python3
"""Select the next eligible prompt from prompts/state.json.

Output (stdout), TAB-separated:
  <ID>\t<file>     -> next prompt to run (pending or in_progress with deps satisfied)
  DONE             -> everything done (or no prompts yet)
  BLOCKED\t<ids>   -> there are pending prompts but none has its dependsOn satisfied

Usage: python3 prompts/next_prompt.py

The engine is stack- and domain-neutral: eligibility is pure topological order
over `dependsOn`, with no project-specific logic. `state.json` lives next to this
file (path-relative); nothing about the host project is hardcoded.

Sharded claims (parallel-execution safety)
------------------------------------------
When several contributors run the suite at once, two of them must not pick the
same prompt. A *claim* is a small file `prompts/claims/<promptId>.json` written
by the orchestrator before it delegates a prompt to a subagent. This selector
**skips any prompt that has a claim file**, so a second worker selects the next
free prompt instead (or reports BLOCKED/DONE). The mechanism is fully backward
compatible: if `prompts/claims/` is absent or holds only `.gitkeep`, behavior is
identical to before. Reading claims uses the standard library only (a directory
listing) — no extra dependency.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
CLAIMS_DIR = os.path.join(HERE, "claims")


def claimed_ids() -> set:
    """Prompt ids that currently have a claim file in prompts/claims/.

    A claim is a file named `<promptId>.json`. The directory is optional: if it
    does not exist (or contains only `.gitkeep`), no prompt is claimed and the
    selector behaves exactly as it did before claims existed. Reading is a plain
    directory listing — stdlib only, no parsing of the claim contents required to
    decide eligibility.
    """
    if not os.path.isdir(CLAIMS_DIR):
        return set()
    ids = set()
    for name in os.listdir(CLAIMS_DIR):
        if name == ".gitkeep" or not name.endswith(".json"):
            continue
        ids.add(name[: -len(".json")])
    return ids


def main() -> int:
    with open(STATE, encoding="utf-8") as fh:
        data = json.load(fh)

    prompts = data["prompts"]
    done = {p["id"] for p in prompts if p.get("status") == "done"}
    claimed = claimed_ids()
    runnable_status = {"pending", "in_progress"}

    # A prompt being actively worked on carries a claim; skip it so a second
    # worker won't grab it. (Claims never touch `done` prompts.)
    pending = [
        p
        for p in prompts
        if p.get("status") in runnable_status and p["id"] not in claimed
    ]
    if not pending:
        print("DONE")
        return 0

    # File order is already topological (by phase/sequence).
    for p in pending:
        deps = p.get("dependsOn", []) or []
        if all(d in done for d in deps):
            print(f"{p['id']}\t{p.get('file', '')}")
            return 0

    # Nothing eligible: pending prompts have unsatisfied dependencies.
    ids = ",".join(p["id"] for p in pending)
    print(f"BLOCKED\t{ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
