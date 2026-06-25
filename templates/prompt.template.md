# [P<phase>.<seq>] — <Prompt title>

> Standard template for a Forge prompt. Copy and fill it in. Every prompt is
> **self-contained** and **independent of conversation context** — an agent must
> be able to execute it cold, from the file and the referenced docs alone.

---

## Metadata

- **ID:** P<phase>.<seq>
- **Phase:** <phase number and name>
- **Depends on:** <prompt ids or "none">
- **Reference docs (read before starting)** — list only the docs/sections THIS
  prompt needs (link by requirement id; do not pre-load whole specs):
  - `docs/requirements/index.md`
  - `docs/requirements/conventions.md` (Conventions Map — apply matching `EC-` rules)
  - `docs/requirements/<specific docs/sections for this prompt>`
- **Requirements covered:** <the specific requirement ids this prompt implements,
  e.g. R-xx / NFR-xx / BR-xx / C-xx — these ids (not whole docs) are what to
  retrieve, implement, and tag>
- **Expected outputs / artifacts:** <folders / files / resources this prompt produces>

---

## Agent role

You are an autonomous build agent working on this repository. **Read the
reference docs above before any action.** The source of truth for requirements
is `docs/requirements/`. Do **not** invent requirements; if something is
ambiguous, record the open question and follow the decision most aligned with
the docs and the recorded architecture decisions (ADRs, see
`docs/requirements/decisions.md`). Honor the project's stack and conventions as
declared in `forge.config.json` — do not hardcode tools the project did not
choose.

**Honor the Conventions Map.** Read `docs/requirements/conventions.md` (if the
project has one) and identify **every `EC-` entry whose "Applies to" scope
matches the work in this prompt** — e.g. pagination/virtualization for any list,
async loading/empty/error states for any fetched view, authorization on every
action, avoid N+1, accessibility, debounced search. Apply each matching **active**
`EC` within its **Parameters**, and **record which `EC` ids you honored** in the
relevant code and tests (optionally as `@convention EC-xx` tags). These are
cross-cutting defaults you must not skip just because the requirement text does
not restate them. If, while building, you hit a **recurring concern that the map
does not cover**, do **not** silently invent a one-off rule: **propose** adding
it to the map via **`/forge-add-convention`** (a `proposed` entry for the
developer to approve).

## Context (self-sufficient)

<A summary of everything that matters for this prompt, with no reliance on prior
conversation. Always point to the docs that back each claim.>

> **Context discipline (budget).** Include only what THIS prompt needs. Retrieve
> the specific `@requirement` ids it implements — link to requirement docs by id
> rather than pasting large excerpts (long context degrades recall, and
> mid-context detail is the most easily lost). Put the load-bearing instruction —
> the Objective and the Acceptance criteria — where attention is strongest: near
> the **start** and restated at the **end**. Prefer one concrete worked example
> over a long abstract description.

## Objective

<The expected result, in 1–3 sentences.>

## Preconditions

- <state of the repository / prompts already done / services available>

## Tasks

1. <step>
2. <step>
3. <…>

## Acceptance criteria

- [ ] <verifiable condition>
- [ ] Applicable Conventions Map (`EC-`) rules are honored — every `EC` whose
      "Applies to" matches this prompt's work is applied within its parameters,
      and the honored `EC` ids are recorded in code/tests.
- [ ] <…>

## State & docs update (required)

1. Add `@requirement <id>` tags in the relevant code **and tests** (traceability).
2. Run the docs-sync command (`/forge-sync-docs`) to regenerate derived
   artifacts (e.g. API spec, ERD/data dictionary, traceability matrix,
   changelog, `STATUS.md`) — only those the project actually has.
3. Update `prompts/state.json` (`status` → `done`, plus `commit` and
   `updatedAt`) and regenerate `prompts/STATUS.md`.
4. Create a **Conventional Commit** (e.g. `feat(<scope>): …`).

## Verification

- <how to validate: the quality gates from `forge.config.json`
  (`ci.commands.lint` / `typecheck` / `test` / `build` / `docsCheck`), plus any
  prompt-specific checks — screenshots, sample runs, etc.>
- Confirm **CI is green** and the **Definition of Done** is met
  (see `prompts/README.md`, §5).
