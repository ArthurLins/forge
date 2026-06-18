<!--
  Golden example — the SELF-CONTAINED PROMPT link (illustrative).
  A filled instance of templates/prompt.template.md for the Notes feature. This
  is link #2 of the loop. Domain-neutral; stack-light. In a real project this
  file lives under prompts/phase-<n>-<slug>/ and is tracked in state.json.
-->

# [P1.1] — Notes: create & list

> A self-contained Forge prompt, filled from `templates/prompt.template.md`. An
> agent can execute it cold, from this file and the referenced docs alone.

---

## Metadata

- **ID:** P1.1
- **Phase:** 1 — Notes
- **Depends on:** none
- **Reference docs (read before starting):**
  - `docs/requirements/index.md`
  - the requirement entry: [`requirement.md`](requirement.md) (`FR01`, `BR01`)
- **Requirements covered:** `FR01`, `BR01`
- **Expected outputs / artifacts:** a `createNote` operation and a `listNotes`
  operation, plus a critical-path test for `BR01`.

---

## Agent role

You are an autonomous build agent on this repository. **Read the reference docs
above before any action.** The source of truth is `docs/requirements/`; do not
invent requirements. Honor the project's stack and conventions as declared in
`forge.config.json` — do not hardcode tools the project did not choose. (In this
illustrative example the code is stack-light pseudocode.)

## Context (self-sufficient)

The project needs a minimal **Notes** feature. A note has a **title** (required,
non-empty) and an optional **body**. `FR01` defines create + list; `BR01` is the
invariant that the title must be non-empty, and it is a **critical path** — so it
ships with a test. List order is most-recent-first (`FR01.2`).

## Objective

Implement `createNote` (rejecting an empty title) and `listNotes` (most recent
first), with a passing critical-path test for `BR01`.

## Preconditions

- The requirement entry exists (`FR01`, `BR01`).
- No prior prompt is required (`Depends on: none`).

## Tasks

1. Add a pure `validateTitle` helper that enforces `BR01` (non-empty title).
2. Implement `createNote`: validate, assign an id, persist, return the note.
3. Implement `listNotes`: return the user's notes, most recent first (`FR01.2`).
4. Tag the implementation with `@requirement FR01` and `@rule BR01`.
5. Write a critical-path test covering `BR01` (reject empty title) **and** the
   happy path (accept a valid title); tag it the same way.

## Acceptance criteria

- [ ] `createNote` rejects an empty/whitespace title and accepts a valid one.
- [ ] `listNotes` returns notes most recent first.
- [ ] Code **and** test carry `@requirement FR01` / `@rule BR01`.
- [ ] The critical-path test passes.

## State & docs update (required)

1. Add `@requirement FR01` / `@rule BR01` tags in the code **and** test.
2. Run `/forge-sync-docs` so the traceability matrix and `STATUS.md` regenerate.
3. Update `prompts/state.json` (`status` → `done`, `commit`, `updatedAt`) and
   regenerate `prompts/STATUS.md`.
4. Create a **Conventional Commit** (e.g. `feat(notes): create & list notes`).

## Verification

- Run the project's quality gates from `forge.config.json → ci.commands`
  (`lint` / `typecheck` / `test` / `build`) — all green.
- Confirm the traceability matrix now shows `FR01` (and the `BR01` rule) as
  `covered` (code + test). See [`traceability-row.md`](traceability-row.md).
- Confirm **CI is green** and the **Definition of Done** is met
  (`prompts/README.md` §5).
