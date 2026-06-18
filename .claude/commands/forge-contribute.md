---
description: Improve the Forge framework ITSELF — a new or changed skill, command, catalog entry, template, tool, generator, or doc. The meta-circular contributor entry point: scope the change against the constitution (FORGE.md), record it in self/, apply the minimal edit, GATE it with forge-selfcheck, then land it (direct commit for the maintainer, or a draft PR for a contributor) and archive it. SELF-ONLY — for maintaining Forge, not for building an adopter's project (use /forge-add-requirement, /forge-plan-phase, etc. for that). Forge is self-hosting.
argument-hint: '[--pr]  (--pr or a non-maintainer actor ⇒ draft PR instead of a direct commit)'
allowed-tools: Task, Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-contribute` — improve Forge itself (meta-circular)

You are an agent (Claude, Opus 4.8) at the root of the **Forge framework
repository** (not an adopter's project). This is how Forge **maintains itself**:
a change to a skill, command, catalog entry, template, tool, generator, or doc is
scoped against the constitution, applied minimally, **gated by `forge-selfcheck`**,
and landed. Forge is **self-hosting** — improving Forge *with* Forge means an
update is, by construction, already applied *to* Forge.

> **This is SELF-ONLY.** Use it only to change the framework itself. To add a
> requirement or plan a phase **in an adopter's project**, use
> `/forge-add-requirement`, `/forge-plan-phase`, `/forge-run`, etc. instead. This
> command and its workspace (`self/`) are excluded from the adopter export
> (`forge.manifest.json → selfOnly`); `forge-selfcheck` exempts it from the
> adopter skills-catalog parity check.

**Landing mode:** `$ARGUMENTS`. Default is **maintainer/solo** → a **direct
commit** to `main`. Pass **`--pr`** (or when the actor is **not the maintainer**)
→ open a **draft PR** and do **not** commit to `main`.

## Hard rules (never broken)

1. **Never land a change that fails `forge-selfcheck`.** The gate is mandatory in
   every mode; fix or revert a red change — never land it.
2. **Never violate the constitution** (`FORGE.md`, the eight principles +
   stack-neutral / domain-agnostic / English / derived-docs-as-code /
   traceability). If a change would, refuse and adjust.
3. **Require explicit human confirmation before applying** (a hard stop after the
   proposal).
4. **Keep the change minimal.** No drive-by refactors; smallest safe edit.
5. **Never pollute the root seeds** — root `prompts/state.json` stays the empty
   seed and `docs/requirements/` stays only `.gitkeep`. Forge's own working state
   lives in `self/`.

## Lifecycle (lean — proposal → apply → archive)

### 1. Scope & propose

- Understand the requested change in the developer's words.
- Read the **constitution** [`FORGE.md`](../../FORGE.md) and Forge's own source of
  truth under [`self/requirements/`](../../self/requirements/) (`index.md`,
  `functional.md` for the `FR-S*` capabilities, `decisions.md` for the `ADR-S*`).
- **Classify the area:** skill/command · template · tool/generator · agent guide ·
  catalog/doc · engine · self-hosting infra.
- **Constitution check:** verify the change does **not** violate a principle —
  stack-neutral, domain-agnostic, English, source-of-truth-before-code,
  derived-docs-as-code, traceability, isolated orchestration, layered guidance. If
  it would, **refuse or adjust** and explain why.
- **Summarize the proposal** (what changes, which files, which `FR-S*`/`ADR-S*` it
  touches or adds, the constitution check result) and **STOP for explicit human
  confirmation. Do not apply anything before the developer confirms.**

### 2. Record

- Add a work item to [`self/prompts/state.json`](../../self/prompts/state.json)
  with `status: "pending"` (a new `S*` id in the appropriate phase; create a phase
  if the area warrants one). Regenerate the self STATUS:
  `FORGE_ROOT=$(pwd)/self PYTHONPATH=tools python3 -m forge_tools status --out self/prompts/STATUS.md`.
- Start a contribution log `self/prompts/.logs/contribution-<date>.md` capturing:
  the proposal, the rationale, and the constitution check.

### 3. Apply

- Implement the **minimal** change to the framework files. For a larger change,
  delegate to an **isolated `Task` subagent** (clean context) so this thread stays
  lean.
- If the change **adds or renames a DISTRIBUTABLE skill/command**, register it in
  **both** the [`AGENTS.md`](../../AGENTS.md) catalog table **and**
  [`docs/guides/skills-catalog.md`](../../docs/guides/skills-catalog.md)
  (registration-parity is enforced by `forge-selfcheck`). A **self-only** command
  is the exception — do not add it to the adopter catalogs.
- If the change adds/changes a framework capability or decision, update
  `self/requirements/functional.md` (`FR-S*`) or `decisions.md` (`ADR-S*`).

### 4. Gate (mandatory)

- Regenerate derived docs as needed, then run the gate:

  ```bash
  make forge-selfcheck        # selfcheck (constitution invariants) + docs-freshness
  ```

  It **must PASS** (hard checks green; warnings are allowed). If it fails, **fix
  or revert** — never proceed with a red gate. Use `make forge-selfcheck-report`
  for a non-failing, human-readable view while iterating.

### 5. Land

- **Maintainer / solo (default):**
  1. Regenerate the changelog and fold it in (`make forge-changelog` /
     `make forge-sync-docs`).
  2. Stage all and create **one Conventional Commit** describing the framework
     change (e.g. `feat(forge-...): …`, `docs(forge): …`, `fix(forge-...): …`),
     ending the body with the `Co-Authored-By` trailer.
  3. **Commit directly** to `main`.
- **Contributor mode (`--pr`, or a non-maintainer actor):**
  1. Create a branch, commit the change (Conventional Commit).
  2. Open a **draft PR** with `gh pr create --draft`, including the change summary
     **and the `forge-selfcheck` result** in the PR body.
  3. Do **not** commit to `main` — the flow is proposal → approval → PR.

### 6. Archive

- Mark the work item `done` in `self/prompts/state.json` (record the `commit` when
  committing directly; for a PR, note the PR reference). Regenerate the self
  STATUS (same command as step 2).
- Finalize the contribution log: the outcome, the gate result, and the commit/PR
  reference.

## Verification

- `make forge-selfcheck` is **green** (hard checks pass; warnings, if any, are
  reviewed).
- The constitution is intact; the change is minimal; the root seeds are
  untouched (empty `prompts/state.json`, `docs/requirements/` only `.gitkeep`).
- A distributable skill/command change is registered in **both** catalogs; a
  self-only one is not in the adopter catalogs.
- The work item is `done` in `self/prompts/state.json` and the log is finalized.

## Notes

- **Meta-circular:** this command *is* Forge being used to maintain Forge.
- **selfcheck-always, PR-optional** (`ADR-S4`): the gate runs in every mode; only
  the landing differs (direct commit vs. draft PR).
- Never remove the root seeds (`prompts/state.json`, `docs/requirements/`); never
  add a stack or a domain to the framework.
