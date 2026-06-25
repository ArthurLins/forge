# Contribution log — 2026-06-25 (S2.2 — prompt context discipline)

**Work item:** `S2.2` (phase S2 — Scale & async-collaboration readiness).
**Command:** `/forge-contribute` (maintainer / solo mode → direct commit).
**Area:** template / engine guidance — the prompt standard + the Definition of Done.
**Touches:** `FR-S12` (template family — context-discipline standard); backed by
`ADR-S5`. Closes review gap **SC-4** (`self/reviews/2026-06-25-scale-async-readiness.md`).

## Proposal

Make the **prompt standard** enforce context discipline so prompts stay within a
tight context budget as projects scale: retrieve only the specific `@requirement`
ids a prompt implements (link docs by id, do not pre-load whole specs), place the
load-bearing instruction at the start/end, and prefer one concrete worked example.

## What landed

- **`templates/prompt.template.md`** — a "Context discipline (budget)" callout in
  the *Context* section, plus scoping language on the *Reference docs* and
  *Requirements covered* metadata bullets (cite the specific ids — those, not
  whole docs, are what to retrieve and tag).
- **`prompts/README.md` §5 (Definition of Done)** — new check: *"Context was
  scoped, not dumped"*.
- **`self/requirements/functional.md`** — `FR-S12` records the context-discipline
  standard.

## Rationale (evidence)

- Long-context recall degrades with input length, *even on simple tasks*
  (*Context Rot*, Chroma 2025), and mid-context detail is the most easily lost —
  a U-shaped position bias (*Lost in the Middle*, Liu et al., TACL 2024). → keep
  the spec scoped and put load-bearing text at the start/end.
- Curate the token set deliberately rather than filling the window (*Effective
  context engineering*, Anthropic 2025); on-demand, by-id retrieval over
  bulk-loading (*Code execution with MCP*, Anthropic 2025).
- Worked examples beat bare field lists for accuracy (*Advanced tool use*,
  Anthropic 2025).

## Constitution check (FORGE.md)

- **Stack-neutral / domain-agnostic / English:** PASS — guidance only; no tool,
  language, or domain assumed; no new stack token introduced.
- **Source-of-truth-before-code:** PASS — backed by `ADR-S5` + the planned `S2.2`.
- **Traceability:** PASS — *strengthens* it (cite the specific `@requirement` ids).
- **Layered guidance:** PASS — the template and the DoD (`prompts/README.md` §5)
  are updated consistently.
- **Derived-docs-as-code / root seeds:** PASS — no generated artifact hand-edited;
  root `prompts/state.json` and `docs/requirements/` seeds untouched.
- **Minimal:** PASS — two distributable files + the self records.

**Result: PASS — no principle violated.** Explicit human confirmation: granted
(maintainer approved S2.2 "as proposed").

## Gate + verification

- `make forge-selfcheck` → PASS (invariants green; no new domain residue; root
  docs fresh).

## Outcome

- Landed on `main` (maintainer mode, direct commit) as
  `feat(forge-prompt): context discipline in the prompt standard (S2.2)` — commit
  **`98c8eb9`** (recorded as `S2.2`'s commit). The derived root changelog was
  refreshed via a follow-up `chore(prompts):` bookkeeping commit (skip-listed by
  `changelog.py`).
- `S2.2` recorded `done`; phase `S2` now 2/8. `make forge-selfcheck` green
  post-commit; not pushed.
