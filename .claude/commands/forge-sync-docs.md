---
description: Synchronize a Forge project's derived documentation — run the sync-docs orchestrator (core generators: STATUS, traceability matrix, changelog) plus any stack hooks declared in forge.config.json, then summarize the documentation diff. Generated artifacts are never hand-edited.
allowed-tools: Task, Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-sync-docs` — regenerate the derived documentation

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project.
Regenerate the **derived** docs so generated artifacts and `prompts/STATUS.md`
match the source, then summarize the diff. The **sources of truth** stay
`docs/requirements/` (requirements) and `prompts/state.json` (tracking) — this
command only **derives** artifacts.

This command upholds **Principle 6 — "Derived docs are code"**
([`FORGE.md`](../FORGE.md)): STATUS, the traceability matrix, the changelog, and
any declared stack artifacts are **generated** (never edited) and the CI
docs-freshness gate fails if they are stale.

## How it runs

Forge ships a runtime-agnostic orchestrator (Python 3, the same runtime the
prompt engine already uses — no project stack needed for the core):

```bash
make forge-sync-docs        # core generators + any declared stack hooks
# equivalently, no install step:
PYTHONPATH=tools python3 -m forge_tools sync-docs
# core text artifacts only (skip stack hooks):
make forge-docs-gen         # = sync-docs --core-only
```

`make forge-sync-docs` runs, idempotently, in one pass:

1. **STATUS** — `prompts/STATUS.md` from `prompts/state.json`.
2. **Traceability matrix** — `<docs.generatedDir>/traceability.md` from the
   `@requirement`/`@rule` tags (scanned per `traceability.globs` /
   `traceability.tagAliases`), cross-checked against `docs/requirements/`.
3. **Changelog** — `<docs.generatedDir>/CHANGELOG.md` from the Conventional
   Commits / SemVer tags in git history.
4. **Declared stack hooks** — each `forge.config.json → docsHooks[]` entry runs
   **after** the core (e.g. build an API contract, regenerate a typed client into
   `docs.generatedDir`). With `docsHooks: []` (the default) only the core runs and
   the sync still succeeds — Forge assumes **no stack**.

## Procedure

1. **Read the profile** — `forge.config.json` for `docs.generatedDir`,
   `docsHooks`, and `ci.commands.docsCheck` (the freshness gate). Do not hardcode
   any stack step; only the declared hooks run.

2. **Run the sync.** For a simple regeneration, run `make forge-sync-docs`
   directly. For a heavier sync (e.g. several declared hooks, or to keep this
   thread's context lean), **delegate to the `docs-sync` subagent** (the `Task`
   tool, subagent type `docs-sync`) with this instruction:

   > You are the **docs-sync** subagent in a Forge-built repository, with a
   > **clean context**. Read `forge.config.json` for `docs.generatedDir`,
   > `docsHooks`, and the docs-freshness gate. Run `make forge-sync-docs` (or
   > `PYTHONPATH=tools python3 -m forge_tools sync-docs`) to regenerate
   > `prompts/STATUS.md`, the traceability matrix, the changelog, and any declared
   > stack hooks — **idempotently**, deriving only from the source of truth; never
   > hand-edit a generated artifact and never invent requirements. Then confirm
   > freshness with `make forge-sync-docs-check`. Return: the regenerated
   > artifacts, the documentation diff (`git status` / `git diff --stat` of the
   > generated paths), and any inconsistency (e.g. a traceability gap, a `done`
   > prompt missing a `commit`).

3. **Confirm freshness** — `make forge-sync-docs-check` (the `ci.commands.docsCheck`
   gate) must report **no drift**.

4. **Summarize the diff** — show `git status` / `git diff --stat` limited to
   `prompts/STATUS.md`, `docs.generatedDir`, and any hook output. Note any
   traceability **gap** surfaced (a requirement with no code/test, or a tag at an
   undeclared ID). Suggest committing the artifacts (`docs: sync derived
   artifacts`, per the project's commit style) or folding them into the feature
   commit.

## Notes

- **Idempotent:** a second run reports "nothing to update".
- **Stack-neutral:** the core generators run with no project stack installed;
  stack-specific docs are **only** the declared `docsHooks`. Nothing is hardcoded.
- **Never hand-edit** generated artifacts; edit the source (requirements,
  `state.json`, commits, code tags) and regenerate.
- Never remove `docs/requirements/` or `prompts/`; never invent requirements.
