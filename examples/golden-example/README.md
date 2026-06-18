# Golden example — the end-to-end loop (illustrative)

> **What this is.** One small, **domain-neutral** feature shown end to end, so an
> adopter can see the complete Forge loop on a generic example before applying it
> to their own project. It is **illustrative only** — the code is deliberately
> **stack-light pseudocode** (no real language, framework, or datastore), and the
> domain is a plain **"Notes"** item. Mirror its *shape*, not its syntax.
>
> A real project realizes this shape in its own stack (from
> [`forge.config.json`](../../forge.config.json)) and its own source of truth
> (`docs/requirements/`). Here, the "requirements" and "config" are inlined into
> the example files so it reads standalone.

## The chosen feature

**Notes — create & list.** An authorized user creates a note (with a non-empty
title) and lists their notes. It is small but exercises **every** transversal
decision Forge cares about in a single flow:

- a **requirement** with a stable ID and one **critical business rule**;
- a **self-contained prompt** that drives the build;
- **code tagged with `@requirement`** linking implementation back to the requirement;
- a **critical-path test** for the rule;
- the resulting **traceability row** (requirement → code → test).

## The loop, file by file

Read these in order — they are the five links of the chain Forge enforces.

| #   | Link in the loop                | File                                                  | Forge principle |
| --- | ------------------------------- | ----------------------------------------------------- | --------------- |
| 1   | **Requirement** (source of truth) | [`requirement.md`](requirement.md)                  | 1 (source of truth before code) |
| 2   | **Prompt** (self-contained unit)  | [`prompt-instance.md`](prompt-instance.md)          | 3 (self-contained prompts) |
| 3   | **Code** (with `@requirement` tags) | [`code/create-note.pseudo`](code/create-note.pseudo) | 7 (traceability) |
| 4   | **Test** (the critical path)      | [`code/create-note.spec.pseudo`](code/create-note.spec.pseudo) | DoD critical-path test |
| 5   | **Traceability row** (generated)  | [`traceability-row.md`](traceability-row.md)        | 6 + 7 |

## Why each link matters (the checklist to copy)

1. **Requirement first.** `FR01` and rule `BR01` are written **before** any code.
   The code traces back to them; nothing is invented (Principle 1).
2. **One self-contained prompt.** `prompt-instance.md` carries everything an
   agent needs to build the feature cold — objective, reference docs, tasks,
   acceptance criteria, verification — with no reliance on conversation memory
   (Principle 3).
3. **Domain logic is pure and testable.** The rule "a note must have a non-empty
   title" (`BR01`) lives in a small pure function, trivial to test, independent of
   any I/O or framework.
4. **Code carries `@requirement` / `@rule` tags.** The implementation tags the
   requirement (`@requirement FR01`) and the rule (`@rule BR01`); so does the
   test. That is what the traceability matrix is generated from (Principle 7).
5. **The critical path has a test.** `BR01` is the project's declared critical
   path, so `create-note.spec.pseudo` exercises both the accept and reject cases.
   The Definition of Done gates exactly this.
6. **The matrix is derived, not written.** `traceability-row.md` is what the
   traceability tool *emits* for this feature from the tags above — committed and
   CI-checked, never hand-maintained (Principle 6).

## How to reuse it

When you build a real feature, replicate the **five links**:

1. Write the requirement (and any critical rule) in `docs/requirements/` — or use
   `/forge-add-requirement`.
2. Plan a prompt for it with `/forge-plan-phase` (it uses
   `templates/prompt.template.md`).
3. Implement it in your stack, tagging code with `@requirement <ID>` (and
   `@rule <ID>` for a business rule).
4. Write the critical-path test (also tagged).
5. Run `/forge-sync-docs` so the traceability matrix and `STATUS.md` regenerate.

Scaffold the skeleton with `/forge-new-feature <name>` (it runs the project's
declared generator, or falls back to a stack-agnostic checklist derived from this
example).
