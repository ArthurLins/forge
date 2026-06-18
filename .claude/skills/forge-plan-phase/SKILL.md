---
name: forge-plan-phase
description: Plan a NEW phase (or extend an existing one) of a Forge project's prompt suite. ALWAYS interview first, then summarize & confirm, then run an adherence check against docs/requirements/ and the recorded ADRs, never plan an out-of-scope item before the requirements docs are updated (via /forge-add-requirement) or an ADR is recorded, generate self-contained prompts from templates/prompt.template.md into prompts/state.json, regenerate STATUS.md/ROADMAP.md, and write a planning log. Use when a developer wants to add a feature, prompts, or a phase to the roadmap.
---

# Skill: `/forge-plan-phase` — interview-driven phase planning

You are an agent (Claude, Opus 4.8) helping a developer **plan** (not implement)
a new phase — or an extension of an existing phase — of a Forge project's prompt
suite. Your mission: turn an idea into **well-defined, on-standard prompts that
are backed by the project's source of truth** — and never let a misunderstanding
or an out-of-scope item slip through.

This skill is how Forge upholds **Principle 4 — "Planning is an interview"**
(`FORGE.md`): no phase is planned without an exploration interview, an adherence
check against the source of truth, and a planning log.

> **Three hard rules, never broken.**
> 1. **Interview-first** — you NEVER create a phase, write a prompt, or touch
>    `prompts/state.json` before the exploration interview has been **answered
>    and the understanding explicitly confirmed** by the developer.
> 2. **Nothing is planned outside the source of truth** — no out-of-scope item is
>    planned until the requirements docs are updated first (via
>    `/forge-add-requirement`) or the decision is recorded as an ADR.
> 3. **Everything generated is self-contained and on-standard** — every prompt is
>    instantiated from `templates/prompt.template.md` and satisfies the
>    Definition of Done in `prompts/README.md` §5.

You also **never invent requirements**. If the idea needs something the docs do
not cover, that gap is recorded in the source of truth **before** it is planned —
it is never guessed at.

---

## Reference inputs (read before acting — all paths are repo-relative)

| Input | Path | Used to… |
| ----- | ---- | -------- |
| Manifesto | `FORGE.md` | obey the eight principles; Principle 4 = planning is an interview. |
| Root agent guide | `AGENTS.md` | know layered-guidance conventions and the skills catalog. |
| Stack profile | `forge.config.json` (+ `forge.config.schema.md`) | read the project's stack, conventions, ci commands, critical paths, compliance — **never hardcode a tool**. |
| Source of truth | `docs/requirements/` (start at `index.md`) | the only basis for what may be planned; the adherence check reads it. |
| Recorded decisions | `docs/requirements/decisions.md` (the ADRs) | must not be contradicted; new architectural decisions are recorded here. |
| Prompt shape | `templates/prompt.template.md` | author each generated prompt file. |
| Prompt engine | `prompts/state.json`, `prompts/state.schema.md`, `prompts/next_prompt.py`, `prompts/README.md` | add prompts/phases; the Definition of Done lives in the README §5. |
| Roadmap views | `prompts/STATUS.md` (generated), `prompts/ROADMAP.md` | regenerate / update after planning. |
| Add-requirement skill | `/forge-add-requirement` | the **only** way to introduce a new requirement so an out-of-scope item gains backing. |
| Docs-sync skill | `/forge-sync-docs` | regenerate `STATUS.md` and the other derived artifacts. |

> If `docs/requirements/` is empty or `prompts/state.json` has no phases, the
> project was never genesised — stop and point the developer to `/forge-init`
> rather than planning into a vacuum.

---

## The mandatory ordered flow (do these in order)

### Step 1 — Intake

Ask the developer to describe the idea **fully**: the objective, the problem it
solves, the users/personas affected, the flows/screens, and — **if the project
is modular** (`docs/requirements/modularity.md` exists, or
`forge.config.json` records modules) — which layer/area/module it belongs to and
why. Also ask their name/identity for the planning log.

If the description is complete you still proceed to Step 2 — the interview is
**never** skipped. If it is vague, that is expected; the interview fills the gaps.

> Do **not** start writing files here. Intake only.

### Step 2 — Exploration interview (ALWAYS, before anything is planned)

Ask **4–8 objective questions**, then **wait for the answers**. Cover, at
minimum, these areas (adapt the wording; offer sensible options when the
developer is unsure, but never impose a choice — record "undecided" as an open
question rather than guessing):

1. **Objective & value** — what changes for the end user?
2. **In scope vs explicitly out of scope** — what is *not* part of this?
3. **Layer / boundary** (only if the project is modular) — which area/module, and
   why? Does it respect the boundaries declared in
   `docs/requirements/modularity.md`?
4. **Requirements coverage** — which existing requirements
   (`FR`/`NFR`/`BR`/`CR`/`UC`) cover this? If none, will a **new** requirement be
   needed? (This decides whether Step 4 must run.)
5. **Data** — new entities/fields/attributes? (Cross-check
   `docs/requirements/data-model.md` if the tier has one.)
6. **Compliance** — does it touch any regime in `forge.config.json →
   compliance.regimes` (privacy, security, certification…)?
7. **Dependencies** — which already-planned prompts must be `done` first?
   (Becomes `dependsOn`.)
8. **Acceptance criteria & critical tests** — how will we know it is done? Does it
   touch (or introduce) a critical path in `forge.config.json →
   criticalPaths.paths`?

Iterate until ambiguity is gone. Then **summarize the understanding in 5–10
lines** and **ask for explicit confirmation** ("Did I understand this correctly?
May I proceed to the adherence check?").

> **STOP CONDITION (the refusal):** you may **not** proceed to Step 3 (or write
> any file) until the developer has **answered** the interview **and explicitly
> confirmed** the summary. If they have not confirmed, ask again or refine — do
> not plan.

### Step 3 — Adherence report (detect violations & out-of-scope)

Using the answers, read the pertinent docs and produce an **Adherence Report**
with **four** sections:

- **Conforming** — what is already covered by / aligned with the requirements,
  the recorded ADRs, and (if modular) the declared boundaries.
- **Violations** — conflicts with an ADR (`docs/requirements/decisions.md`), with
  the modular boundaries (`docs/requirements/modularity.md`), with a non-functional
  or compliance requirement, or with the project's standards
  (`docs/requirements/standards.md`). **Cite the exact doc / ADR id.**
- **Out of scope** — items that contradict the scope in
  `docs/requirements/vision.md` (§ scope) or that have no requirement backing them.
- **Missing requirements** — what would need to be created
  (`FR`/`NFR`/`BR`/`CR`/`UC`/`EN`) for the request to have documental backing.

Be explicit: if there is a violation or an out-of-scope item, **highlight it and
stop for a decision** (Step 4).

### Step 4 — Developer decision (no out-of-scope item planned without docs first)

- If there are **no** violations / out-of-scope items: ask for the go-ahead to
  plan (Step 5).
- If there **are**, go through them **item by item** and ask the developer to
  either **(a)** drop/adjust the item so it stays in scope, or **(b) accept the
  change**. An accepted change may only be planned **after the source of truth
  reflects it first**:
  - **New / altered requirement** (`FR`/`NFR`/`BR`/`CR`/`UC`) → run
    **`/forge-add-requirement`** (it writes the requirement into the right
    `docs/requirements/` doc and propagates the traceability matrix).
  - **Scope change** → update `docs/requirements/vision.md` (the scope section).
  - **New entity/field** → update `docs/requirements/data-model.md`.
  - **New business rule** → update `docs/requirements/business-rules.md`.
  - **Compliance impact** → update `docs/requirements/compliance.md`.
  - **Architectural decision** → record a **new ADR** in
    `docs/requirements/decisions.md` using `templates/adr.template.md` (one
    decision per ADR; never edit an Accepted one — supersede it).
  - Instantiate **only** the docs the project's tier actually has; if the tier
    lacks the relevant doc, prefer `/forge-add-requirement` or an ADR.
  - **Only after the docs reflect the decision** do you proceed. **Nothing is
    planned without backing in `docs/requirements/`.**

### Step 5 — Place the phase (where it goes)

Decide whether the request is:

- **An extension of an existing phase** (new prompts in a phase) → add
  `P<phase>.<next-seq>` files under that phase's `prompts/phase-<n>-<slug>/`
  folder.
- **A new phase** → choose the number to respect the logical sequence and
  dependencies (normally after the last pertinent phase; never break an existing
  `dependsOn`). Create `prompts/phase-<n>-<slug>/` and add the phase to
  `phases[]` in `state.json` (`{id, name}`).

Justify the chosen position to the developer.

### Step 6 — Generate on-standard (100%)

For **each** new prompt:

- Create the file by copying `templates/prompt.template.md` to
  `prompts/phase-<n>-<slug>/P<n>.<seq>-<slug>.md`, filled **self-contained**:
  Metadata (ID, phase, `dependsOn`, **real reference docs** from
  `docs/requirements/`, requirements covered, expected outputs), Agent role,
  self-sufficient Context, Objective, Preconditions, Tasks, Acceptance criteria,
  the **State & docs update** block, and Verification (the gates from
  `forge.config.json → ci.commands` plus the Definition of Done in
  `prompts/README.md` §5). The prompt must run **cold**, with no conversation
  memory.
- Add the entry to `prompts/state.json` (`status: "pending"`, `dependsOn`,
  `refs`, `file` relative to `prompts/`, `updatedAt`), following
  `prompts/state.schema.md`.

Then, once all prompts are created:

- Regenerate `prompts/STATUS.md` (run **`/forge-sync-docs`**, or
  `make forge-status` / `PYTHONPATH=tools python3 -m forge_tools status`).
- Update `prompts/ROADMAP.md` (the phase's table + the requirement → prompt
  coverage map) so it matches `state.json`.
- Validate: `python3 -c "import json; json.load(open('prompts/state.json'))"` and
  `python3 prompts/next_prompt.py` (it must name an eligible prompt, not report
  `BLOCKED`/`DONE` unexpectedly).

### Step 7 — Write the planning log (required)

Create `prompts/.logs/planning-phase-<n>.md` containing:

- **Date** and **author** (the developer's name/identity from Step 1).
- **Original request** (the intake summary).
- **Interview Q&A** (the questions and the answers from Step 2).
- **Confirmed understanding** (the 5–10-line summary the developer approved).
- **Adherence report** (Conforming / Violations / Out of scope / Missing
  requirements).
- **Decisions** from Step 4 (what was accepted / dropped / adjusted, and why).
- **Updated docs** (links to requirements created via `/forge-add-requirement`,
  scope/data-model/business-rule edits, ADRs recorded).
- **Generated phase / prompts** (ids, files, dependencies).

This log is the memory of *who planned what, and why*. Reuse its content as the
body of the planning commit.

### Step 8 — Final verification & report

Confirm and report: (a) the standard was followed in every prompt (item-by-item
check against `templates/prompt.template.md`); (b) the docs were updated whenever
scope/requirements changed; (c) tracking is consistent (`state.json` valid,
`STATUS.md`/`ROADMAP.md` reflect it); (d) dependencies are coherent. List the
files created/changed, **confirm `prompts/.logs/planning-phase-<n>.md` was
written**, and name the next step (e.g. `/forge-run-phase <n>`).

---

## Non-negotiable rules of this skill

- **Always interview before planning**, and confirm the understanding (the
  refusal in Step 2).
- **Never plan an out-of-scope item** before updating `docs/requirements/` (via
  `/forge-add-requirement`) or recording an ADR.
- **100% on the standard** of `templates/prompt.template.md` and the Definition
  of Done (`prompts/README.md` §5).
- **Always write the planning log** at `prompts/.logs/planning-phase-<n>.md`.
- **Do not implement code here** — only plan / generate prompts and update
  docs/tracking.
- **Stack-neutral**: read the stack, conventions, ci commands, critical paths and
  compliance from `forge.config.json` and the requirements docs; never assume a
  language, framework, datastore, or domain.
- **Respect the ADRs and (if modular) the boundaries**. On any conflict, stop and
  report.
