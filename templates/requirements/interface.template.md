<!--
  Forge — interface template (tier: full). Screens, navigation, and design
  system. Genesis copies this to docs/requirements/interface.md. Replace every
  {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Interface & Design

> **Purpose:** the screens (or surfaces), how the user navigates between them,
> and the brand/design-system rules they follow. Each screen maps back to the
> functional requirements it serves.

<!-- This document has no ID prefix of its own; reference FR/UC IDs. For a
     non-visual project (e.g. a CLI or a library), reframe "screens" as
     commands/surfaces, or drop this document from the tier. -->

---

## Screens / surfaces

| ID  | Screen / surface | Serves (FR/UC) | Primary actions          |
| --- | ---------------- | -------------- | ------------------------ |
| S1  | {{SCREEN_NAME}}  | {{FR_UC_IDS}}  | {{ACTIONS}}              |

## Navigation

{{NAVIGATION_OVERVIEW}}
<!-- How users move between screens; entry points; role-based visibility. -->

## Design system & brand

- **Brand:** {{BRAND_NOTES}}
- **Tokens / components:** {{DESIGN_TOKENS}}
- **Accessibility:** {{ACCESSIBILITY_NOTES}}

<!-- Keep design choices consistent with forge.config.json (frameworks) and any
     UI framework chosen in the Stack ADR. -->

---

### Worked stub (generic — replace or delete)

| ID  | Screen        | Serves | Primary actions               |
| --- | ------------- | ------ | ----------------------------- |
| S1  | Item list     | FR01   | search, create, open, archive |
| S2  | Item detail   | FR01   | edit, save, archive           |

> Navigation: the list (S1) is the entry point; selecting an item opens the
> detail (S2). Design system: follow the project's component library and tokens;
> meet the project's accessibility target.
