---
description: Scaffold a new feature in a Forge-built project — PLUGGABLE. If forge.config.json declares a generators.feature command, run it; otherwise emit a stack-agnostic scaffolding CHECKLIST (files to create, @requirement tags to add, critical-path tests to write, docs to sync) derived from the golden example. Never assumes a stack.
argument-hint: '<feature-name>  (kebab-case) [target area/module]'
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-new-feature` — scaffold a feature (pluggable)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Create a
new feature **the way this project is built** — by running the project's declared
feature generator when there is one, and otherwise by laying down a **stack-agnostic
checklist** the developer can fill in. The source of truth is
`docs/requirements/`; **never invent requirements**.

This command is **pluggable** (the same idea as `docsHooks` for sync): Forge
imposes **no** generator. It reads whether the project declared one and adapts —
so a feature is scaffolded with the project's own tooling when present, and
gracefully degraded to a guided checklist when not. It **never assumes** a
specific language, framework, datastore, or monorepo tool.

**Inputs:** `$ARGUMENTS` — the **feature name** in `conventions.fileCasing`
(default `kebab-case`), and optionally the **target area/module** (relevant only
if the project is modular).

## Step 0 — Read the profile and the requirements

1. Read `forge.config.json`:
   - **`generators.feature`** — the project's feature-scaffold command, if any
     (see "How the generator is declared" below). Its presence decides which path
     this command takes.
   - `stack.*`, `conventions.*` (casing/language), `criticalPaths.paths`,
     `traceability.{globs,tagAliases}`, `ci.commands.*`.
2. Read the requirement(s) this feature implements in `docs/requirements/` (the
   `FR`/`NFR`/`BR`/`CR`/`UC`/`EN` it realizes) and the generated
   `traceability.md`. **If the feature has no backing requirement, stop** and run
   `/forge-add-requirement` first — nothing is built ahead of the source of truth.
3. If the project is **modular** (`docs/requirements/modularity.md` exists), pick
   the target area/module so the feature lands inside the allowed boundary.

## Path A — A generator IS declared (`generators.feature` present)

Run the declared command, substituting the feature name (and target, if the
template uses one). The command string may contain placeholders the project
defined — commonly `{{name}}` and `{{target}}`:

```bash
# Example shape (the actual command comes from forge.config.json, NOT from here):
#   generators.feature = "<project's scaffold command> {{name}} --area {{target}}"
<resolved generators.feature command>
```

Then finish the feature on-standard:

1. **Wire it in** as the project's generator/docs expect (register the module,
   add routes/menu, replace placeholder data access, etc. — per
   `docs/requirements/` and the project's own conventions).
2. **Add `@requirement` tags** in the implementing code **and tests** (a keyword
   from `traceability.tagAliases`, default `@requirement <ID>`; `@rule <ID>` /
   `@businessRule <ID>` for a `BR`).
3. **Critical-path tests** — if the feature touches any path in
   `criticalPaths.paths`, write the test that covers it (the Definition of Done
   gates this).
4. **Sync derived docs** — run `/forge-sync-docs` (or `make forge-sync-docs`) so
   the matrix/STATUS and any declared `docsHooks` are fresh.
5. **Quality gates** — run the configured `ci.commands.*` (`lint`/`typecheck`/
   `test`/`build`/`docsCheck`); all must pass.
6. **Definition of Done** (`prompts/README.md` §5) + a **Conventional Commit**
   (e.g. `feat(<area>): add <feature> feature`).

## Path B — NO generator declared (the fallback CHECKLIST)

This is the default and must always work with **no stack present**. Do **not**
assume any specific language, framework, datastore, or monorepo tool. Produce a
concrete, **stack-agnostic checklist** for `<feature-name>`, modeled on the
framework's domain-neutral **golden example**
(`docs/guides/` golden example, built in F8 — read it for the canonical
end-to-end shape) and the project's own conventions. Present it as actionable
items the developer fills with their stack:

```
Feature scaffolding checklist — <feature-name>  (no generator declared)

1. Requirement backing
   [ ] The feature realizes a declared requirement in docs/requirements/
       (FR/NFR/BR/CR/UC/EN). If not, run /forge-add-requirement first.

2. Code (create, following conventions.* casing and — if modular — inside the
   target module's boundary in docs/requirements/modularity.md)
   [ ] An entry point / interface for the feature (the unit a caller invokes).
   [ ] The core logic / service that implements the requirement's flow.
   [ ] Data access (or its placeholder) for any entity the feature reads/writes.
   [ ] Input validation and an explicit mapping between external and internal
       shapes (no leaking of internal models).
   [ ] Registration/wiring so the feature is reachable (route/handler/menu/export
       — whatever this stack uses).

3. Traceability tags
   [ ] Tag the implementing code with @requirement <ID> (and @rule <ID> for a BR),
       using a keyword from forge.config.json → traceability.tagAliases.

4. Tests
   [ ] A test for the feature's main behavior, tagged with the same @requirement <ID>.
   [ ] If the feature touches a path in forge.config.json → criticalPaths.paths,
       a passing critical-path test for it (required by the Definition of Done).

5. Docs
   [ ] Run /forge-sync-docs so the traceability matrix, STATUS, changelog and any
       declared docsHooks are regenerated; confirm the <ID> moves from gap to
       covered.

6. Gates & commit
   [ ] Run the configured ci.commands.* (lint/typecheck/test/build/docsCheck) —
       all green.
   [ ] Conventional Commit, e.g. feat(<area>): add <feature> feature.
```

Fill the bracketed `<…>` from the actual requirement and the project's stack, and
walk the developer through each item.

## How the generator is declared (for project authors)

Forge does **not** ship a generator. A project that has scaffolding tooling
declares it in `forge.config.json` under a `generators` object (set during
`/forge-init` or added later), e.g.:

```json
"generators": {
  "feature": "<the project's feature-scaffold command, with {{name}}/{{target}} placeholders>",
  "module":  "<the project's module-scaffold command, with {{name}} placeholder>"
}
```

When `generators.feature` is **absent or empty**, this command uses **Path B**
(the checklist) — which is the stack-neutral default and always succeeds.

## Notes

- **Pluggable & stack-neutral:** the generator command, casing, gate commands,
  critical paths and tag keywords all come from `forge.config.json`. No stack is
  assumed; the no-generator fallback is a checklist, never an assumed toolchain.
- **Requirement-first:** never scaffold a feature without a backing requirement —
  run `/forge-add-requirement` first if needed.
- The companion `/forge-new-module` follows the same pluggable pattern for whole
  modules (only relevant to modular projects).
- Never remove `docs/requirements/` or `prompts/`; never invent requirements.
