# Forge — capabilities (self)

The framework's capabilities, as `FR-S*` items — **one per skill / tool / template
family**, stated briefly (lean by design). These describe what Forge *provides*;
the principles they serve are in [`FORGE.md`](../../FORGE.md). New framework
capabilities are added here via [`/forge-contribute`](../../.claude/commands/forge-contribute.md).

## Genesis & planning

- **FR-S1 — Genesis interview (`/forge-init`).** Turn a one-line idea into a
  right-sized source of truth: interview first, stack first, write a Stack ADR +
  filled `forge.config.json`, instantiate tier-scaled `docs/requirements/`, seed a
  roadmap, sync derived docs. (Serves principles 1, 2, 4.)
- **FR-S2 — Phase planning (`/forge-plan-phase`).** Plan a phase via an
  exploration interview + adherence check against the source of truth + a planning
  log, emitting on-standard prompts. (Serves principle 4.)

## Orchestration

- **FR-S3 — Prompt execution (`/forge-run`, `/forge-next`, `/forge-run-phase`).**
  Execute eligible prompts, each in an isolated clean subagent, in dependency
  order. (Serves principles 3, 5.)
- **FR-S4 — Independent review (`/forge-review` + `reviewer` subagent).** Run a
  read-only reviewer over a change set and emit an APPROVED/REJECTED verdict,
  enforcing only what the project configured. (Serves principle 5.)
- **FR-S5 — Quick change lane (`/forge-freechat`).** Apply the smallest safe edit
  for a colloquial hotfix/tweak, run affected gates, sync docs, log and commit;
  refuse anything needing a new requirement. (Serves principles 5, 6.)

## Source of truth & conventions

- **FR-S6 — Requirement management (`/forge-add-requirement`).** The only
  sanctioned way to add/alter a requirement in `docs/requirements/`, propagating
  dependent docs and the traceability matrix. (Serves principles 1, 7.)
- **FR-S7 — Conventions Map (`/forge-add-convention`).** Add/alter a cross-cutting
  engineering/UX convention (`EC`) every feature honors. (Serves principles 1, 8.)
- **FR-S8 — Feature/module scaffolding (`/forge-new-feature`, `/forge-new-module`).**
  Scaffold a feature or module via the project's declared generator, or a
  stack-agnostic checklist fallback. (Serves principle 2.)

## Derived docs (code)

- **FR-S9 — Derived-docs generators + sync (`/forge-sync-docs`, `tools/forge_tools/*`,
  the `Makefile`).** Generate STATUS, the traceability matrix and the changelog
  from source, with a `--check` mode that fails on drift; orchestrate core
  generators plus declared stack `docsHooks`. (Serves principles 6, 7.)
- **FR-S10 — Status view (`/forge-status`).** Present read-only suite progress and
  the next eligible prompt from the state machine. (Serves principles 3, 6.)

## Engine & templates

- **FR-S11 — Prompt-suite engine (`prompts/` + `next_prompt.py` + `state.json`).**
  A machine-readable state machine that selects the next eligible prompt by
  topological `dependsOn` order. (Serves principle 3.)
- **FR-S12 — Template family (`templates/`).** Right-sized requirement templates
  (lean↔full), the self-contained prompt template, the ADR template, the layered
  agent-guide template, the conventions catalog, and the CI gate template. (Serves
  principles 1, 4, 8.)
- **FR-S13 — Layered agent guides (`AGENTS.md` root + per area).** A root agent
  guide pointing to the layer below, with a consolidated Definition of Done.
  (Serves principle 8.)
- **FR-S14 — Golden example (`examples/golden-example/`).** A single
  domain-neutral, end-to-end worked feature as the mental template. (Serves
  principles 1, 7.)
- **FR-S15 — CI gate template (`templates/ci/`).** A provider-agnostic workflow
  with commits / quality / docs-freshness jobs whose commands come from
  `forge.config.json`. (Serves principles 6, 8.)

## Self-hosting (this workspace)

- **FR-S16 — Distribution manifest (`forge.manifest.json`).** Declare which paths
  are self-only vs. distributable, and the seeds to reset on export. (Serves the
  self-hosting model — `ADR-S2`.)
- **FR-S17 — Invariant gate (`forge-selfcheck`, `tools/forge_tools/selfcheck.py`).**
  Enforce Forge's constitution as automated assertions (seed purity, registration
  parity, domain-residue, stack-residue warnings, manifest coverage, skill
  structure) + docs freshness. (Serves principles 1, 2, 6, 8; `ADR-S3`.)
- **FR-S18 — Clean export (`forge-export`, `tools/forge_tools/export.py`).** Produce
  a clean adopter copy of Forge — git-tracked files minus `selfOnly`, with the
  seeds reset — in one command (no copy-paste). (Serves the self-hosting model;
  `ADR-S2`.)
- **FR-S19 — Meta-circular contribution (`/forge-contribute`).** The entry point
  for improving Forge itself: scope against the constitution → record → apply →
  gate (`forge-selfcheck`) → land (commit or draft PR) → archive. (Serves the
  self-hosting model; `ADR-S4`.)
- **FR-S20 — Framework CI (`.github/workflows/forge-selfcheck.yml`).** Forge's own
  CI: run `make forge-selfcheck` (selfcheck + docs freshness) on PR and push to
  `main`. (Serves principle 6; `ADR-S3`.)
