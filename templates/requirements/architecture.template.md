<!--
  Forge — architecture template (tier: full). Technical architecture and
  integrations. Genesis copies this to docs/requirements/architecture.md.
  Replace every {{PLACEHOLDER}}; delete these comments once filled. The stack
  itself is decided in the Stack ADR (decisions.md / forge.config.json); this
  document describes how the pieces fit and talk to the outside world.
-->

# {{PROJECT_NAME}} — Architecture & Integrations

> **Purpose:** the technical architecture — components, how they communicate,
> deployment shape — and the external systems the project integrates with. The
> stack values come from the [Stack ADR](decisions.md) and
> [`forge.config.json`](../../forge.config.json); this document is the *picture*,
> not the stack decision.

<!-- No ID prefix of its own. Architectural decisions belong in decisions.md as
     ADRs; reference them here (e.g. "per ADR-001 / ADR-002"). -->

---

## 1. Overview

{{ARCHITECTURE_OVERVIEW}}
<!-- A short paragraph + (optionally) a diagram link: the major components and
     how a request flows through them. -->

## 2. Components

| Component       | Responsibility            | Talks to                |
| --------------- | ------------------------- | ----------------------- |
| {{COMPONENT}}   | {{RESPONSIBILITY}}        | {{DEPENDENCIES}}        |

## 3. Deployment

{{DEPLOYMENT_MODEL}}
<!-- Where and how it runs; environments; how it is packaged. -->

## 4. External integrations

| Integration     | Direction      | Protocol / contract     | Notes              |
| --------------- | -------------- | ----------------------- | ------------------ |
| {{SYSTEM}}      | {{IN/OUT}}     | {{PROTOCOL}}            | {{NOTES}}          |

## 5. Decision references

This architecture is governed by the ADRs in [decisions.md](decisions.md):
{{ADR_REFERENCES}}.

---

### Worked stub (generic — replace or delete)

> **Overview.** A client surface calls an application service, which persists to
> a datastore. **Components:** client (UI/CLI) → service (business logic) →
> datastore. **Deployment:** packaged and run per the Stack ADR. **External
> integrations:** none in the MVP. **Decision references:** ADR-001 (stack),
> ADR-002 (soft-delete).
