# Contributing — guide for AI agents

> Contribution guide **for agents** (and the developers who pilot them) working
> on a Forge-built project. It consolidates the workflow and the Definition of
> Done in one place. Read it alongside the root [`AGENTS.md`](../../AGENTS.md)
> and the area-level `AGENTS.md` for wherever you are working.
>
> **Source of truth for requirements:** `docs/requirements/`. **Never invent
> requirements.** Start from `docs/requirements/index.md`. Everything below is
> **stack-neutral** — the concrete tools and commands come from
> [`forge.config.json`](../../forge.config.json), never from this guide.

---

## 0. TL;DR — the loop of one contribution

```
1. Find work        → /forge-status   ·  python3 prompts/next_prompt.py
2. Read requirements → the docs cited in the prompt (docs/requirements/)
3. Branch           → git branch feat/<id>-<slug>   (never commit straight to the default branch)
4. Implement        → mirror the golden example (examples/golden-example/)
5. Test critical paths → those declared in forge.config.json → criticalPaths.paths
6. Trace            → @requirement <ID> tags in CODE and TESTS
7. Sync docs        → /forge-sync-docs   (STATUS, traceability, changelog, + any stack hooks)
8. Verify           → run forge.config.json → ci.commands  (all green)
9. Update tracking   → state.json (done + commit + updatedAt) → STATUS.md
10. Commit + review  → Conventional Commit → open PR → run /forge-review
```

---

## 1. Choosing the next work

Implementation is driven by a **suite of self-contained prompts** in `prompts/`.
Each prompt states its objective, preconditions, reference docs, tasks,
acceptance criteria and verification — and does **not** rely on prior
conversation.

- **Roadmap:** [`prompts/ROADMAP.md`](../../prompts/ROADMAP.md).
- **Progress:** [`prompts/STATUS.md`](../../prompts/STATUS.md) (generated from
  `prompts/state.json`).
- **Next eligible** (all `dependsOn` are `done`): `python3 prompts/next_prompt.py`
  or `/forge-status`.
- **Run a prompt:** open `prompts/<phase>/<ID>-*.md`. In batches: `/forge-run`,
  `/forge-run-phase <n>` (each prompt in an isolated subagent).

A prompt is eligible only when **all** of its `dependsOn` are `done`.

---

## 2. Before coding: read the requirements

1. Open the documents listed under **"Reference docs"** in the prompt.
2. `docs/requirements/` is the only source of truth. Its depth depends on the
   project's tier (`lean` / `standard` / `full`, recorded in `forge.config.json`
   → `requirementTiers.selected`). The ID taxonomy is in
   `docs/requirements/index.md`:

   | Prefix | Kind                    | Prefix | Kind                          |
   | ------ | ----------------------- | ------ | ----------------------------- |
   | `FR`   | Functional requirement  | `CR`   | Compliance requirement        |
   | `NFR`  | Non-functional req.     | `UC`   | Use case                      |
   | `BR`   | Business rule           | `EN`   | Entity (data model)           |
   | `ADR`  | Architecture decision   | —      | —                             |

3. **If anything is ambiguous or missing:** stop and record the question (in
   `prompts/.logs/<ID>.note.md` when in autonomous mode). **Do not** fill the
   gap yourself. To add or change a requirement, use `/forge-add-requirement` —
   the docs lead the code, never the reverse (Principle 1).

---

## 3. Implementing to the standard

### 3.1. The golden example is the mental template

The canonical end-to-end feature lives in
[`examples/golden-example/`](../../examples/golden-example/): a small,
domain-neutral feature shown from requirement → prompt → code (with
`@requirement` tags) → test → traceability row. Mirror its **shape** whenever
you build a feature — the stack-specific details are yours to fill from
`forge.config.json`.

### 3.2. Honor the stack and the architecture

- Use **only** the language, runtime, frameworks, datastore, package manager and
  monorepo tool declared in `forge.config.json → stack`. Do not introduce a tool
  the project did not choose.
- Respect the recorded **ADRs** (`docs/requirements/decisions.md`) — including
  the Stack ADR.
- If the project is **modular** (`docs/requirements/modularity.md` exists),
  respect its boundaries: depend across boundaries only through the declared
  contracts, never by reaching into another area's internals. The reviewer
  subagent fails a boundary violation.

### 3.3. Code rules (from `forge.config.json → conventions`)

- Casing: files `fileCasing`, types/classes `typeCasing`,
  variables/functions `identifierCasing`, constants `constantCasing` (Forge
  defaults: kebab-case / PascalCase / camelCase / UPPER_SNAKE_CASE).
- **Language:** code identifiers in `codeLanguage`; docs/UI text in
  `docsLanguage` (defaults: English / English).
- Validate inputs at the boundary; map between transport shapes and domain types
  explicitly; never leak a storage model straight out.
- If the project generates a client/contract from a spec, treat it as
  **derived** — never hand-edit it (it is a `docsHooks` artifact).

---

## 4. Critical-path tests (required)

The flows that **must** be covered by a test are exactly those declared in
`forge.config.json → criticalPaths.paths` (defined from the requirement docs —
typically the riskiest business rules and security paths). If your change
touches a critical path, it ships with a passing test for that path.

A PR does **not** integrate with a critical-path test broken. Do not spend tests
on trivial getters — focus on the rule.

---

## 5. Traceability (`@requirement` tags)

The matrix (`<generatedDir>/traceability.md`) is **derived from the code**
(Principle 7):

- Add `@requirement <ID>` in the artifact that implements a requirement —
  and **in its tests** — using the taxonomy IDs (`FR`/`NFR`/`CR`/`UC`/`EN`).
- Add `@rule <ID>` (alias `@businessRule <ID>`) where code enforces a business
  rule (`BR`).
- Every delivered requirement needs **at least one implementation file and one
  test file** carrying the tag, or it shows up as a `gap`/`partial` row. The
  accepted keywords and scanned globs are config (`forge.config.json →
  traceability`), not code.

---

## 6. Syncing the documentation

Run **`/forge-sync-docs`** at the end. In one idempotent pass it regenerates
(Principle 6):

1. **STATUS** of the suite (`prompts/STATUS.md`).
2. **Traceability matrix** (`<generatedDir>/traceability.md`).
3. **Changelog** (`<generatedDir>/CHANGELOG.md`).
4. Any **stack `docsHooks`** the project declared (e.g. an API contract or a
   generated client) — run after the core generators.

CI runs the same orchestrator in `--check` mode (`forge.config.json →
ci.commands.docsCheck`) and **fails** if any derived artifact is stale.

---

## 7. Updating the state tracking

On finishing a prompt:

1. In [`prompts/state.json`](../../prompts/state.json): mark the prompt `done`,
   fill `commit` (hash) and `updatedAt` (ISO date).
2. Regenerate [`prompts/STATUS.md`](../../prompts/STATUS.md) (via
   `/forge-sync-docs`).
3. **If you cannot finish** (error, ambiguity, missing dependency): do **not**
   mark `done`. Leave it `in_progress` (or `blocked`), write the reason in
   `prompts/.logs/<ID>.note.md`, make a partial commit, and stop.

---

## 8. Commit, PR and subagents

- **Conventional Commits** (validated in CI): `feat:`, `fix:`, `chore:`,
  `docs:`, `refactor:`, `test:`, … with the prompt's scope (e.g.
  `feat(<feature>): …`). Derived-doc syncs go under `chore(...)`.
- **Trunk-based:** the default branch is always releasable; use short branches
  (`feat/...`, `fix/...`). PRs require **green CI** before merge.
- **Merge messages:** prefix `Merge ...`.
- **Subagents** (via the orchestration skills): `reviewer`
  (quality/conformance, read-only) and `docs-sync` (derived-doc sync). Run
  `/forge-review` before closing work.

---

## 9. Definition of Done (final checklist)

A prompt/feature is done only when **all** hold (mirrors
[`prompts/README.md` §5](../../prompts/README.md)):

- [ ] Code matches the referenced requirements (nothing invented, nothing
      out of scope).
- [ ] **Critical-path tests pass** for any critical path touched
      (`forge.config.json → criticalPaths.paths`).
- [ ] **Quality gates pass** — `forge.config.json → ci.commands`
      (`lint` / `typecheck` / `test` / `build`) all green.
- [ ] **Derived docs synced** (`/forge-sync-docs`); `ci.commands.docsCheck`
      reports no drift.
- [ ] **`@requirement` tags** present in the relevant code **and** tests.
- [ ] **Conventional Commit** created; PR opened; **CI green**.
- [ ] `prompts/state.json` and `prompts/STATUS.md` updated.

---

## 10. Project map and skills

- **Where everything lives:** [`project-map.md`](project-map.md).
- **Skills & commands catalog:** [`skills-catalog.md`](skills-catalog.md) —
  prefer a skill over a manual procedure; it keeps the standard and updates the
  derived docs for you.
