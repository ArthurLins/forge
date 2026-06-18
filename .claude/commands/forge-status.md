---
description: Show a Forge project's progress — done/total, status breakdown, the next eligible prompt, and any blocked prompts — by reading prompts/state.json and next_prompt.py.
allowed-tools: Bash, Read
---

# `/forge-status` — show the prompt-suite progress

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Read the
state machine and present a clear, human-readable progress report. This is
read-only — it changes nothing.

`prompts/state.json` is the machine-readable source of tracking and
`prompts/STATUS.md` is its generated human view; `python3 prompts/next_prompt.py`
selects the next eligible prompt by topological order over `dependsOn`. Nothing
here is stack- or domain-specific.

## Procedure

1. **Counts and status breakdown** — run:

   ```bash
   python3 - <<'PY'
   import json, pathlib
   d = json.loads(pathlib.Path("prompts/state.json").read_text(encoding="utf-8"))
   prompts = d.get("prompts", [])
   total = len(prompts)
   by = {}
   for p in prompts:
       by[p["status"]] = by.get(p["status"], 0) + 1
   print(f"Project: {d.get('project','(unnamed)')}  (version {d.get('version','?')})")
   print(f"Done: {by.get('done', 0)}/{total}")
   if by:
       print("By status: " + ", ".join(f"{k}={v}" for k, v in by.items()))
   # Phase rollup
   phases = {ph['id']: ph['name'] for ph in d.get('phases', [])}
   for pid, name in phases.items():
       ps = [p for p in prompts if p.get('phase') == pid]
       done = sum(1 for p in ps if p['status'] == 'done')
       print(f"  Phase {pid} — {name}: {done}/{len(ps)}")
   PY
   ```

2. **Next eligible prompt** — run `python3 prompts/next_prompt.py` and report:
   - `<ID>\t<file>` → name the next prompt to run (suggest `/forge-next`,
     `/forge-run`, or `/forge-run-phase`).
   - `DONE` → the suite is complete.
   - `BLOCKED\t<ids>` → list the blocked prompts.

3. **Blocked / pending detail** — from `prompts/state.json`, list any prompt whose
   `status` is `blocked`, and the next few `pending` prompts with their
   `dependsOn`, so the developer can see what is waiting on what. Cross-check with
   `prompts/STATUS.md` (the generated view) for the current phase.

## Notes

- Read-only: do not modify `state.json`, `STATUS.md`, or any prompt file.
- If `prompts/state.json` has no prompts yet, the project was never genesised —
  point the developer to `/forge-init`.
- If `prompts/STATUS.md` disagrees with `state.json`, it is stale — suggest
  running `/forge-sync-docs` (or `make forge-status`) to regenerate it.
