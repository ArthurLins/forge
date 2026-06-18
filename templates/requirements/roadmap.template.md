<!--
  Forge — roadmap template (tier: lean). The phased plan. Genesis seeds this
  with an initial set of phases; the prompt-suite engine turns phases into
  self-contained prompts tracked in prompts/state.json. Replace every
  {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Roadmap

> **Purpose:** the phased plan that turns the requirements into work. Each phase
> groups related requirements into a milestone; the prompt-suite engine expands
> phases into autonomous prompts executed by **eligibility** (a prompt becomes
> runnable when its dependencies are done). This document is the human view;
> `prompts/state.json` is the machine view.

## Phases

| Phase | Goal                       | Delivers (requirement IDs) | Depends on |
| ----- | -------------------------- | -------------------------- | ---------- |
| P0    | {{PHASE_GOAL}}             | {{REQUIREMENT_IDS}}        | —          |
| P1    | {{PHASE_GOAL}}             | {{REQUIREMENT_IDS}}        | P0         |

<!-- Order phases so dependencies flow forward. A phase delivers one or more
     FR/NFR/etc. and may depend on earlier phases. -->

## Milestones

- **{{MILESTONE}}** — {{MILESTONE_DESCRIPTION}}

---

### Worked stub (generic — replace or delete)

| Phase | Goal                                  | Delivers     | Depends on |
| ----- | ------------------------------------- | ------------ | ---------- |
| P0    | Foundation: scaffold, config, CI gate | —            | —          |
| P1    | Item management (create / list / edit)| FR01         | P0         |
| P2    | Search and archive                    | FR01.2, FR01.4 | P1       |

> Milestone **MVP** — a user can create, find, edit, and archive items end to
> end (delivers FR01).
