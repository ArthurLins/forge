<!--
  Forge — functional requirements template (tier: lean). The "what the system
  does". Genesis copies this to docs/requirements/functional.md. Replace every
  {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Functional Requirements

> **Purpose:** describe every functional requirement (**FR**) — objective,
> flow(s), and detailed sub-requirements — grouped by area. IDs are stable and
> are referenced by the [traceability matrix](traceability.md).

**ID convention:** functional requirements use the prefix **`FR`** (e.g.
`FR01`), with dotted sub-items (`FR01.1`). Numbers are never reused. Tag
implementing code and tests with `@requirement FR01`. See the
[index](index.md) for the full taxonomy.

**Priority convention:** **[Must]** (first release), **[Should]** (desirable in
first release), **[Later]** (future versions).

---

## FR01 — {{REQUIREMENT_TITLE}}

**Objective:** {{REQUIREMENT_OBJECTIVE}}

### Flow

1. {{FLOW_STEP_1}}
2. {{FLOW_STEP_2}}

### Requirements

- FR01.1 — {{SUB_REQUIREMENT}} **[Must]**
- FR01.2 — {{SUB_REQUIREMENT}} **[Should]**

<!-- Repeat the FR## block for each functional requirement. Group related FRs
     under area headings if the project is large. -->

---

### Worked stub (generic — replace or delete)

## FR01 — Manage items

**Objective:** let an authorized user create, view, edit, and archive items.

### Flow

1. The user opens the item list.
2. The user creates a new item with a name and an owner.
3. The system saves it and assigns a unique identifier.
4. The user can later edit fields or archive the item.

### Requirements

- FR01.1 — Create an item with a required name and owner; reject an empty name. **[Must]**
- FR01.2 — List items with search by name and filter by status. **[Must]**
- FR01.3 — Edit an item's fields, preserving its identifier and history. **[Must]**
- FR01.4 — Archive (soft-delete) an item rather than hard-delete it. **[Should]**
