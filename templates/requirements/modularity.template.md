<!--
  Forge — modularity template (tier: full). Shared core × modules and the
  boundaries between them. Genesis copies this to
  docs/requirements/modularity.md ONLY for projects that are organized as a
  shared core plus pluggable modules/areas. Replace every {{PLACEHOLDER}};
  delete these comments once filled.
-->

# {{PROJECT_NAME}} — Modular Architecture

> **Purpose:** the platform view — a **shared core** plus **modules/areas** —
> and the **boundaries** between them: who may depend on whom, how modules are
> registered, and how new ones are added. Only needed when the project has more
> than one major area; smaller projects skip this document.

<!-- No ID prefix of its own; reference EN/FR/ADR IDs. The boundary rules here
     should match the dependency rules enforced in code (linting / build). -->

---

## 1. Layers

| Layer        | Contains                  | May depend on            |
| ------------ | ------------------------- | ------------------------ |
| {{LAYER}}    | {{WHAT_IT_HOLDS}}         | {{ALLOWED_DEPENDENCIES}} |

<!-- Typical shape: a shared core (used by all), modules (use the core, not each
     other), and shared utilities (depend only on themselves). -->

## 2. Boundary rules

1. {{BOUNDARY_RULE}}
<!-- e.g. "modules depend on the core, never on each other"; "the core does not
     depend on any module". State the rules; the build enforces them. -->

## 3. Module registry & distribution

{{REGISTRY_MODEL}}
<!-- How modules are declared/registered and how a build selects which ones ship. -->

## 4. Adding a module

{{HOW_TO_ADD_A_MODULE}}
<!-- The steps (or the skill) to scaffold a new module within the boundaries. -->

---

### Worked stub (generic — replace or delete)

| Layer       | Contains                        | May depend on        |
| ----------- | ------------------------------- | -------------------- |
| `core`      | shared domain used by all areas | `shared` only        |
| `module-a`  | one feature area                | `core`, `shared`     |
| `shared`    | cross-cutting utilities         | `shared` only        |

> **Boundary rules:** a module depends on `core` and `shared`, never on another
> module; `core` never depends on a module. **Registry:** modules declare
> themselves in a central registry; a build selects which modules ship.
> **Adding a module:** scaffold it, register it, and respect the boundaries
> above.
