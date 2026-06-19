# Contribution log — 2026-06-18 (team hardening)

**Work items:** `S1.1`, `S1.2` (phase S1 — Team hardening / multi-contributor)
**Command:** `/forge-contribute` (maintainer / solo mode → direct commit)
**Note:** this is a retroactive record — apply & land already happened in this
session (commits `ff1952a`, `1ddddcb`, both pushed); this entry closes the
self-hosting loop by archiving the work in the `self/` roadmap.

## Proposal (two questions raised by the maintainer)

1. **A static validation CI that fails a PR unless the project is structurally
   intact**, optionally enabled at `/forge-init`.
2. **Multiple PRs / multiple contributors** — flagged as a possible structural
   problem (single shared `state.json`, regenerated derived docs, parallel
   prompt execution).

## What landed

- **`S1.1` — `forge-validate`** (`ff1952a`): a distributable static integrity gate
  for adopter projects (state-integrity incl. cycle detection, requirement-tag
  integrity, conventions integrity, config integrity, docs-freshness; passes
  trivially on an empty/pre-genesis project). Plus optional **strict validation
  CI** selectable at `/forge-init` (`ci.strictValidation`, `templates/ci/
  forge-validate.yml.template`, intended as a required check on PRs).
- **`S1.2` — multi-contributor hardening** (`1ddddcb`): the industry-standard
  package, **without re-architecting `state.json`** —
  - **sharded claims** (`prompts/claims/<id>.json`): `next_prompt.py` skips
    claimed prompts so two workers never grab the same one (backward compatible);
  - **merge queue + required checks** (`merge_group` triggers added to Forge's CI
    and the adopter templates);
  - **`merge=union`** for the regenerated, line-oriented derived docs
    (`CHANGELOG.md`, `STATUS.md`, `traceability.md`) — kills the most common
    conflict; resolve canonically with `make forge-sync-docs`;
  - **`docs/guides/teams.md`** documenting the model and exact GitHub settings;
  - `forge-validate` extended with **claims-integrity**; `forge-selfcheck`
    seed-purity and `export.py` reset extended to `prompts/claims/`.

## Constitution check (FORGE.md)

- **Stack-neutral / domain-agnostic / English:** PASS (all knobs from
  `forge.config.json`; no stack or domain hardcoded; residue scans clean).
- **Derived-docs-as-code:** the union-merge attribute keeps generated docs as the
  single source; `make forge-sync-docs` is the canonical writer. PASS.
- **Root seeds untouched:** root `prompts/state.json` empty; `docs/requirements/`
  only `.gitkeep`; `prompts/claims/` ships only `.gitkeep`. PASS.
- **Decision recorded:** the multi-contributor approach (merge queue + claims +
  union-merge + validate gate, not a state re-shard) was an explicit, stated
  design call (see `self/requirements/decisions.md`). PASS.

**Result: PASS — no principle violated.** Human confirmation: granted (maintainer
said "sim" to recording this).

## Gate + verification (independently re-run by the orchestrator)

- `make forge-selfcheck` → PASS; `make forge-validate-check` → PASS.
- Claim-skip proven in a scratch project (no claim → P1; claim P1 → P2; claim
  both → DONE; release → P1).
- Union-merge proven in a scratch git repo (two divergent appends auto-merge,
  both lines present, zero conflict markers).
- `merge_group` present in all three workflows/templates; export resets
  `prompts/claims/` to `.gitkeep` and ships the new distributable files.

## Outcome

- `S1.1` and `S1.2` recorded `done` (commits `ff1952a`, `1ddddcb`); a new phase
  `S1 — Team hardening` added to the self roadmap; self STATUS regenerated.
