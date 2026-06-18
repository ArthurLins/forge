<!--
  Forge — use cases template (tier: full). Detailed interaction flows. Genesis
  copies this to docs/requirements/use-cases.md. Replace every {{PLACEHOLDER}};
  delete these comments once filled.
-->

# {{PROJECT_NAME}} — Use Cases

> **Purpose:** detailed use cases — actors, pre-conditions, the main flow, and
> the alternate/exception flows — for the interactions that warrant step-by-step
> precision. Use cases realize functional requirements and enforce business
> rules.

**ID convention:** use cases use the prefix **`UC`** (e.g. `UC01`). Reference
the requirements and rules each use case touches. See the [index](index.md) for
the full taxonomy.

---

## UC01 — {{USE_CASE_TITLE}}

- **Actor(s):** {{ACTORS}}
- **Realizes:** {{FR_IDS}} — **Enforces:** {{BR_IDS}}
- **Pre-conditions:** {{PRECONDITIONS}}
- **Post-conditions:** {{POSTCONDITIONS}}

**Main flow**

1. {{STEP}}
2. {{STEP}}

**Alternate flows**

- A1. {{ALTERNATE_STEP}}

**Exception flows**

- E1. {{EXCEPTION_STEP}}

<!-- Repeat the UC## block per use case. -->

---

### Worked stub (generic — replace or delete)

## UC01 — Create an item

- **Actor(s):** Editor
- **Realizes:** FR01 — **Enforces:** BR01
- **Pre-conditions:** the actor is authenticated and authorized to edit.
- **Post-conditions:** a new item exists with a unique identifier.

**Main flow**

1. The Editor opens the item list and chooses "New item".
2. The Editor enters a name and selects an owner.
3. The system validates the input and saves the item.
4. The system shows the new item in the list.

**Alternate flows**

- A1. The Editor cancels before saving; no item is created.

**Exception flows**

- E1. The name is empty → the system blocks the save and shows a validation
  message (BR01).
