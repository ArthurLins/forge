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
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")


def main() -> int:
    with open(STATE, encoding="utf-8") as fh:
        data = json.load(fh)

    prompts = data["prompts"]
    done = {p["id"] for p in prompts if p.get("status") == "done"}
    runnable_status = {"pending", "in_progress"}

    pending = [p for p in prompts if p.get("status") in runnable_status]
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
