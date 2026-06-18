---
description: Execute the next eligible Forge prompt(s) — one, the next N, or all currently eligible — each in an isolated subagent, applying the Definition of Done and updating tracking after each.
argument-hint: '[1 | N | all]  (default: 1 prompt)'
allowed-tools: Task, Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-run` — execute the next eligible prompt(s)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Execute
the suite of build prompts in order, in batches, updating tracking after each.
Use `/forge-next` for the strict single-step mode and `/forge-run-phase` to run a
whole phase.

**How many to run this invocation:** `$ARGUMENTS` — if empty, run **1** prompt;
if a number **N**, run up to N; if **`all`**, keep going until the suite is
complete or progress is blocked.

This command upholds **Principle 5 — "Agents are orchestrated in isolation"**
(`FORGE.md`): **each prompt runs in its own clean subagent**, and completing a
prompt **updates the state machine and the derived docs** before the next one
starts. Only short summaries return to this thread, so its context stays lean
even in `all` mode.

## Procedure (repeat for the requested count)

1. **Find the next eligible prompt** — run `python3 prompts/next_prompt.py`.
   - `DONE` → announce total completion and **stop**.
   - `BLOCKED\t<ids>` → explain the pending prompts have unsatisfied dependencies
     and **stop**.
   - Otherwise the output is `<ID>\t<file>`.

2. **Delegate to an ISOLATED subagent** (the `Task` tool, a general-purpose
   agent) with this self-contained instruction:

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
   > tags are added in code **and tests**; derived docs are synced via
   > **`/forge-sync-docs`** (or `make forge-sync-docs`). Then mark `<ID>` as
   > `done` in `prompts/state.json` (fill `commit` and `updatedAt`), regenerate
   > `prompts/STATUS.md`, and make a **Conventional Commit**. If you **cannot**
   > finish, do **not** mark it `done`: leave it `in_progress`, write the reason
   > to `prompts/.logs/<ID>.note.md`, commit the partial progress, and report.
   > Return a summary of at most 8 lines: what you did, the key files, the final
   > status, and any blockers.

3. **Verify and decide whether to continue** — run `python3
   prompts/next_prompt.py` again.
   - If the **same `<ID>`** returns (it did not complete) → **stop** and show the
     reason from `prompts/.logs/<ID>.note.md`. Do **not** retry automatically.
   - If it advanced and there is still count remaining (N not reached, or `all`),
     go back to step 1.

## When done

Show a summary: prompts completed this run, the next eligible prompt, and overall
progress (e.g. done X / total) from `prompts/state.json`. In `all` mode, if the
orchestrator context grows large, suggest `/compact` and continuing, or running
phase by phase with `/forge-run-phase`.

## Notes

- Each prompt runs **isolated** in a subagent; only its summary returns → the
  orchestrator stays lean for the whole run.
- The subagent needs permission to `git commit`; approve it when prompted.
- **Stack-neutral:** every gate/test/command comes from `forge.config.json →
  ci.commands` and `criticalPaths.paths`, and the source of truth is
  `docs/requirements/`. No tool name is hardcoded here.
- Work only on the suite's prompts; never remove `docs/requirements/` or
  `prompts/`.
