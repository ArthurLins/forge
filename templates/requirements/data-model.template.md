<!--
  Forge — data model template (tier: standard). Entities and relationships.
  Genesis copies this to docs/requirements/data-model.md. Replace every
  {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Data Model

> **Purpose:** the entities, their attributes, and how they relate — the data
> dictionary. Stays conceptual and stack-neutral; the concrete schema lives in
> code and (when applicable) in a generated artifact.

**ID convention:** entities use the prefix **`EN`** (e.g. `EN01`). Reference an
entity by its code in other documents. See the [index](index.md) for the full
taxonomy.

---

## EN01 — {{ENTITY_NAME}}

{{ENTITY_DESCRIPTION}}

| Attribute       | Type        | Notes / constraints              |
| --------------- | ----------- | -------------------------------- |
| {{ATTRIBUTE}}   | {{TYPE}}    | {{CONSTRAINT}}                   |

**Relationships:** {{RELATIONSHIPS}}
<!-- e.g. "EN01 has many EN02"; "EN01 belongs to one EN03". -->

<!-- Repeat the EN## block per entity. -->

---

## Entity-relationship overview

{{ER_OVERVIEW}}
<!-- A short prose or list overview of how the entities connect. A generated ERD
     (if the stack supports it) may be linked from docs/generated/. -->

---

### Worked stub (generic — replace or delete)

## EN01 — Item

The primary record the system manages.

| Attribute    | Type      | Notes / constraints                  |
| ------------ | --------- | ------------------------------------ |
| `id`         | identifier| unique, system-assigned, immutable   |
| `name`       | text      | required, non-empty                  |
| `status`     | enum      | `active` \| `archived`               |
| `ownerId`    | reference | → `EN02.id`                          |
| `createdAt`  | timestamp | set on creation                      |

**Relationships:** an Item (`EN01`) belongs to one Owner (`EN02`); an Owner has
many Items.

## EN02 — Owner

A user who owns items.

| Attribute  | Type       | Notes / constraints |
| ---------- | ---------- | ------------------- |
| `id`       | identifier | unique              |
| `name`     | text       | required            |
