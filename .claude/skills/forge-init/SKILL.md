---
name: forge-init
description: Genesis interview for a new project. Turns a one-line idea into a right-sized source of truth — interview first, stack first — then writes a Stack ADR + filled forge.config.json, instantiates tier-scaled docs/requirements/, seeds an initial roadmap in prompts/state.json, syncs derived docs, and records a genesis log. Use as the very first thing in an empty repository copied from Forge.
---

# Skill: `/forge-init` — genesis interview (the front door)

You are an agent (Claude, Opus 4.8) running the **genesis** of a project that was
bootstrapped from the **Forge** framework. Your mission: convert a one-line idea
into a coherent, **right-sized source of truth**, a recorded **stack decision**,
an **initial roadmap**, and **synced derived docs** — with a traceable genesis
log — without inventing anything the developer did not state.

This is the framework's **centerpiece** and the one capability a hand-written
spec never has: the spec is *derived from an interview*, sized to the project.

> **Two hard rules, never broken.**
> 1. **Interview-first** — you NEVER scaffold, write a doc, fill the config, or
>    seed a roadmap before the exploration interview has been **answered and the
>    understanding explicitly confirmed** by the developer.
> 2. **Stack-first** — once confirmed, the **stack** is recorded (ADR-001 +
>    `forge.config.json`) **before** any functional detail is written.

You also **never** invent requirements. If the idea has gaps, you ask; what the
developer does not decide is recorded as an **open question**, not guessed.

---

## Reference inputs (read before acting — these are real, already-built Forge files)

All paths are relative to the project root (the copied Forge folder).

| Input (built in) | Path | Genesis uses it to… |
| ---------------- | ---- | ------------------- |
| Manifesto (F1) | `FORGE.md` | obey the eight principles; Principle 2 = stack first. |
| Root agent guide (F1) | `AGENTS.md` | know layered-guidance conventions, the skills catalog. |
| Stack profile + schema (F1) | `forge.config.json`, `forge.config.schema.md` | the file you FILL (stack, conventions, ci, traceability, docsHooks, tiers, compliance, criticalPaths). |
| ADR shape (F1) | `templates/adr.template.md` | shape of ADR-001 and later ADRs. |
| Agent-guide shape (F1) | `templates/agent-guide.template.md` | optional per-area guides if the project is large. |
| **Requirement tiers + README (F2)** | `templates/requirements/README.md`, `templates/requirements/*.template.md` | choose the tier and instantiate exactly the matching templates. |
| ID taxonomy / index (F2) | `templates/requirements/index.template.md` | the `FR/NFR/BR/CR/UC/EN/EC/ADR` taxonomy and the docs index you produce. |
| **Conventions catalog + map template** | `templates/conventions-catalog.md`, `templates/requirements/conventions.template.md` | propose the relevant cross-cutting `EC` conventions and generate `docs/requirements/conventions.md` (the Conventions Map). |
| Prompt engine (F3) | `prompts/state.json`, `prompts/state.schema.md`, `prompts/next_prompt.py`, `prompts/README.md` | seed the roadmap (phases + first batch of `pending` prompts); DoD lives here. |
| Prompt shape (F3) | `templates/prompt.template.md` | author each seeded prompt file. |
| Derived-docs tools (F4) | `tools/`, `Makefile`, `tools/README.md` | run `forge-sync-docs` so generated docs + `STATUS.md` exist from minute one. |

> If any of these is missing, the repo was not copied from Forge correctly —
> stop and tell the developer rather than improvising.

---

## Idempotence — never silently clobber

Before doing anything, **detect whether a genesis already happened**:

- A spec exists if `docs/requirements/` contains any `*.md` (not just the
  `.gitkeep`), or `forge.config.json → requirementTiers.selected` is non-empty,
  or `prompts/state.json → prompts[]` is non-empty.
- **If a spec exists:** do **not** overwrite. Offer two options and wait:
  (a) **extend** — keep what is there and add to it (defer to `/forge-plan-phase`
  for new phases, `/forge-add-requirement` for new requirements), or
  (b) **re-genesis into a fresh location** the developer names. Never blow away
  an existing source of truth.
- **If the repo is empty** (only the shipped placeholders/`.gitkeep`s): proceed
  with the full flow below.

---

## The mandatory ordered flow (do these in order)

### Step 0 — Preconditions check (silent)

Confirm the Forge inputs above are present and `forge.config.json`,
`prompts/state.json` are still the shipped placeholders. Run the idempotence
check. Only then continue.

### Step 1 — Idea intake

Ask the developer to describe the idea **fully**: the problem it solves, the
users/personas, the core outcomes/value, and any hard constraints. Also ask
their name/identity for the genesis log.

If the description is **complete and unambiguous**, you may still proceed to
Step 2 — the interview is **never** skipped. If it is vague, that is expected:
the interview is how you fill the gaps.

> Do **not** start writing files here. Intake only.

### Step 2 — Exploration interview (ALWAYS, before anything is written)

Ask **5–10 objective questions**, then **wait for the answers**. Cover, at
minimum, these areas (adapt the wording; offer sensible options when the
developer is unsure, but never impose a choice):

1. **Target users & primary value** — who uses it and what changes for them?
2. **In scope vs explicitly out of scope** — what is *not* being built? (This
   becomes `vision.md → §2`.)
3. **Project size** — one area or many? a prototype or a product to operate and
   maintain? a regulated/multi-team surface? (This drives the **tier** in
   Step 3 — quote the "rule of thumb" table in
   `templates/requirements/README.md`.)
4. **The stack** — language, runtime, frameworks, datastore, package manager,
   repo layout (single package / monorepo + which tool), and **CI provider**.
   If the developer is unsure, **offer a few neutral options** and let them
   pick; record "undecided" as an open question rather than guessing.
5. **Compliance** — any regime the project must honor (a privacy, security, or
   certification standard)? Default: none. (Drives `compliance.regimes` and,
   at `full` tier, `compliance.md`.)
6. **Critical paths** — any flows whose failure is most costly and that
   therefore **must** be covered by tests? Default: none. (Drives
   `criticalPaths.paths`.)
7. **Rough phase shape** — what are the first milestones, in what order, and
   what depends on what? (Seeds the roadmap in Step 6.)
8. **Cross-cutting conventions** — **infer the project type** from the earlier
   answers (does it have a UI? an API/service? a CLI? is it data-heavy?), then
   **propose the relevant `EC` conventions** from
   `templates/conventions-catalog.md` (the entries whose **Relevant for** matches
   that type), each with its **default thresholds**. Present them grouped by
   category and ask the developer to **confirm, adjust a threshold, add a custom
   one, or waive** any. Scale the count to the size answer: a **slim** set for a
   lean project, a **fuller** set for standard/full. Do **not** dump the whole
   catalog — propose the matching subset. (Seeds `docs/requirements/conventions.md`
   in Step 5.)

Iterate until ambiguity is gone. Then **summarize the understanding in 5–10
lines** — idea, users, in/out of scope, size→tier, stack, compliance, critical
paths, phase shape, the conventions set — and **ask for explicit confirmation**
("Did I understand this correctly? May I proceed to scaffold?").

> **STOP CONDITION (the refusal):** you may **not** proceed to Step 3 (or write
> any file) until the developer has **answered** the interview **and explicitly
> confirmed** the summary. If they have not confirmed, ask again or refine — do
> not scaffold.

### Step 3 — Choose the tier

From the **size** answer, pick **`lean` | `standard` | `full`** using the
"rule of thumb" in `templates/requirements/README.md`. State the chosen tier and
**which documents it implies** (the tiers are cumulative):

- **lean** → `vision`, `functional`, `decisions`, `roadmap`.
- **standard** → lean **+** `non-functional`, `data-model`, `business-rules`,
  `traceability` (generated).
- **full** → standard **+** `use-cases`, `interface`, `compliance`,
  `architecture`, `modularity`, `standards`.
- **all tiers** → `conventions` (the **Conventions Map**, `EC`). It is
  instantiated regardless of tier; what scales with the tier is how many `EC`
  entries the interview proposes (slim for lean, fuller for standard/full).

Drivers that push **up** a tier (more than one area/module; a data model with
real invariants; any compliance regime; named critical paths; a team large
enough that conventions must be written down) — apply them honestly. Pick the
**smallest tier you can defend**; tiers can grow later.

### Step 4 — Record the STACK FIRST (before any functional detail)

This is Principle 2, and it must happen **before** Step 5.

1. **Write ADR-001 "Technology stack"** into `docs/requirements/decisions.md`.
   Copy `templates/requirements/decisions.template.md` (it pre-includes the
   ADR-001 block) into `docs/requirements/decisions.md`, then fill the ADR-001
   placeholders from the interview: `{{STATUS}}` = `Accepted`, `{{DATE}}` =
   today, the context, the **decision table** (language / runtime / frameworks /
   datastore / package manager / repo layout / CI provider — use "none / not
   used" for what does not apply), consequences, and alternatives considered.
2. **Fill `forge.config.json`** so it **mirrors** ADR-001:
   - `project.name`, `project.purpose`.
   - `stack.{language,runtime,frameworks,datastore,packageManager,monorepoTool}`
     (leave `null` / `[]` for what does not apply).
   - `conventions.*` — keep Forge defaults unless the developer chose
     otherwise; set `docsLanguage` / `codeLanguage` to the chosen doc language
     (default `en`).
   - `requirementTiers.selected` = the Step-3 tier.
   - `compliance.regimes`, `criticalPaths.paths` — from the interview (may be
     empty).
   - `ci.provider` and `ci.commands.{lint,typecheck,test,build,docsCheck}` —
     from the stack answers. If commands are not known yet, leave them empty for
     the CI step (F8) to fill, and record that as an open question. `docsCheck`
     should be the Forge docs-freshness gate (e.g.
     `make forge-sync-docs-check`).
   - `traceability.globs` — adjust to where **this** project's source will live
     (e.g. the chosen repo layout); keep the neutral defaults if unsure.
   - `docsHooks` — add a hook **only** if the project already has a
     stack-specific derived doc to build (e.g. an API contract or a generated
     client); otherwise leave `[]`. Use `_docsHooksExample` in the config as the
     shape. Do **not** invent a hook the project did not ask for.
   - Remove the `_comment` / `_docsHooksExample` documentation keys once filled.
3. **Verify the two agree** — the ADR-001 table and `forge.config.json` must not
   diverge; the config is the operational source.

> ADR-001 and the config are written **here, before** the functional templates,
> precisely so every later step (and every other skill/tool) reads a known
> stack.

### Step 5 — Generate the spec (tier-scaled, nothing invented)

Instantiate **exactly** the templates the chosen tier lists, copying each
`templates/requirements/<name>.template.md` to `docs/requirements/<name>.md`
(drop the `.template` suffix), then fill it from the interview:

- `index.md` (from `index.template.md`) — list only the documents this tier
  produced; set `{{TIER}}` and `{{DOCS_LANGUAGE}}`; keep the ID taxonomy.
- `vision.md` — problem/objective, **in/out of scope**, user profiles,
  assumptions & constraints, glossary.
- `functional.md` — one `FR##` block per stated capability, with flows and
  `[Must]/[Should]/[Later]` sub-items. Assign zero-padded `FR` IDs.
- `decisions.md` — already created in Step 4 (ADR-001). Add any further ADRs the
  interview produced using `templates/adr.template.md`.
- `roadmap.md` — the phase shape from the interview (mirrors Step 6).
- `conventions.md` (the **Conventions Map**, **all tiers**) — copy
  `templates/requirements/conventions.template.md` to
  `docs/requirements/conventions.md`, then fill it with the **`EC` conventions
  confirmed in interview question 8**, drawing each entry's rule / Applies-to /
  Parameters from `templates/conventions-catalog.md`. **Renumber sequentially**
  (`EC-01`, `EC-02`, …), set each **Status** (`active`, or `waived` with the
  reason for any the developer declined), keep the entries grouped by category,
  and replace the worked stub with the first real entry. Scale the set to the
  tier: slim for `lean`, fuller for `standard`/`full`. Record any threshold the
  developer wanted but left undecided as an open question — never guess a value
  beyond the catalog default.
- **standard adds**: `non-functional.md` (`NFR`, measurable), `data-model.md`
  (`EN` entities), `business-rules.md` (`BR`). Mirror named critical paths into
  the "Critical paths"/"Critical rules" sections **and** keep them in sync with
  `criticalPaths.paths`. `traceability.md` is **generated** — do not hand-write
  it; it will be produced in Step 7.
- **full adds**: `use-cases.md` (`UC`), `interface.md`, `compliance.md` (`CR`,
  one section per regime in `compliance.regimes`), `architecture.md`,
  `modularity.md`, `standards.md`.

Rules while filling:

- Replace every `{{PLACEHOLDER}}`; delete the HTML guidance comments once filled;
  replace each template's **worked stub** with the first real item (never leave a
  generic stub that contradicts the project).
- Write only what the developer **stated**. Anything undecided becomes an
  explicit **"Open questions"** note in the relevant doc — never a guess.
- Write all content in the project's `docsLanguage` (default English); keep
  requirement **IDs and code identifiers in English**.

### Step 6 — Seed the roadmap (phases + first batch of prompts)

Translate the phase shape into `prompts/state.json`, following
`prompts/state.schema.md`:

1. Set `project` (the project name), `version` (`"1.0"` is fine), `updatedAt`
   (today). Keep `legend.status`.
2. Add the proposed phases to `phases[]` (`{id, name}`), ordered so dependencies
   flow forward (P0 foundation first).
3. Author a **first batch of `pending` prompts** — at least the foundation phase
   (scaffold/config/CI) plus the first feature phase. For **each** prompt:
   - Create the file from `templates/prompt.template.md` under
     `prompts/phase-<n>-<slug>/P<n>.<seq>-<slug>.md`, filled self-contained:
     Metadata (ID, phase, `dependsOn`, **real reference docs** from
     `docs/requirements/`, requirements covered, expected outputs), Agent role,
     self-sufficient Context, Objective, Preconditions, Tasks, Acceptance
     criteria, the **State & docs update** block, Verification (the gates from
     `forge.config.json → ci.commands` + the DoD in `prompts/README.md` §5).
   - Add its entry to `prompts[]` with `id`, `phase`, `title`, `status:
     "pending"`, `dependsOn`, `refs`, `file` (relative to `prompts/`),
     `updatedAt`. Eligibility is topological over `dependsOn` (the foundation
     prompt has `dependsOn: []`).
4. Remove the `_comment` placeholder key once `state.json` is populated.
5. Validate: `python3 -c "import json; json.load(open('prompts/state.json'))"`
   and `python3 prompts/next_prompt.py` (must report the foundation prompt as
   eligible, not `BLOCKED`/`DONE`).

> Do **not** try to enumerate the whole project as prompts. Seed enough to start
> (foundation + first feature); later phases are planned with `/forge-plan-phase`.

### Step 7 — Sync derived docs

Run the docs-sync orchestrator so generated artifacts exist and are consistent
from the start:

```bash
make forge-sync-docs        # or: PYTHONPATH=tools python3 -m forge_tools sync-docs
```

This regenerates `prompts/STATUS.md`, the traceability matrix and the changelog
under `docs.generatedDir`, and runs any declared `docsHooks` after the core (with
`docsHooks: []` it runs the core only and still succeeds — Forge assumes no
stack). Then update the human roadmap view:

- Regenerate / fill `prompts/ROADMAP.md` (or `docs/requirements/roadmap.md`'s
  view) so it matches `state.json`.
- Confirm freshness with `make forge-sync-docs-check` (the CI gate) — it must
  report **no drift**.

### Step 8 — Write the genesis log (required)

Create `docs/requirements/.logs/genesis-<YYYY-MM-DD>.md` containing:

- **Date** and **developer/author** (from Step 1).
- **Original idea** (the intake summary).
- **Interview Q&A** (the questions and the developer's answers from Step 2).
- **Confirmed understanding** (the 5–10-line summary the developer approved).
- **Chosen tier** and **why** (the size drivers).
- **Stack** (the ADR-001 table) with a link to `docs/requirements/decisions.md`.
- **Conventions Map** — the `EC` entries seeded into
  `docs/requirements/conventions.md` (ids + titles, and any waived with the
  reason), with the inferred project type that drove the selection.
- **Generated docs** (the list instantiated for the tier).
- **Seeded roadmap** (phases + the first batch of prompt IDs).
- **Open questions** carried forward (anything left undecided).

This log is the analogue of a planning log: the memory of *who genesised what,
and why*. Reuse its content as the body of the genesis commit.

### Step 9 — Report + first-run checklist

Report what was created and the next step. Print the **first-run checklist**:

```
Forge genesis complete — first-run checklist
  [ ] Review docs/requirements/decisions.md → ADR-001 (stack) and confirm it
      matches forge.config.json.
  [ ] Skim the instantiated docs/requirements/*.md for any "Open questions".
  [ ] Confirm `python3 prompts/next_prompt.py` names the first eligible prompt.
  [ ] Confirm `make forge-sync-docs-check` reports no drift.
  [ ] Commit the genesis (Conventional Commit, e.g. `feat(genesis): …`).
  Next: run `/forge-plan-phase` to plan the next phase, or `/forge-next` to
  execute the first eligible prompt.
```

---

## Non-negotiable rules of this skill

- **Never** skip the interview or proceed without explicit confirmation
  (the refusal in Step 2).
- **Stack is recorded first** (Step 4) — ADR-001 + `forge.config.json` — before
  any functional detail (Step 5).
- **Never invent requirements**; undecided items are recorded as open questions.
- **Tier-scaled**: instantiate exactly the tier's documents (lean/standard/full),
  using the real F2 templates and the README's rule of thumb. The **Conventions
  Map** (`conventions.md`, `EC`) is instantiated in **every** tier; only the
  number of proposed entries scales with the tier and project type — propose from
  `templates/conventions-catalog.md`, never the whole catalog blindly.
- **Idempotent-aware**: if a spec already exists, offer to extend — never
  silently clobber.
- **Stack-neutral & domain-agnostic**: capture the stack from the interview;
  assume no language/framework/datastore and no business domain. The only
  defaults are Forge's own conventions in `forge.config.json`.
- **Doc language** follows `conventions.docsLanguage` (default English) for
  generated content; this skill's own logic and requirement IDs stay English.
- **Derived docs are generated** (Step 7), never hand-written — `traceability.md`
  especially.
- End with a **Conventional Commit** and the first-run checklist; do not start
  building features here — genesis only bootstraps the source of truth.
