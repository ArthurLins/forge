---
description: Execute only the next eligible prompt of a Forge project (safe, one at a time) in an isolated subagent, then apply the Definition of Done and update tracking.
allowed-tools: Task, Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-next` — run the next eligible prompt (safe, 1×)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Execute
**exactly one** prompt — the next eligible one — and stop. This is the safe,
single-step mode; use `/forge-run` for batches and `/forge-run-phase` for a whole
phase.

This command upholds **Principle 5 — "Agents are orchestrated in isolation"**
(`FORGE.md`): the prompt runs in a **clean subagent** with a fresh context, and
completion **updates the state machine and the derived docs**. The orchestrator
thread stays lean because only a short summary returns.

## Procedure (exactly one prompt)

1. **Find the next eligible prompt** — run `python3 prompts/next_prompt.py`.
   - `DONE` → announce everything is complete and **stop**.
   - `BLOCKED\t<ids>` → explain that the listed pending prompts have unsatisfied
     dependencies, and **stop** (do not force anything).
   - Otherwise the output is `<ID>\t<file>`.

2. **Delegate execution to an ISOLATED subagent** (the `Task` tool, a
   general-purpose agent), passing it this self-contained instruction:

   > You are an agent (Claude, Opus 4.8) in a Forge-built repository, with a
   > **clean context**. Read `prompts/README.md` and the prompt file `<file>`,
   > plus every doc it references in `docs/requirements/` (the source of truth —
   > do **not** invent requirements). Read `forge.config.json` for the project's
   > stack, conventions and CI commands — never hardcode a tool. Read
   > `docs/requirements/conventions.md` (the **Conventions Map**) and apply every
   > `EC-` rule whose "Applies to" scope matches this prompt's work, within its
   > parameters, recording the honored `EC` ids in code/tests; if a recurring
   > concern is missing from the map, propose it (note `/forge-add-convention`).
   > Execute prompt `<ID>` in full and satisfy the **Definition of Done**
   > (`prompts/README.md`
   > §5): implementation matches the referenced requirements; critical-path tests
   > pass for any path in `forge.config.json → criticalPaths.paths` the prompt
   > touches; the quality gates in `forge.config.json → ci.commands`
   > (`lint`/`typecheck`/`test`/`build`/`docsCheck`) pass; `@requirement <id>`
   > tags are added in code **and tests**; derived docs are synced by running
   > **`/forge-sync-docs`** (or `make forge-sync-docs`). Then mark `<ID>` as
   > `done` in `prompts/state.json` (fill `commit` and `updatedAt`), regenerate
   > `prompts/STATUS.md`, and make a **Conventional Commit**. If you **cannot**
   > finish (error, serious ambiguity, missing dependency), do **not** mark it
   > `done`: leave it `in_progress`, write the reason to
   > `prompts/.logs/<ID>.note.md`, commit the partial progress, and report.
   > Return a summary of at most 8 lines: what you did, the key files, the final
   > status, and any blockers.

3. **Verify the result** — run `python3 prompts/next_prompt.py` again.
   - If the **same `<ID>`** returns, it did not complete → **stop** and show the
     reason from `prompts/.logs/<ID>.note.md`. Do **not** retry automatically.
   - If it advanced to a different id, the prompt is done.

4. **Report** — show the prompt completed now, overall progress (done / total
   from `prompts/state.json`), and the next eligible prompt.

## Notes

- Only the subagent's short summary returns to this thread → the orchestrator
  context stays clean (equivalent to compacting after the prompt, but more
  reliable).
- The subagent needs permission to `git commit`; approve it when prompted, or run
  in a suitable permission mode.
- **Stack-neutral:** every gate/test/command comes from `forge.config.json →
  ci.commands` and `criticalPaths.paths`, and the source of truth is
  `docs/requirements/`. No tool name is hardcoded here.
- Work only on the suite's prompts; never remove `docs/requirements/` or
  `prompts/`.
