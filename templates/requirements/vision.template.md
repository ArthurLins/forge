<!--
  Forge — vision template (tier: lean). The "what & why" of the project.
  Genesis copies this to docs/requirements/vision.md. Replace every
  {{PLACEHOLDER}}; delete these comments once filled. No ID prefix of its own —
  this document frames the project; numbered items live in the other documents.
-->

# {{PROJECT_NAME}} — Vision & Scope

> **Purpose:** state the problem, who it is for, and the boundaries of what is
> being built — the context every other requirement document assumes.

## 1. Problem & objective

{{PROBLEM_STATEMENT}}
<!-- One or two paragraphs: what problem exists today, and what success looks
     like. Keep it concrete and measurable where possible. -->

## 2. Scope

**In scope**

- {{IN_SCOPE_ITEM}}

**Out of scope**

- {{OUT_OF_SCOPE_ITEM}}

<!-- Out of scope is as important as in scope: it stops requirement creep. -->

## 3. User profiles

| Profile         | Goal / what they do                         |
| --------------- | ------------------------------------------- |
| {{USER_ROLE}}   | {{USER_GOAL}}                               |

## 4. Assumptions & constraints

- **Assumption:** {{ASSUMPTION}}
- **Constraint:** {{CONSTRAINT}}
<!-- Constraints often come from forge.config.json (stack, deployment target). -->

## 5. Glossary

| Term         | Definition                                  |
| ------------ | ------------------------------------------- |
| {{TERM}}     | {{DEFINITION}}                              |

---

### Worked stub (generic — replace or delete)

> A small back-office tool to manage **items**: a record with a name, a status,
> and an owner. Users create, list, edit, and archive items, and see a simple
> activity log. *In scope:* item CRUD and search. *Out of scope:* billing,
> external integrations. *User profiles:* **Editor** (manages items),
> **Viewer** (read-only). *Glossary:* **Item** — the primary record this tool
> manages.
