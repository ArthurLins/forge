# Prompt suite — the autonomous-build engine

This folder holds the **structured, self-contained, independent prompts** that
agents execute to build the project, plus the **machine-readable state machine**
that tracks them. Each prompt can run **without relying on prior conversation**:
it references the requirement docs and describes everything the agent needs.

This is the heart of the Forge methodology. Work proceeds autonomously because
every unit of work is a self-contained prompt, tracked in `state.json`, and
selected by topological eligibility over `dependsOn` (`next_prompt.py`).

---

## 1. How to use

1. Open the repository in your agent (e.g. Claude Code).
2. Find the next eligible prompt (its `dependsOn` all `done`):
   ```bash
   python3 prompts/next_prompt.py
   ```
   It prints `<ID>\t<file>`, or `DONE` when nothing is left, or
   `BLOCKED\t<ids>` when pending prompts still have unsatisfied dependencies.
   The human-readable view is **[STATUS.md](STATUS.md)**; the index of all
   phases and prompts is **[ROADMAP.md](ROADMAP.md)**.
3. Open the prompt file (e.g. `phase-1-foundation/P1.1-....md`) and ask the
   agent to execute it.
4. When finished, the agent **updates `state.json`** (status, commit), regenerates
   **`STATUS.md`**, and runs the docs-sync command (`/forge-sync-docs`).

> **Golden rule:** the agent always **reads the referenced docs** in the prompt
> before coding, and never invents requirements. The source of truth is
> `docs/requirements/`.

---

## 2. Conventions

- The **repository root** holds: `docs/requirements/` (the source of truth),
  `prompts/` (this suite), `forge.config.json` (the stack profile), and the
  project workspace once scaffolding lands.
- **Reference paths** in prompts are relative to the repository root.
- **Language** of docs/UI text and of code identifiers follows
  `forge.config.json` → `conventions.docsLanguage` / `conventions.codeLanguage`.
- **Prompt IDs:** `P<phase>.<seq>` (e.g. `P0.1`, `P2.3`).
- **Requirement IDs** follow the project's requirement taxonomy declared in
  `docs/requirements/` (e.g. functional `R-*`, non-functional `NFR-*`, business
  rules `BR-*`, compliance `C-*`).

---

## 3. Folder structure

```
prompts/
├─ README.md            # this guide
├─ ROADMAP.md           # index of ALL phases and prompts
├─ state.json           # machine-readable state (the source of tracking)
├─ state.schema.md      # field-by-field documentation of state.json
├─ STATUS.md            # human-readable view, GENERATED from state.json
├─ next_prompt.py       # selects the next eligible prompt (topological)
└─ phase-<n>-<slug>/    # one folder per phase, holding its prompt files
   └─ P<n>.<seq>-....md
```

The prompt template lives at `templates/prompt.template.md` — copy it to author
a new prompt.

---

## 4. State tracking (required)

State is kept in **`state.json`** (machine-readable) and reflected in
**`STATUS.md`** (human-readable, generated).

### Possible states

`pending` → `in_progress` → `blocked` → `done`

### `state.json` contract

Each prompt is an object with: `id`, `phase`, `title`, `status`, `dependsOn`
(list of ids), `refs` (referenced requirement docs), `file` (path under
`prompts/`), `commit` (hash, when `done`), `updatedAt`. The full schema is
documented in **[state.schema.md](state.schema.md)**.

### Agent responsibility when finishing a prompt

1. Mark the prompt `done` in `state.json`, filling `commit` and `updatedAt`.
2. Regenerate `STATUS.md` from `state.json` (or via `/forge-sync-docs`).
3. Satisfy the Definition of Done (section 5).

---

## 5. Definition of Done (every prompt)

A prompt is only `done` when **all** of the following hold. The list is
**parameterized** — it reads the project's own critical paths and the project's
own commands from `forge.config.json`, so nothing about a specific tool or
domain is baked in here.

- [ ] **Implementation matches the referenced requirements** — nothing invented,
      nothing outside the prompt's scope. (Check it against the docs in the
      prompt's "Reference docs".)
- [ ] **Context was scoped, not dumped** — the prompt retrieved only the specific
      `@requirement` ids it implements (linking docs by id, not pasting large
      excerpts), with the load-bearing spec at the start/end.
- [ ] **Critical-path tests pass.** The critical flows are those declared by the
      project in `forge.config.json` → `criticalPaths.paths` (defined from its
      requirement docs). If the prompt touches a critical path, that path has a
      passing test.
- [ ] **Quality gates pass** — lint, format, type-check, test, and build **as
      defined in `forge.config.json` → `ci.commands`** (`lint`, `typecheck`,
      `test`, `build`, `docsCheck`). No specific tool names are assumed here; run
      whatever the config declares.
- [ ] **Derived docs are synced** — run the docs-sync command
      (`/forge-sync-docs`) so generated artifacts (and `STATUS.md`) are fresh.
      `ci.commands.docsCheck` must report no drift.
- [ ] **`@requirement` tags added** — code and tests that implement a requirement
      carry the matching `@requirement <id>` tag (traceability).
- [ ] **Conventional Commit created** and **CI is green**.
- [ ] **`state.json` and `STATUS.md` updated** (status, `commit`, `updatedAt`).

> If the project declares no critical paths and no CI commands yet (a fresh
> `forge.config.json`), the corresponding checks are vacuously satisfied — but
> genesis (`/forge-init`) and the CI step are expected to fill them, so most
> projects exercise the full list.

---

## 6. Self-sufficiency principles

- Each prompt declares its **objective, preconditions, reference docs, tasks,
  acceptance criteria, and verification**.
- No prompt assumes conversation memory; everything that matters is in the file
  or in the cited docs.
- When a prompt depends on another, that is recorded in `dependsOn` (state.json)
  and in the prompt's "Preconditions".
