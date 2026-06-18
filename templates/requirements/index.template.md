<!--
  Forge — requirements index template (equivalent of a project's "00 index").
  Genesis copies this to docs/requirements/index.md and lists the documents that
  the chosen tier actually instantiated. Replace every {{PLACEHOLDER}}; delete
  these guidance comments once filled.
-->

# {{PROJECT_NAME}} — Requirements (source of truth)

> **Purpose:** the index of this project's source of truth. Everything built
> traces back to a document here. **This folder is the single source of truth;
> code follows it, never the reverse.**

- **Project:** {{PROJECT_NAME}}
- **One-line purpose:** {{PROJECT_PURPOSE}}
- **Requirement tier:** {{TIER}} <!-- lean | standard | full; mirrors forge.config.json -->
- **Docs language:** {{DOCS_LANGUAGE}} <!-- from forge.config.json -->

---

## Source of truth before code

This folder is written **before** implementation. Agents and contributors
**never invent requirements**: if something needed to build a feature is not
here, the work stops and the gap is recorded here first — it is not filled in by
guesswork. Code links back to these documents through `@requirement` tags, and
the [traceability matrix](traceability.md) is generated from those tags.

---

## Documents in this project

<!--
  List ONLY the documents the chosen tier instantiated. Remove rows that do not
  apply. (lean: vision, functional, decisions, roadmap, conventions. standard:
  + non-functional, data-model, business-rules, traceability. full: + use-cases,
  interface, compliance, architecture, modularity, standards.)
-->

| Document                                  | Tier      | Contents                                                        |
| ----------------------------------------- | --------- | --------------------------------------------------------------- |
| [vision.md](vision.md)                    | lean      | Problem, scope, objectives, user profiles, assumptions, glossary. |
| [functional.md](functional.md)            | lean      | Functional requirements (`FR`), grouped by area, with flows.    |
| [decisions.md](decisions.md)              | lean      | Architecture Decision Records (`ADR`), incl. the Stack ADR.     |
| [roadmap.md](roadmap.md)                  | lean      | Phased plan and milestones.                                     |
| [conventions.md](conventions.md)          | all tiers | Conventions Map: cross-cutting engineering/UX defaults (`EC`).  |
| [non-functional.md](non-functional.md)    | standard  | Non-functional requirements (`NFR`) and critical paths.         |
| [data-model.md](data-model.md)            | standard  | Entities (`EN`), attributes, relationships, data dictionary.    |
| [business-rules.md](business-rules.md)    | standard  | Business rules (`BR`) and critical paths.                       |
| [traceability.md](traceability.md)        | standard  | **Generated** matrix: requirement → source → code → tests.      |
| [use-cases.md](use-cases.md)              | full      | Use cases (`UC`): pre-conditions, main/alternate/exception flows. |
| [interface.md](interface.md)              | full      | Screens, navigation, brand and design-system pointers.          |
| [compliance.md](compliance.md)            | full      | Compliance requirements (`CR`) per regime.                      |
| [architecture.md](architecture.md)        | full      | Technical architecture and external integrations.               |
| [modularity.md](modularity.md)            | full      | Shared core × modules, boundaries, extensibility.               |
| [standards.md](standards.md)              | full      | Code & process standards, testing, CI/CD, versioning.           |

---

## ID taxonomy (the conventions)

Every requirement item carries a **stable, prefixed identifier** so it can be
referenced from other documents, from the traceability matrix, and from
`@requirement` tags in code and tests. Prefixes are **language-neutral English
codes** (a project may localize the surrounding labels, but the codes stay as
below).

| Prefix  | Meaning                      | Lives in            | Example   |
| ------- | ---------------------------- | ------------------- | --------- |
| **FR**  | Functional Requirement       | `functional.md`     | `FR01`    |
| **NFR** | Non-Functional Requirement   | `non-functional.md` | `NFR01`   |
| **BR**  | Business Rule                | `business-rules.md` | `BR01`    |
| **CR**  | Compliance Requirement       | `compliance.md`     | `CR01`    |
| **UC**  | Use Case                     | `use-cases.md`      | `UC01`    |
| **EN**  | Entity (data)                | `data-model.md`     | `EN01`    |
| **EC**  | Engineering Convention       | `conventions.md`    | `EC-01`   |
| **ADR** | Architecture Decision Record | `decisions.md`      | `ADR-001` |

> **`EC` vs `NFR` vs standards.** An **`EC`** is an *applied, cross-cutting
> default* a feature must honor when its **Applies to** scope matches (e.g.
> "paginate any unbounded list") — checked per change by the
> [reviewer](../../.claude/agents/reviewer.md). An **`NFR`** is a *project-wide
> quality target* ("respond in ≤ 2 s"). **`standards.md`** is *code style and
> process* (naming, commits, CI). The three do not overlap: `EC` is the behavior
> every feature inherits, `NFR` is the bar the whole system meets, standards are
> how the code is written.

**Conventions:**

- IDs are zero-padded and **never renumbered** once published; retire an item by
  marking it obsolete, do not reuse its number.
- Sub-items use a dotted suffix: `FR01.1`, `FR01.2`.
- `ADR` uses a three-digit form (`ADR-001`) and the dedicated
  [ADR template](../adr.template.md).
- Reference an ID inline by its code (e.g. "satisfies `FR01`, enforces `BR03`").
- Tag implementing code and tests with `@requirement FR01` (and
  `@businessRule BR03` / `@requirement CR02` where applicable) so the
  [traceability matrix](traceability.md) can be generated.
- An **`EC`** entry lives in [`conventions.md`](conventions.md) and may be tagged
  on honoring code/tests with `@convention EC-01` for lightweight traceability;
  its primary enforcement is the [reviewer](../../.claude/agents/reviewer.md),
  not the matrix.
