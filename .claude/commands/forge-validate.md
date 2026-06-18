---
description: Statically validate a Forge-built project's structural integrity — the prompt state machine, requirement tags, the Conventions Map, the config, and derived-doc freshness. Run before integrating a change, in CI as a required check, or whenever you want to confirm the project is intact. Read-only; reports, does not fix.
allowed-tools: Bash, Read
---

# `/forge-validate` — project integrity gate

You are an agent (Claude, Opus 4.8) at the root of a **Forge-built project**. Run
the deterministic, stack-neutral static validator and surface its verdict —
**PASS** or **FAIL** — so a structurally broken project is caught before it
merges. It is **read-only**: it points at problems, it does not fix them.

This validator reads every path and knob from
[`forge.config.json`](../../forge.config.json) (it never hardcodes a stack) and
runs on Python 3 alone. It PASSES trivially on an empty / pre-genesis project —
with no prompts and no requirements there is nothing to violate.

## Procedure

Run the integrity gate from the project root:

```bash
make forge-validate-check
```

(or, without the Makefile: `PYTHONPATH=tools python3 -m forge_tools validate --check`).

For a non-failing, human-readable report while iterating, run `make
forge-validate` (alias `make forge-validate-report`).

Then report the result line and, on FAIL, the failing check(s) and what to fix.

## What it checks

| Check | Hard? | Asserts |
| ----- | ----- | ------- |
| **state-integrity** | yes | `prompts/state.json`: prompt ids are unique; every prompt's `file` exists; every `dependsOn` id exists; the dependency graph has **no cycles**; statuses are valid (`pending`/`in_progress`/`blocked`/`done`); `python3 prompts/next_prompt.py` runs without error. |
| **requirement-tag-integrity** | yes | Every `@requirement`/`@rule` id tagged in source (globs/aliases from `forge.config.json → traceability`) is **declared** in `docs/requirements/`. A dangling tag (references an undeclared id) **fails**; a declared requirement with no implementing tag is a **warning**, not a failure. |
| **conventions-integrity** | yes (if present) | Only if `docs/requirements/conventions.md` exists: each `EC-` entry has the required fields (Category, Rule, Applies to, Status) and ids are unique. |
| **config-integrity** | yes | `forge.config.json` is valid JSON with the expected top-level keys. |
| **docs-freshness** | yes | Derived docs are not stale (reuses the `forge-sync-docs --check` logic). |

Warnings never fail the gate; `--check` exits non-zero **only** on a hard
failure.

## When to use it

- **Before integrating** a prompt's work, alongside `/forge-review`.
- **In CI** as a **required status check** — enable strict structural-validation
  CI at `/forge-init` (sets `ci.strictValidation: true` and installs
  `templates/ci/forge-validate.yml.template`), or turn on the optional `validate`
  job in the combined `forge-ci.yml`.
- **Any time** you want to confirm the project is statically intact after editing
  `prompts/state.json`, requirement docs, or the config by hand.

## Notes

- **Read-only & deterministic:** it never edits code; the same project state
  yields the same verdict.
- **Stack-neutral:** every glob, tag alias, generated-docs path and config key it
  uses comes from `forge.config.json`. No tool or domain is hardcoded.
- To fix a FAIL, edit the source (the state machine, the tags, the Conventions
  Map, the config) — or run `make forge-sync-docs` for a docs-freshness failure —
  then re-run the gate.
