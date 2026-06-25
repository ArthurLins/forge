# Contribution log — 2026-06-25 (S2.6 — source-of-truth conflict guard)

**Work item:** `S2.6` (phase S2 — Scale & async-collaboration readiness).
**Command:** `/forge-contribute` (maintainer / solo mode → direct commit).
**Area:** tool/generator — the `forge-validate` integrity gate (additive check).
**Touches:** backed by `ADR-S5`; no new `FR-S*` (forge-validate has no dedicated
capability entry — consistent with how it was introduced in `S1.1`). Closes
review gap **AS-2** (`self/reviews/2026-06-25-scale-async-readiness.md`).

## Proposal

The human-edited source of truth (requirement docs, `prompts/state.json`) is NOT
union-merged (correctly — it is source, not derived), so a parallel merge can
conflict and a silently mis-merged spec could land. Add a pre-merge guard to
`forge-validate` (which runs as a required merge-queue check when
`ci.strictValidation` is on).

## What landed

- **`tools/forge_tools/validate.py`** — new check `source-of-truth-integrity`
  (added to `run_all()` + the docstring):
  - **HARD FAIL** on any unambiguous git conflict marker (`<<<<<<<`, `>>>>>>>`,
    `|||||||`, exactly 7 chars at line start) in `docs/requirements/**/*.md`,
    `prompts/state.json`, or `forge.config.json`. The ambiguous middle marker
    `=======` is deliberately NOT matched alone (it collides with markdown setext
    underlines / table rules); a real conflict always carries `<<<<<<<`/`>>>>>>>`.
  - **WARNING** when a prompt `ref` does not resolve to an existing requirement
    doc under `docs/requirements/` (skipped pre-genesis, when no doc exists).

## Rationale (evidence)

- Keep the trunk green with quality gates and small batches (*Accelerate/DORA*
  2018); every behavior is a CI contract — the Beyoncé Rule (*Software Engineering
  at Google* 2020); conflicting implicit decisions on a shared artifact produce
  bad results, so guard the shared source (*Don't build multi-agents*, Cognition
  2025).

## Constitution check (FORGE.md)

- **Stack-neutral / domain-agnostic / English:** PASS — pure-Python check; no
  stack/domain; scans only the project's source of truth.
- **Source-of-truth-before-code / traceability:** PASS — strengthens both (a
  mis-merged spec or a dangling ref is now caught).
- **Derived-docs-as-code:** PASS — the guard explicitly does NOT put source under
  union-merge; it only reads the source of truth.
- **Root seeds untouched:** PASS — additive tool check; passes trivially on the
  empty seed.
- **Minimal:** PASS — one tool file (one new check + helpers) + self records.

**Result: PASS — no principle violated.** Explicit human confirmation: granted
(maintainer approved S2.6 "conflict-guard + ref-consistency").

## Gate + verification (independently re-run by the maintainer)

- Isolated check (scratch): clean source → PASS, no warning; an injected
  `<<<<<<<`/`>>>>>>>` conflict → hard FAIL on the exact lines (the `=======`
  line correctly ignored); a `ref` to a non-existent doc → WARNING, exit 0.
- `make forge-validate-check` on the Forge repo itself → `source-of-truth-integrity`
  PASS, `RESULT: PASS`.
- `make forge-selfcheck` → PASS (invariants green; root docs fresh).

## Outcome

- _(filled at archive)_ Landed on `main` as a `feat(forge-validate):` commit; the
  derived changelog refreshed via a follow-up `chore(prompts):` bookkeeping
  commit. `S2.6` recorded `done` (phase S2 now 4/8).
