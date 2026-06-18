# Forge — end-to-end self-test report

> **A worked walkthrough.** This report records a full dogfood of Forge: copy the
> framework into an empty project, run the genesis interview, plan a phase,
> execute prompts, review the change, and sync derived docs — verifying every
> artifact one stage produces is the valid input the next stage expects. It is
> both a **proof that the loop runs when copied** and a reading-by-example for a
> new adopter.
>
> **Verdict:** **PASS** — the full loop (init → plan → run → review → sync) ran on
> a throwaway sample project; the traceability matrix shows the sample
> requirement → code → test row; `forge-sync-docs --check` is clean; one
> framework gap was found and fixed (in the framework, not the sandbox).

- **Date:** 2026-06-18
- **Method:** the framework was copied to a disposable sandbox
  (`/tmp/forge-selftest/`, excluding `.git`) so the genesis never wrote into the
  shipped framework's empty `docs/requirements/` / `prompts/state.json` seeds. The
  agent played **both** roles — inventing the idea and the interview answers, and
  acting as the build agent the skills describe.
- **Sample idea:** **Tasks** — a tiny, domain-neutral, single-user **CLI to-do
  tracker** (add / list / complete), persisted to a local JSON file. Stack:
  **Python 3 standard library only**, **lean** requirement tier, no compliance,
  one named critical path (`complete-a-task`).

---

## The sample project at a glance

| Aspect | Value |
| ------ | ----- |
| Tier | `lean` (vision, functional, decisions, roadmap) |
| Stack | Python 3 (stdlib only), local JSON store, pip, single `src/` package, GitHub Actions |
| Critical path | `complete-a-task` (open → done) |
| Compliance | none |
| Configured gates | `test` = `python3 -m pytest -q`; `docsCheck` = `make forge-sync-docs-check` (lint/typecheck/build intentionally empty → skipped) |
| Requirement | `FR01 — Manage tasks` (FR01.1–FR01.5) |

---

## Stage-by-stage walkthrough

### 1. Genesis — `/forge-init`  ·  PASS

**Ran:** the genesis flow — idea intake → exploration interview (answered +
confirmed) → tier choice (`lean`) → **stack first** (ADR-001 +
`forge.config.json`) → tier-scaled spec → seeded roadmap → sync → genesis log.

**Observed (each artifact verified as the next stage's input):**

- `forge.config.json` filled: project, Python stack, `requirementTiers.selected =
  lean`, `criticalPaths.paths = ["complete-a-task"]`, `traceability.globs =
  ["src/**/*","tests/**/*"]`, configured `ci.commands`.
- `docs/requirements/decisions.md` with **ADR-001 (stack)** + ADR-002 (JSON
  store); the ADR-001 table mirrors `forge.config.json` (Principle 2).
- Lean spec instantiated: `index.md`, `vision.md`, `functional.md` (FR01),
  `roadmap.md`.
- `prompts/state.json` seeded with phases P0/P1 and two `pending` prompts
  (`P0.1`, `P1.1`); `python3 prompts/next_prompt.py` → `P0.1` (eligible, not
  `BLOCKED`/`DONE`).
- Derived docs generated: `prompts/STATUS.md`, `docs/generated/traceability.md`
  (declares `FR01`, status `gap` pre-implementation), `docs/generated/CHANGELOG.md`.
- `docs/requirements/.logs/genesis-2026-06-18.md` written.
- `make forge-sync-docs-check` → **clean**. Committed `feat(genesis): …`.

### 2. Plan — `/forge-plan-phase`  ·  PASS

**Ran:** the planning flow — intake → interview (answered + confirmed) →
**adherence report** → developer decision → place phase → generate on-standard →
planning log.

**Observed:**

- The interview surfaced that status **filtering** was not covered by FR01.2
  (display only). The adherence step flagged it as a **missing requirement**;
  per the hard rule "nothing planned outside the source of truth", **FR01.5 was
  added to `docs/requirements/functional.md` first**, then the prompt was planned.
- New **Phase 2 (Search)** + prompt `P2.1` (filter by status, `dependsOn:
  ["P1.1"]`, refs FR01.5) generated from `templates/prompt.template.md`,
  self-contained.
- `state.json` updated; `STATUS.md`/`ROADMAP.md` regenerated; `next_prompt.py`
  still names `P0.1`. Planning log `prompts/.logs/planning-phase-2.md` written.
- `make forge-sync-docs-check` → **clean**. Committed `docs(plan): …`.

### 3. Run — `/forge-next` (×2)  ·  PASS

**Ran:** `python3 prompts/next_prompt.py` to pick the eligible prompt, then
executed it in an **isolated subagent** (clean context) applying the Definition
of Done, twice (`P0.1` then `P1.1`).

**Observed:**

- **P0.1 (foundation):** scaffolded `src/tasks/`, `tests/`, `pyproject.toml`, and
  `.github/workflows/ci.yml` running only the **non-empty** configured gates. No
  `@requirement` tag (foundation only — correct). `python3 -m pytest -q` passed;
  `make forge-sync-docs-check` clean. Marked `done` with a commit; `next_prompt.py`
  **advanced to `P1.1`**.
- **P1.1 (feature FR01):** implemented `core.py` (model + JSON store) and `cli.py`
  (argparse add/list/done), with `tests/test_tasks.py` covering the
  **`complete-a-task`** critical path. `@requirement FR01` tags added in **code
  and tests** (parent-id convention, per the golden example). 9 tests passed;
  docs synced; matrix flipped `FR01` to **`covered` (1/1)**. Marked `done`;
  `next_prompt.py` advanced to `P2.1`.
- Each prompt used a `feat(...)` feature commit + a `chore(prompts): …` tracking
  commit (which the changelog generator deliberately skips), keeping
  `forge-sync-docs-check` clean.

### 4. Review — `/forge-review`  ·  PASS (APPROVED)

**Ran:** the `reviewer` subagent (read-only, clean context) over the P1.1 commit.

**Observed — the review is project-driven and skips what is unconfigured:**

- **Applied:** critical-path test (`complete-a-task`), traceability
  (`@requirement` in code + tests), standards (the two configured gates, commit
  style, naming).
- **Skipped (and said so):** module boundaries (no `modularity.md`; lean,
  non-modular), compliance (`compliance.regimes` empty), and the empty
  `lint`/`typecheck`/`build` gates.
- Verdict **APPROVED**, no findings. Written to
  `prompts/.logs/review-98bb686.md`.

### 5. Sync & traceability — `forge-sync-docs`  ·  PASS

**Ran:** `make forge-sync-docs` then `make forge-sync-docs-check`.

**Observed:**

- `--check` reports **no drift** across `STATUS.md`, `traceability.md`, `CHANGELOG.md`.
- The traceability matrix carries the sample **requirement → code → test** row:

  | Requirement ID | Source doc | Code | Tests | Status |
  | -------------- | ---------- | ---- | ----- | ------ |
  | FR01 | `docs/requirements/functional.md` | `src/tasks/cli.py`<br>`src/tasks/core.py` | `tests/test_tasks.py` | covered |

- Final suite state: 2/3 prompts done (67%), `P2.1` next eligible.

---

## Gap found & fixed (in the framework, not the sandbox)

**Gap — dotted sub-item tags were treated as "undeclared".** The requirement
templates and the index taxonomy instruct adopters to use **dotted sub-items**
(`FR01.1`, `NFR01.2`, …) and even to tag code with them (`@requirement FR01.5`).
But the traceability tool declared **only top-level ids** as matrix rows, so a
`@requirement FR01.5` tag in code resolved to *no declared requirement* and was
reported under "tags referencing an undeclared requirement" — a false alarm,
since `FR01.5` **is** declared (as a sub-item of `FR01`).

**Fix (stack-neutral, domain-agnostic):** the traceability generator now **rolls a
sub-id up to its nearest declared ancestor**. `@requirement FR01.5` counts toward
`FR01`'s coverage and is no longer flagged as undeclared; an id with no declared
ancestor still surfaces as unknown.

- File fixed: [`tools/forge_tools/traceability.py`](../../tools/forge_tools/traceability.py)
  (new `_resolve_to_declared()` + roll-up fold in `build_report()`); doc note added
  to [`tools/forge_tools/requirements.py`](../../tools/forge_tools/requirements.py).
- **Deliberately matches the golden example:** parent-id tagging still produces a
  single `FR01` row (no spurious per-sub-item rows), exactly as
  [`examples/golden-example/traceability-row.md`](../../examples/golden-example/traceability-row.md)
  documents. Verified: with only parent tags the matrix is unchanged; only sub-id
  tags trigger the roll-up.

No other gaps. Everything else connected stage-to-stage on the first pass.

---

## Reproducing this self-test

From an empty directory, with the Forge framework copied in:

```bash
# 1. genesis — interview, choose a stack & tier, seed the roadmap
/forge-init                       # answer the interview; confirm the summary

# 2. plan a phase (interview → adherence → generate → log)
/forge-plan-phase

# 3. execute the next eligible prompt(s) in isolated subagents
python3 prompts/next_prompt.py    # names the eligible prompt
/forge-next                       # run it; repeat until DONE

# 4. review a change set (read-only, project-driven)
/forge-review <commit|branch>

# 5. sync derived docs and confirm freshness
make forge-sync-docs
make forge-sync-docs-check        # the CI docs-freshness gate — must be clean
```

A new reader can copy this repository, run `/forge-init`, and reach a planned,
executable roadmap following only the shipped docs — which is exactly what this
self-test demonstrated end to end.
