# Roadmap

The **index of all phases and prompts** for this project. Each phase groups a set
of self-contained prompts; each prompt is selected for execution by topological
eligibility over its `dependsOn` (see `next_prompt.py`).

This file is the human-authored plan. The live status of each prompt is tracked
in [`state.json`](state.json) and viewed in [`STATUS.md`](STATUS.md).

> **Empty skeleton.** Genesis (`/forge-init`) seeds the first phase, and phase
> planning (`/forge-plan-phase`) appends the rest. Until then the tables below
> are empty.

## Phases

| Phase | Name | Prompts | Status |
| ----- | ---- | ------- | ------ |
| _none yet_ | | | |

## Prompts

| ID | Phase | Title | Depends on | Status |
| -- | ----- | ----- | ---------- | ------ |
| _none yet_ | | | | |

---

To author a new prompt, copy [`../templates/prompt.template.md`](../templates/prompt.template.md)
into the relevant `phase-<n>-<slug>/` folder, register it in `state.json`, and
regenerate `STATUS.md`.
