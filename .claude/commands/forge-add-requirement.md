---
description: Guided add/change of a requirement (FR/NFR/BR/CR/UC/EN) in a Forge project's docs/requirements/ — the single source of truth — then propagate the dependent docs and regenerate the traceability matrix, and remind to tag implementing code/tests with @requirement <ID>. The only sanctioned way to introduce or alter a requirement before it is built.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-add-requirement` — add or change a requirement (source of truth)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Keep the
**single source of truth** consistent when introducing or changing a requirement.
`docs/requirements/` is the only source of truth — **every scope change starts
here, before any code** (Principle 1, [`FORGE.md`](../FORGE.md)). Code never leads
the docs; the docs lead the code.

This is the **only** sanctioned way to introduce or alter a requirement (it is the
mechanism `/forge-plan-phase` calls when an idea needs new documental backing).
You **never invent** product scope: write only what the developer states; record
anything undecided as an explicit open question.

## Inputs

- **What** to add or change, in the developer's words (a capability, a quality
  target, a rule, a compliance obligation, an entity, a use case).
- Whether it is a **new** requirement or a **change** to an existing one.

## Step 0 — Read the taxonomy and the tier

Read `docs/requirements/index.md` for the **ID taxonomy** and which documents the
project's **tier** actually instantiated, and `forge.config.json` for
`requirementTiers.selected`, `compliance.regimes`, and `criticalPaths.paths`. You
may only edit documents the tier has; if a needed document does not exist for the
tier, prefer recording the decision as an **ADR**
(`docs/requirements/decisions.md`) or note the tier should grow (via `/forge-init`
extend) rather than inventing a missing doc.

The ID taxonomy (from `index.md`):

| Prefix  | Kind                        | Document            |
| ------- | --------------------------- | ------------------- |
| **FR**  | Functional Requirement      | `functional.md`     |
| **NFR** | Non-Functional Requirement  | `non-functional.md` |
| **BR**  | Business Rule               | `business-rules.md` |
| **CR**  | Compliance Requirement      | `compliance.md`     |
| **UC**  | Use Case                    | `use-cases.md`      |
| **EN**  | Entity (data)               | `data-model.md`     |
| **ADR** | Architecture Decision Record| `decisions.md`      |

## Procedure

1. **Read the index and the related docs** for the topic before editing
   (`docs/requirements/index.md`, then the specific documents the change touches).

2. **Choose the requirement kind and ID.** Pick the right prefix and the **next
   free, zero-padded** number in the owning document (or identify the exact ID to
   change). **Never reuse** a retired number; to drop a requirement, mark it
   obsolete rather than renumbering. Sub-items use a dotted suffix (`FR01.2`).

3. **Write the requirement** into its owning document, matching that document's
   existing structure (e.g. objective + flow + `[Must]/[Should]/[Later]`
   sub-items for `FR`; a measurable target for `NFR`; a rule statement for `BR`; a
   per-regime requirement for `CR`). Follow the project's `conventions.docsLanguage`
   for prose; keep the **ID and any code identifiers in English**.

4. **Propagate to the dependent documents the tier has** (only those that apply):
   - **Business rules** (`business-rules.md`) — for new/changed `BR`.
   - **Data model** (`data-model.md`) — if it adds/changes entities/fields (`EN`).
   - **Interface** (`interface.md`) — if it affects screens/navigation.
   - **Non-functional** (`non-functional.md`) — if it adds a quality target or a
     **critical path** (then mirror it into `forge.config.json → criticalPaths.paths`).
   - **Compliance** (`compliance.md`) — if it touches a regime in
     `forge.config.json → compliance.regimes` (`CR`).
   - **Use cases** (`use-cases.md`) — if a `UC` flow changes.
   - **Architecture / ADR** (`decisions.md`) — if it implies an architectural
     decision, record a **new ADR** from `templates/adr.template.md` (one decision
     per ADR; never edit an Accepted one — supersede it).

5. **Regenerate the traceability matrix.** The matrix is **generated**, never
   hand-edited — run the sync so the new/changed ID appears (initially as a
   **gap**, since no code/test references it yet):

   ```bash
   make forge-traceability            # or: PYTHONPATH=tools python3 -m forge_tools traceability
   make forge-sync-docs               # regenerate everything (STATUS, matrix, changelog) — or run /forge-sync-docs
   ```

   Confirm the new ID is now listed in `<docs.generatedDir>/traceability.md`.

6. **Roadmap / prompts (if it creates work).** If the requirement implies build
   work, do **not** plan it here — hand off to **`/forge-plan-phase`** (interview +
   adherence + log) so the prompt(s) are added to `prompts/state.json` and
   `prompts/ROADMAP.md` on standard.

7. **Remind: tag the code and tests.** When the requirement is later implemented,
   the implementing **code and tests** must carry the matching tag (a keyword from
   `forge.config.json → traceability.tagAliases`, default `@requirement <ID>`; use
   `@rule <ID>` / `@businessRule <ID>` for a `BR`). The matrix flips that ID from
   **gap** to **covered** only once both code and test tags exist.

## Verification

- The requirement appears in its owning document and is **consistent** with the
  dependent docs the tier has (data-model / business-rules / interface /
  non-functional / compliance / use-cases as applicable).
- No **orphan** requirement: every requirement has a path to realization (and, if
  it is a critical path, it is mirrored into `forge.config.json →
  criticalPaths.paths`).
- `<docs.generatedDir>/traceability.md` lists the new/changed ID (a fresh one as a
  **gap** until implemented); `make forge-sync-docs-check` reports no other drift.
- Commit the doc change with the project's commit style, e.g.
  `docs(requirements): add FR07 …`.

## Notes

- **Never invent requirements.** Write only what the developer stated; undecided
  details become an explicit "Open questions" note in the relevant doc.
- **Stack-neutral & tier-aware:** edit only documents the project's tier
  instantiated; read the taxonomy, tier, compliance and critical paths from
  `docs/requirements/index.md` and `forge.config.json`.
- The **matrix is generated** — change the requirements and the code tags, then
  regenerate; never hand-edit `traceability.md`.
- Never remove `docs/requirements/` or `prompts/`.
