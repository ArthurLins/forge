---
description: Execute ALL prompts of one phase of a Forge project, each prompt in an isolated subagent (clean context), respecting dependsOn and stopping on the first failure.
argument-hint: '<phase id>  (e.g. /forge-run-phase 1) — defaults to the next eligible prompt''s phase'
allowed-tools: Task, Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-run-phase` — run a whole phase (healthy context)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Goal:
execute **all** pending prompts of the target phase, one at a time, **each in an
isolated subagent with a clean context**. The orchestrator thread stays lean for
the entire phase — the effect of "compact after each prompt", but more reliable
(the subagent returns only a short summary).

This command upholds **Principle 5 — "Agents are orchestrated in isolation"**
(`FORGE.md`). Eligibility is topological over `dependsOn`, so the phase runs in
dependency order; the first failure stops the phase with a clear report.

**Target phase:** `$ARGUMENTS` — if empty, use the phase of the next eligible
prompt.

## Procedure

1. **Determine the target phase.**
   - If `$ARGUMENTS` holds a phase id, use it. (Phase ids are whatever
     `prompts/state.json → phases[].id` declares — they are project-defined, not
     a fixed range.)
   - Otherwise run `python3 prompts/next_prompt.py`, take the returned `<ID>`
     (`P<phase>.<seq>`), and use its phase component.

2. **Phase loop — repeat:**
   a. Run `python3 prompts/next_prompt.py`.
      - `DONE` → announce total completion and **stop**.
      - `BLOCKED\t<ids>` → report the blocked prompts and **stop**.
      - `<ID>\t<file>`: if `<ID>` does **not** belong to the target phase, the
        phase is finished → go to step 3.
   b. **Claim it (parallel-execution safety).** Before delegating, write a claim
      file so a second contributor running the suite in parallel will not pick the
      same prompt: `prompts/claims/<ID>.json` =
      `{ "promptId": "<ID>", "owner": "<you/agent>", "claimedAt": "<ISO-8601 now>" }`.
      `prompts/next_prompt.py` skips any claimed prompt, so the other worker
      selects the next free one (or reports `BLOCKED`/`DONE`).

   c. **Delegate to an ISOLATED subagent** (the `Task` tool, a general-purpose
      agent) with this self-contained instruction:

      > You are an agent (Claude, Opus 4.8) in a Forge-built repository, with a
      > **clean context**. Read `prompts/README.md` and the prompt file `<file>`,
      > plus every doc it references in `docs/requirements/` (the source of truth
      > — do **not** invent requirements). Read `forge.config.json` for the
      > project's stack, conventions and CI commands — never hardcode a tool.
      > Read `docs/requirements/conventions.md` (the **Conventions Map**) and
      > apply every `EC-` rule whose "Applies to" scope matches this prompt's
      > work, within its parameters, recording the honored `EC` ids in
      > code/tests; if a recurring concern is missing from the map, propose it
      > (note `/forge-add-convention`).
      > Execute prompt `<ID>` in full and satisfy the **Definition of Done**
      > (`prompts/README.md` §5): implementation matches the referenced
      > requirements; critical-path tests pass for any path in `forge.config.json
      > → criticalPaths.paths` the prompt touches; the quality gates in
      > `forge.config.json → ci.commands` (`lint`/`typecheck`/`test`/`build`/
      > `docsCheck`) pass; `@requirement <id>` tags are added in code **and
      > tests**; derived docs are synced via **`/forge-sync-docs`** (or `make
      > forge-sync-docs`). Then mark `<ID>` as `done` in `prompts/state.json`
      > (fill `commit` and `updatedAt`), regenerate `prompts/STATUS.md`, and make
      > a **Conventional Commit**. If you **cannot** finish, do **not** mark it
      > `done`: leave it `in_progress`, write the reason to
      > `prompts/.logs/<ID>.note.md`, commit the partial progress, and report.
      > Return a summary of at most 8 lines: what you did, the key files, the
      > final status, and any blockers.
   d. When the subagent returns, **release the claim and verify**: if `<ID>` was
      marked `done`, **delete `prompts/claims/<ID>.json`**; if it did **not**
      complete, **leave the claim** (and the `.logs/<ID>.note.md` note) so a
      parallel worker keeps skipping it. Then run `python3
      prompts/next_prompt.py`:
      - If the **same `<ID>`** returns (it did not complete) → **stop** and show
        the reason from `prompts/.logs/<ID>.note.md`. Do **not** retry
        automatically.
      - If it advanced to another id, continue the loop (step 2).

3. **When the phase is done:** report progress (e.g. done X / total), the phase's
   prompts completed in this run, and the next eligible prompt (it will belong to
   the next phase). Suggest running `/forge-run-phase <next>` to continue.

## Notes

- Each prompt runs **isolated** in a subagent; only its summary returns → the
  orchestrator context stays lean for the whole phase.
- The subagent needs permission to `git commit`; approve it when prompted, or run
  in a suitable permission mode.
- **Stack-neutral:** every gate/test/command comes from `forge.config.json →
  ci.commands` and `criticalPaths.paths`, and the source of truth is
  `docs/requirements/`. No tool name is hardcoded here.
- **Claims convention (parallel-execution safety):** one claim file per in-flight
  prompt (`prompts/claims/<ID>.json`), written **before** delegating and removed
  **after** the prompt is `done`; on failure the claim stays put alongside the
  `.logs/<ID>.note.md` note. Each prompt gets its own file, so claims never
  conflict with each other or with `state.json`. `forge-validate` checks claims
  integrity. See [`docs/guides/teams.md`](../../docs/guides/teams.md).
- Work only on the target phase's prompts; never remove `docs/requirements/` or
  `prompts/`.
