# Contribution log — 2026-06-25 (S2.7 — ownership metadata / inverse-Conway)

**Work item:** `S2.7` (phase S2). **Command:** `/forge-contribute` (maintainer →
direct commit). **Area:** engine schema + status generator + teams guide.
**Touches:** backed by `ADR-S5`. Closes review gaps **AS-4** (and the scale-side
ownership gap). **Severity:** minor.

## What landed (distributable)
- `prompts/state.schema.md` — documents the OPTIONAL `owner` field on a prompt (a
  person / team / agent / module owner; a routing aid for async work).
- `tools/forge_tools/status.py` — renders an **Owner** column **only when** at
  least one prompt declares an `owner`; otherwise the STATUS is byte-identical to
  before (backward-compatible).
- `docs/guides/teams.md` — new §5 "Ownership / assignment (inverse-Conway
  routing)": assign each module's prompts to the agent/contributor that owns its
  secret; combine with `--by-impact` (§2).

## Rationale (evidence)
- A system mirrors the communication structure of the org that builds it (*Conway*
  1968), empirically confirmed (*Mirroring Hypothesis*, MacCormack et al. 2012):
  assign the partition deliberately (the inverse-Conway maneuver). High
  socio-technical congruence — coordination matching the dependency structure —
  measurably cuts completion time (*Cataldo* 2006).

## Constitution check — PASS
Stack-neutral · domain-agnostic · English · derived-docs-as-code preserved (STATUS
still generated; Owner column conditional) · **traceability/ownership** aided ·
root seeds untouched · minimal & backward-compatible. Human confirmation: granted
("rode todos").

## Gate + verification (independently re-run)
- STATUS with an `owner` → Owner column rendered; without any owner → byte-identical
  STATUS (no drift). `make forge-selfcheck` → PASS.

## Outcome
- _(filled at archive)_ Landed on `main` as `feat(forge-engine):`; changelog
  refreshed via a `chore(prompts):` bookkeeping commit. `S2.7` → `done` (S2 7/8).
