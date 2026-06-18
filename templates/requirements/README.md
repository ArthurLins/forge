# Forge — requirement templates (tiered source of truth)

> These templates are how Forge scaffolds a project's **single source of truth**,
> `docs/requirements/`. The genesis interview (`/forge-init`) picks a **tier**
> sized to the project, then instantiates the matching `*.template.md` files into
> `docs/requirements/` (dropping the `.template` suffix). The chosen tier is
> recorded in [`forge.config.json`](../../forge.config.json) under
> `requirementTiers.selected`.

Requirements are written **before** code (Principle 1 in [`FORGE.md`](../../FORGE.md)).
Nothing is invented; if something needed is missing, the gap is recorded here
first.

---

## The three tiers

Tiers are **cumulative**: each larger tier is the smaller one plus more
documents. Genesis instantiates exactly the documents listed for the chosen
tier; the [`index.template.md`](index.template.md) lists whatever ended up
present.

### `lean` — small projects / prototypes

The smallest spec that still keeps code traceable to intent.

| Document                                       | Holds                                              |
| ---------------------------------------------- | -------------------------------------------------- |
| [`vision.template.md`](vision.template.md)     | Problem, scope, users, glossary.                   |
| [`functional.template.md`](functional.template.md) | Functional requirements (`FR`).                |
| [`decisions.template.md`](decisions.template.md) | Architecture Decision Records (`ADR`), incl. the **Stack ADR**. |
| [`roadmap.template.md`](roadmap.template.md)   | Phased plan / milestones.                          |

### `standard` — most production projects

`lean` **plus**:

| Document                                            | Holds                                          |
| --------------------------------------------------- | ---------------------------------------------- |
| [`non-functional.template.md`](non-functional.template.md) | Non-functional requirements (`NFR`) + critical paths. |
| [`data-model.template.md`](data-model.template.md)  | Entities (`EN`), attributes, relationships.    |
| [`business-rules.template.md`](business-rules.template.md) | Business rules (`BR`) + critical paths.  |
| [`traceability.template.md`](traceability.template.md) | **Generated** matrix (requirement → code → test). |

### `full` — large / regulated / multi-area projects

`standard` **plus**:

| Document                                            | Holds                                          |
| --------------------------------------------------- | ---------------------------------------------- |
| [`use-cases.template.md`](use-cases.template.md)    | Use cases (`UC`) with flows.                   |
| [`interface.template.md`](interface.template.md)    | Screens, navigation, design-system pointers.   |
| [`compliance.template.md`](compliance.template.md)  | Compliance requirements (`CR`) per regime.     |
| [`architecture.template.md`](architecture.template.md) | Technical architecture and integrations.    |
| [`modularity.template.md`](modularity.template.md)  | Shared core × modules, boundaries, extension.  |
| [`standards.template.md`](standards.template.md)    | Code & process standards, testing, CI/CD.      |

---

## Rule of thumb for choosing a tier

Pick the **smallest tier you can defend**, then let it grow — genesis can move a
project up a tier later by instantiating the additional templates.

| Pick…        | When…                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| **lean**     | One area, a few contributors, no compliance regime, short horizon. You mainly need to know *what* to build and *why* a few key decisions were made. |
| **standard** | A product you intend to operate and maintain: it has quality targets, a data model worth writing down, and rules that must hold. Most projects land here. |
| **full**     | Large surface, multiple areas/modules, regulated domain (compliance regimes), or a team that needs use cases, interface specs, and explicit standards to coordinate. |

> Drivers that push **up** a tier: more than one major area/module; a data model
> with real invariants; any compliance regime in `forge.config.json`; named
> critical paths that must be tested; a team large enough that conventions must
> be written down rather than shared verbally.

---

## How to use a template

1. Genesis copies `templates/requirements/<name>.template.md` to
   `docs/requirements/<name>.md` (suffix dropped).
2. Replace every `{{PLACEHOLDER}}` with project content; delete the HTML
   guidance comments (`<!-- ... -->`) once filled.
3. Keep the **one worked stub** in each template as a model, or replace it with
   the first real item. Never leave a stub that contradicts the project.
4. Use the **ID taxonomy** consistently (defined once in
   [`index.template.md`](index.template.md)): `FR`, `NFR`, `BR`, `CR`, `UC`,
   `EN`, `ADR`.
5. `traceability.md` is **generated** — never hand-edit it (see its template's
   banner).

All requirement content is written in the project's documentation language
(`forge.config.json` → `conventions.docsLanguage`); requirement **IDs and code
identifiers stay in English**.
