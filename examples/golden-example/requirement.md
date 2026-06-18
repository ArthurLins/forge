<!--
  Golden example — the SOURCE-OF-TRUTH link (illustrative).
  In a real project these entries live in docs/requirements/functional.md and
  docs/requirements/business-rules.md. They are inlined here so the example reads
  standalone. Domain-neutral ("Notes"); stack-light. This is link #1 of the loop.
-->

# Golden example — requirement (Notes)

> Written **before** any code (Forge Principle 1). The code in
> [`code/`](code/) and the test trace back to the IDs below; nothing is invented.

## Functional requirement

### FR01 — Manage notes

**Objective:** let an authorized user create and list short notes.

**Flow**

1. The user opens their note list.
2. The user creates a new note with a title and optional body.
3. The system assigns a unique identifier and saves it.
4. The user can list their notes, most recent first.

**Requirements**

- FR01.1 — Create a note with a **required, non-empty title**; reject an empty
  title. **[Must]**
- FR01.2 — List the current user's notes, most recent first. **[Must]**

> Tag implementing code and tests with `@requirement FR01`.

## Business rule (with a critical path)

| ID       | Rule                                                              | Related |
| -------- | ---------------------------------------------------------------- | ------- |
| **BR01** | A note must have a non-empty title; creation is rejected otherwise. | FR01    |

### Critical rules / paths

`BR01` is flagged **critical**: creating a note is the feature's core write, and
silently accepting an empty title would corrupt the list. So it **must** be
covered by a test (the Definition of Done gates this). In a real project this row
is kept in sync with `forge.config.json → criticalPaths.paths`.

| Critical rule (BR) | Why it is critical                                  | Covered by (test ref)                   |
| ------------------ | --------------------------------------------------- | --------------------------------------- |
| **BR01**           | The core write; an empty title would corrupt the list. | `code/create-note.spec.pseudo` (BR01 case) |

> Tag enforcing code and its test with `@rule BR01` (alias `@businessRule BR01`).
