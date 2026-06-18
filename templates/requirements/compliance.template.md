<!--
  Forge — compliance template (tier: full). Regulatory / standards obligations.
  Genesis copies this to docs/requirements/compliance.md ONLY when the project
  declares one or more regimes in forge.config.json (compliance.regimes).
  EMPTY BY DEFAULT — Forge assumes NO compliance regime. Replace every
  {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Compliance Requirements

> **Purpose:** the obligations imposed by the **compliance regimes** this
> project must honor (e.g. a privacy law, a security standard, a certification,
> an industry data-exchange standard). Forge is domain-neutral and assumes **no
> regime by default**; a project lists its regimes in
> [`forge.config.json`](../../forge.config.json) → `compliance.regimes`, and this
> document details each one's requirements.

**ID convention:** compliance requirements use the prefix **`CR`** (e.g.
`CR01`), and may be sub-scoped per regime (e.g. `CR-PRIV01`, `CR-SEC01`). Tag
implementing code/tests with `@requirement CR01`. See the [index](index.md) for
the full taxonomy.

> If `compliance.regimes` is empty, this document is **not instantiated** —
> there is nothing to comply with beyond the project's own NFRs.

---

## Regimes in scope

| Regime          | Why it applies         | Config entry (`compliance.regimes`) |
| --------------- | ---------------------- | ----------------------------------- |
| {{REGIME_NAME}} | {{WHY_APPLICABLE}}     | {{CONFIG_VALUE}}                    |

---

## CR01 — {{COMPLIANCE_REQUIREMENT_TITLE}}

- **Regime:** {{REGIME_NAME}}
- **Obligation:** {{OBLIGATION}}
- **How the system satisfies it:** {{IMPLEMENTATION_NOTE}}
- **Evidence / verification:** {{EVIDENCE}}

<!-- Repeat the CR## block per compliance requirement, grouped by regime. -->

---

### Worked stub (generic — replace or delete)

> Example of the **shape** only — uses a neutral, invented standard. Replace with
> the project's real regimes.

## CR01 — Record-retention obligation

- **Regime:** "Generic Data-Retention Standard" (illustrative)
- **Obligation:** retain records for a defined minimum period before deletion.
- **How the system satisfies it:** archived records are retained for the
  configured retention window and excluded from hard-delete.
- **Evidence / verification:** an automated test asserts archived records survive
  the retention window; the audit log records deletions.
