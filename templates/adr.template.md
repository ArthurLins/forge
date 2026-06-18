<!--
  Forge — generic Architecture Decision Record (ADR) template.

  Copy this to add ONE decision to docs/requirements/decisions.md (or keep ADRs
  as separate files if the project prefers). One decision per ADR. An ADR is
  immutable once Accepted: to change a decision, write a NEW ADR that supersedes
  this one and set this one's status to "Superseded by ADR-NNN".

  Replace every {{PLACEHOLDER}}; delete these guidance comments once filled.
  ADRs use the prefix `ADR` with a three-digit, never-reused number (ADR-001…).
-->

# ADR-{{NNN}} — {{DECISION_TITLE}}

- **Status:** {{STATUS}} <!-- Proposed | Accepted | Rejected | Superseded by ADR-NNN -->
- **Date:** {{DATE}}
- **Deciders:** {{DECIDERS}}

## Context

{{CONTEXT}}
<!-- The forces at play: the problem, the constraints, what makes this decision
     necessary now. State facts, not the conclusion. -->

## Decision

{{DECISION}}
<!-- The choice made, in the active voice ("We will…"). Be specific and
     verifiable. If this decision sets stack values, mirror them in
     forge.config.json (this is what ADR-001, the Stack ADR, does). -->

## Consequences

- **Positive:** {{POSITIVE_CONSEQUENCE}}
- **Trade-off:** {{NEGATIVE_CONSEQUENCE}}
<!-- What becomes easier and what becomes harder as a result. Honest trade-offs
     are what make an ADR worth keeping. -->

## Alternatives considered

- {{ALTERNATIVE}} — rejected because {{REASON}}.

<!--
  Worked stub (generic — replace or delete):

  # ADR-002 — Soft-delete instead of hard-delete
  - Status: Accepted
  - Context: records may be referenced elsewhere and occasionally need recovery.
  - Decision: archive records (a status flag) rather than physically delete them.
  - Consequences: recovery and audit are possible; queries must exclude archived
    rows and storage grows over time.
  - Alternatives: hard-delete — rejected: loses recoverability and audit trail.
-->
