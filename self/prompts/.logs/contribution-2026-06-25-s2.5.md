# Contribution log — 2026-06-25 (S2.5 — WIP limits + dependency-aware scheduling)

**Work item:** `S2.5` (phase S2). **Command:** `/forge-contribute` (maintainer →
direct commit). **Area:** engine + orchestration + gate. **Touches:** `FR-S11`;
backed by `ADR-S5`. Closes review gap **AS-3**.
**Implementation:** isolated subagent + scratch test; verified, gated, landed here.

## What landed (distributable)
- `prompts/next_prompt.py` (+ `self/prompts/next_prompt.py`, identical) — optional
  `--by-impact` flag: among the already-eligible prompts, return the one that
  unblocks the most pending dependents, tie-break by file order. **Default
  (no flag) is byte-identical to before.** Stdlib-only.
- `tools/forge_tools/validate.py` — `claims-integrity` WARNS when ACTIVE
  (non-expired) claims exceed `claims.maxConcurrent` (a WIP limit; never a hard
  fail).
- `forge.config.schema.md` — optional `claims.maxConcurrent` (non-negative int;
  absent/0 = unlimited).
- `.claude/commands/forge-run.md`, `forge-run-phase.md`, `docs/guides/teams.md` —
  parallelism convention: hold at most `claims.maxConcurrent` in-flight claims;
  pick with `next_prompt.py --by-impact`.

## Rationale (evidence)
- The serial fraction bounds speed-up (*Amdahl* 1967) and coordination overhead
  grows combinatorially (*Brooks* 1975); elite delivery uses small batches + WIP
  limits + trunk-based flow (*Accelerate/DORA* 2018; *Reinertsen* 2009); schedule
  from the dependency graph to maximize congruence (*Cataldo* 2006); parallelize
  only independent work (*Multi-agent research system*, Anthropic 2025).

## Constitution check — PASS
Stack-neutral · domain-agnostic · English · selector stdlib-only & default
unchanged · derived-docs-as-code intact · root seeds untouched · minimal. Human
confirmation: granted ("rode todos").

## Gate + verification (independently re-run)
- Selector: no-flag identical to today (P2 in a fixture where file-order≠impact);
  `--by-impact` → P1 (unblocks P4+P5); tie → file order; robust to stray args.
- Validate: `maxConcurrent=1` + 2 fresh claims → WARNING, exit 0; none set → no
  warning. Selector copies byte-identical.
- `make forge-selfcheck` → PASS.

## Outcome
- Landed on `main` as `feat(forge-engine): WIP limits + dependency-aware
  scheduling (S2.5)` — commit **`3789444`**; changelog refreshed via a
  `chore(prompts):` bookkeeping commit. `S2.5` → `done` (phase S2 now 5/8). Not
  pushed.
