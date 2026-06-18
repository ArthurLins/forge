---
description: Scaffold a new module in a MODULAR Forge-built project — PLUGGABLE. If forge.config.json declares a generators.module command, run it; otherwise emit a stack-agnostic module scaffolding CHECKLIST (boundary, registration, requirement doc, tracking, first feature). Only relevant when the project declares modules; never assumes a stack.
argument-hint: '<module-name>  (kebab-case)'
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-new-module` — scaffold a module (pluggable)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Create a
new **module** the way this project is built — by running the project's declared
module generator when there is one, and otherwise by laying down a **stack-agnostic
checklist**. The source of truth is `docs/requirements/`; **never invent
requirements**.

Like `/forge-new-feature`, this command is **pluggable**: Forge imposes no
generator and assumes no stack. It only applies to **modular** projects.

> **Applicability.** This command is meaningful only when the project is modular —
> i.e. `docs/requirements/modularity.md` exists (declared by a `full`-tier genesis
> or added later). If the project is **not** modular, stop and tell the developer
> there are no modules to scaffold; a flat project uses `/forge-new-feature`.

**Inputs:** `$ARGUMENTS` — the **module name** in `conventions.fileCasing`
(default `kebab-case`).

## Step 0 — Read the profile and the boundaries

1. Read `forge.config.json`:
   - **`generators.module`** — the project's module-scaffold command, if any. Its
     presence decides the path.
   - `stack.*`, `conventions.*`, `traceability.*`, `ci.commands.*`.
2. Read `docs/requirements/modularity.md` — the shared-core × modules split, the
   **boundary rules** (what a module may depend on; that modules do not depend on
   each other unless explicitly allowed), and the central registry/extension
   mechanism the project uses.

## Path A — A generator IS declared (`generators.module` present)

Run the declared command, substituting the module name:

```bash
# The actual command comes from forge.config.json, NOT from here:
#   generators.module = "<the project's module-scaffold command> {{name}}"
<resolved generators.module command>
```

Then finish on-standard, per `modularity.md`:

1. **Register** the module in the project's central registry / composition points
   and set its declared boundary tags so the boundary lint (if any) passes.
2. **Requirement doc** — instantiate/fill the module's requirement document under
   `docs/requirements/` (no unresolved placeholders).
3. **Tracking** — add the module's entry/phase to `prompts/state.json` if the
   project tracks modules there.
4. **First feature** — create the module's first feature with `/forge-new-feature`.
5. **Sync docs** (`/forge-sync-docs`), run the configured `ci.commands.*`, satisfy
   the **Definition of Done**, and make a **Conventional Commit** (e.g.
   `feat(<module>): scaffold module`).

## Path B — NO generator declared (the fallback CHECKLIST)

Default; must work with **no stack present**. Do **not** assume any tool. Produce
a concrete, **stack-agnostic checklist** for `<module-name>`, derived from
`docs/requirements/modularity.md` and the framework's domain-neutral golden
example (`docs/guides/`, F8):

```
Module scaffolding checklist — <module-name>  (no generator declared)

1. Boundary & placement
   [ ] Create the module's workspace location per docs/requirements/modularity.md.
   [ ] Set its boundary so it depends only on what the doc allows (shared core /
       shared libs), and not on other modules.

2. Registration
   [ ] Register the module in the central registry / composition points the
       project uses (so it is discovered and wired in).

3. Requirement doc
   [ ] Add the module's requirement document under docs/requirements/ and fill it
       (no unresolved placeholders). Use the project's ID taxonomy.

4. Tracking
   [ ] Add the module's entry/phase to prompts/state.json if the project tracks
       modules there; regenerate STATUS via /forge-sync-docs.

5. First feature
   [ ] Create the module's first feature with /forge-new-feature (which itself
       falls back to a checklist when no generators.feature is declared).

6. Gates & commit
   [ ] Sync docs (/forge-sync-docs); run ci.commands.* (lint/typecheck/test/build/
       docsCheck) — all green.
   [ ] Conventional Commit, e.g. feat(<module>): scaffold module.
```

## How the generator is declared (for project authors)

Declare it in `forge.config.json` under `generators.module` (set during
`/forge-init` or added later):

```json
"generators": {
  "feature": "<feature-scaffold command, with {{name}}/{{target}} placeholders>",
  "module":  "<module-scaffold command, with {{name}} placeholder>"
}
```

When `generators.module` is **absent or empty**, this command uses **Path B**
(the checklist).

## Notes

- **Pluggable & stack-neutral:** the generator command, boundaries, casing, gates
  and tag keywords come from `forge.config.json` and `docs/requirements/`. No
  stack assumed; the fallback is a checklist.
- **Modular-only & requirement-first:** only for projects with
  `modularity.md`; back every module with its requirement document.
- Never remove `docs/requirements/` or `prompts/`; never invent requirements.
