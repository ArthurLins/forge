<!--
  Forge — decisions template (tier: lean). The architecture decision log (ADRs).
  Genesis copies this to docs/requirements/decisions.md AND pre-fills ADR-001
  (the Stack ADR) from the genesis interview. Replace every {{PLACEHOLDER}};
  delete these comments once filled.
-->

# {{PROJECT_NAME}} — Architecture Decision Records (ADRs)

> **Purpose:** the log of significant, hard-to-reverse decisions. Each ADR is
> immutable once accepted: to change a decision, add a **new** ADR that
> supersedes the old one (mark the old one `Superseded by ADR-NNN`). New ADRs
> use the shared shape in [`adr.template.md`](../adr.template.md).

**ID convention:** ADRs use the prefix **`ADR`** with a three-digit number
(`ADR-001`, `ADR-002`, …), assigned in order and never reused. See the
[index](index.md) for the full taxonomy.

---

## Decision log (summary)

| ADR       | Decision                          | Status        |
| --------- | --------------------------------- | ------------- |
| ADR-001   | Technology stack                  | {{STATUS}}    |
| {{ADR_ID}} | {{DECISION_SUMMARY}}             | {{STATUS}}    |

---

## ADR-001 — Technology stack

> **First-class, decided first.** Forge chooses the stack before anything else
> (Principle 2 in `FORGE.md`). Genesis records the chosen values **here** and in
> [`forge.config.json`](../../forge.config.json) — the two must agree. Every
> Forge skill and tool reads `forge.config.json`; this ADR captures the
> *reasoning* behind those values.

- **Status:** {{STATUS}} <!-- Proposed | Accepted | Superseded by ADR-NNN -->
- **Date:** {{DATE}}

### Context

{{STACK_CONTEXT}}
<!-- What kind of project this is, the team's familiarity, the deployment target,
     and any hard constraints that bound the stack choice. -->

### Decision

The project is built with the following stack (mirrored in `forge.config.json`):

| Aspect             | Choice              | `forge.config.json` field      |
| ------------------ | ------------------- | ------------------------------ |
| Language           | {{LANGUAGE}}        | `stack.language`               |
| Runtime / platform | {{RUNTIME}}         | `stack.runtime`                |
| Frameworks         | {{FRAMEWORKS}}      | `stack.frameworks`             |
| Datastore          | {{DATASTORE}}       | `stack.datastore`              |
| Package manager    | {{PACKAGE_MANAGER}} | `stack.packageManager`         |
| Repo layout        | {{REPO_LAYOUT}}     | `stack.monorepoTool` (if any)  |
| CI provider        | {{CI_PROVIDER}}     | `ci.provider`                  |

<!-- Leave a row's value as "none / not used" when it does not apply — a project
     may use none, some, or all of these. Keep this table in sync with the
     config file; if they ever diverge, the config is the operational source and
     this ADR must be corrected. -->

### Consequences

- {{POSITIVE_CONSEQUENCE}}
- {{TRADE_OFF}}

### Alternatives considered

- {{ALTERNATIVE}} — rejected because {{REASON}}.

---

## ADR-002 — {{DECISION_TITLE}}

<!-- Add further ADRs using adr.template.md. One generic worked stub below. -->

---

### Worked stub (generic — replace or delete)

## ADR-002 — Soft-delete instead of hard-delete

- **Status:** Accepted
- **Date:** {{DATE}}

**Context.** Records may be referenced elsewhere and occasionally need to be
recovered.
**Decision.** Items are archived (a status flag) rather than physically deleted;
archived items are hidden by default and excluded from active listings.
**Consequences.** Recovery and audit are possible; queries must filter out
archived rows, and storage grows over time.
**Alternatives.** Hard-delete — rejected: loses recoverability and audit trail.
