# Contribution log — 2026-06-25 (S2.3 — module-scoped / incremental derived docs)

**Work item:** `S2.3` (phase S2). **Command:** `/forge-contribute` (maintainer →
direct commit). **Area:** tools/generators. **Touches:** `FR-S9`; backed by
`ADR-S5`. Closes review gaps **SC-1, SC-2, SC-3**.
**Implementation:** isolated subagent + scratch test; verified, gated, landed here.

## What landed (distributable — 6 files)
- `tools/forge_tools/common.py` — `traceability_scopes(config)` (validates the
  optional `traceability.scopes`; `[]` when absent).
- `tools/forge_tools/requirements.py` — `parse_requirements()` gains an optional
  `source_docs` allow-list (default = all; unchanged).
- `tools/forge_tools/traceability.py` — `build_report()` parameterized
  (globs / req-doc filter / title); `--scope NAME` writes
  `<generatedDir>/traceability.<name>.md` over that module's globs + owned docs;
  unknown scope → exit 2. No flag = the global matrix, byte-identical.
- `tools/forge_tools/sync_docs.py` — `--only status|traceability|changelog`
  (subset run) and, when scopes are declared, regenerates/verifies one matrix per
  scope after the global one. No scopes/flags = unchanged.
- `tools/forge_tools/changelog.py` — `--max N` bounds the Unreleased section
  (omitted-count note); absent = unbounded (unchanged).
- `forge.config.schema.md` — documents `traceability.scopes` + the new flags.

## Rationale (evidence)
- Decompose around hidden, change-prone decisions so a module is workable in
  isolation (*Parnas* 1972); module boundaries mirror the contributor/agent
  partition (*Conway* 1968; *Mirroring*, MacCormack et al. 2012); progressive,
  on-demand disclosure instead of regenerating/loading everything (*Code execution
  with MCP*, Anthropic 2025; *Effective context engineering*, 2025).

## Constitution check — PASS
Stack-neutral (scopes/globs from `forge.config.json`) · domain-agnostic · English ·
**derived-docs-as-code** preserved (scoped output is still generated, never
hand-edited) · traceability strengthened (per-module matrices) · root seeds
untouched · minimal & backward-compatible. Human confirmation: granted ("rode
todos").

## Gate + verification (independently re-run)
- **Backward-compat (the hard guarantee):** with no scopes/flags the generators'
  output is **byte-identical to HEAD** — `make forge-sync-docs-check` → no drift;
  `make forge-selfcheck` → PASS.
- Scoped: global matrix (FR01+FR02); `--scope a` → `traceability.a.md`;
  unknown scope → exit 2; `sync-docs` writes global + per-scope; `sync-docs
  --check` fresh → exit 0; `--only` subset; `changelog --max` bounds.

## Outcome
- Landed on `main` as `feat(forge-tools): module-scoped + incremental derived docs
  (S2.3)` — commit **`3f2e41c`**; changelog refreshed via a `chore(prompts):`
  bookkeeping commit. `S2.3` → `done` (phase S2 now 6/8); **unblocks `S2.7` and
  `S2.8`**. Not pushed.
