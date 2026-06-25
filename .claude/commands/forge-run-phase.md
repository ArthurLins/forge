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
      `{ "promptId": "<ID>", "owner": "<you/agent>", "claimedAt": "<ISO-8601 now>",
      "heartbeatAt": "<ISO-8601 now>" }`. Include the initial `heartbeatAt`;
      `prompts/next_prompt.py` skips any live-claimed prompt, so the other worker
      selects the next free one (or reports `BLOCKED`/`DONE`). If you are
      re-claiming a prompt whose previous claim **expired** (its `heartbeatAt`
      went stale beyond `claims.ttlSeconds`, default 1800s), carry forward the
      prior `attempts` value.

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
      While the subagent runs, **refresh `heartbeatAt`** on the claim
      periodically (~every 300s / on each significant step) so a live worker keeps
      the claim from expiring; if you crash, the heartbeat goes stale and the
      selector auto-releases the prompt after the TTL.
   d. When the subagent returns, **release the claim and verify**: if `<ID>` was
      marked `done`, **delete `prompts/claims/<ID>.json`**; if it did **not**
      complete, **leave the claim** (and the `.logs/<ID>.note.md` note) and
      **increment `attempts`** in the claim (carrying any prior value), so a
      parallel worker keeps skipping it — after `claims.maxAttempts` (default 3)
      failures, set the prompt's `status` to `blocked` in `prompts/state.json`.
      Then run `python3 prompts/next_prompt.py`:
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
- **Parallelism — WIP limit + impact-aware picking.** When running a phase's
  prompts in parallel, hold at most `claims.maxConcurrent` (see
  `forge.config.schema.md` → `claims`) in-flight claims at once — the **WIP
  limit**; absent / `0` = unlimited. Before claiming a new prompt, count the
  ACTIVE claims in `prompts/claims/` and wait if you are at the cap. To choose
  *which* eligible prompt to start, run `python3 prompts/next_prompt.py
  --by-impact`: it returns, among the same eligible set, the prompt that unblocks
  the most still-pending work. Rationale: bounded WIP keeps queues short and
  feedback fast, and picking high-impact work first widens the dependency
  frontier. The flag is optional and changes nothing in serial mode.
- The subagent needs permission to `git commit`; approve it when prompted, or run
  in a suitable permission mode.
- **Stack-neutral:** every gate/test/command comes from `forge.config.json →
  ci.commands` and `criticalPaths.paths`, and the source of truth is
  `docs/requirements/`. No tool name is hardcoded here.
- **Claims convention (parallel-execution safety + self-healing):** one claim
  file per in-flight prompt (`prompts/claims/<ID>.json`), written with
  `claimedAt` AND an initial `heartbeatAt` **before** delegating, `heartbeatAt`
  refreshed while it runs, and removed **after** the prompt is `done`. On failure
  the claim stays put alongside the `.logs/<ID>.note.md` note with `attempts`
  incremented; after `maxAttempts` (default 3) the prompt is set to `blocked`. A
  crashed worker stops refreshing, so after the TTL (`claims.ttlSeconds`, default
  1800s) the selector ignores the stale claim and the prompt is eligible again —
  **no manual deletion needed**. A legacy claim with no `heartbeatAt` is never
  auto-released. Each prompt gets its own file, so claims never conflict with each
  other or with `state.json`. `forge-validate` checks claims integrity (and warns
  on expired/over-attempt claims). See
  [`docs/guides/teams.md`](../../docs/guides/teams.md).
- Work only on the target phase's prompts; never remove `docs/requirements/` or
  `prompts/`.
