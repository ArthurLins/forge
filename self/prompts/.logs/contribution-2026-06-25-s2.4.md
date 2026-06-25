# Contribution log — 2026-06-25 (S2.4 — claim self-healing)

**Work item:** `S2.4` (phase S2 — Scale & async-collaboration readiness).
**Command:** `/forge-contribute` (maintainer / solo mode → direct commit).
**Area:** engine + orchestration + integrity gate — sharded-claim lifecycle.
**Touches:** `FR-S11` (engine self-healing); backed by `ADR-S5`. Closes review
gap **AS-1** (`self/reviews/2026-06-25-scale-async-readiness.md`).
**Implementation:** delegated to an isolated subagent (clean context) with a test
scenario; verified, gated, and landed here by the maintainer.

## Proposal

A sharded claim (`prompts/claims/<id>.json`) was only ever removed by the worker
that wrote it; a crashed worker's claim blocked its prompt **forever** (the
selector skipped it; `forge-validate` only *warned* after 7 days). Make parallel
execution **self-healing**: claims carry an optional `heartbeatAt` the
orchestrator refreshes; the selector auto-releases a claim whose heartbeat goes
stale past a TTL; and the orchestrator moves a prompt to `blocked` after
`maxAttempts` failures.

## What landed

**Distributable (8 files):**
- `prompts/next_prompt.py` **and** `self/prompts/next_prompt.py` (kept identical) —
  TTL-aware claim reading: a claim is skipped unless its `heartbeatAt` is older
  than the TTL (`CLAIM_TTL_SECONDS = 1800`, overridable via
  `forge.config.json → claims.ttlSeconds`); expired claims are **ignored
  non-destructively** (file left in place). Stdlib `json`/`datetime` only; never
  raises on bad input.
- `tools/forge_tools/validate.py` — `claims-integrity` shape-checks the optional
  `heartbeatAt`/`attempts` (malformed → hard fail) and warns on an expired
  heartbeat or `attempts >= maxAttempts` on a non-`blocked` prompt; existing
  checks intact.
- `docs/guides/teams.md` — claim schema + a "Self-healing (heartbeat + TTL)"
  section + the rewritten orchestration convention.
- `.claude/commands/forge-next.md` / `forge-run.md` / `forge-run-phase.md` —
  write an initial `heartbeatAt`, refresh it while running, carry `attempts`
  forward, and set `blocked` after `maxAttempts`.
- `forge.config.schema.md` — the OPTIONAL `claims` object (`ttlSeconds` 1800,
  `maxAttempts` 3; absent = defaults).

**Self records:** `FR-S11` notes the self-healing selector; `S2.4` → `done`.

## Backward-compatibility (the hard guarantee — held)

- No claims dir, or a claim **without** `heartbeatAt` → behavior **byte-identical**
  to before (legacy claims are never auto-released).
- A malformed claim (bad JSON / unparseable timestamp) → treated as **active**
  (the prompt is never wrongly released on bad input).
- The selector stays **stdlib-only** and never raises.

## Rationale (evidence)

- Long-running agent systems need **durable, resumable, self-healing** execution
  rather than manual recovery (*How we built our multi-agent research system*,
  Anthropic 2025). Make queues **visible and bounded** (*Reinertsen* 2009). A
  bounded retry/escalation (move to `blocked` after N) is the validated
  reflect-then-escalate reliability pattern (*Reflexion*, Shinn et al. 2023).

## Constitution check (FORGE.md)

- **Stack-neutral / domain-agnostic / English:** PASS — no stack/domain; selector
  stdlib-only; knobs optional in `forge.config.json`.
- **Isolated orchestration / engine:** PASS — strengthens the engine's robustness;
  selection stays pure topological order; expired-claim handling is additive.
- **Derived-docs-as-code / traceability / layered guidance:** PASS — no generated
  artifact hand-edited; teams.md + the command guides updated consistently.
- **Root seeds untouched:** PASS — all engine/tool edits are distributable; the
  root `prompts/state.json` seed and `docs/requirements/` stay pristine; the
  shipped `prompts/claims/` still holds only `.gitkeep`.
- **Minimal:** PASS — confined to the claim lifecycle; no unrelated refactor.

**Result: PASS — no principle violated.** Explicit human confirmation: granted
(maintainer approved S2.4 "completo" + subagent implementation).

## Gate + verification (independently re-run by the maintainer)

- Selector test (scratch): no claim → P1; fresh heartbeat → P2; **expired
  heartbeat → P1 (auto-released)**; legacy (no heartbeat, 30d old) → P2 (no
  regression); malformed JSON → P2 (treated active). All as expected.
- `forge-validate` (scratch): expired claim → WARNING, exit 0; malformed
  `attempts` → hard FAIL, exit 1.
- `make forge-selfcheck` → PASS (invariants green; root docs fresh).
- The two `next_prompt.py` copies are byte-identical.

## Outcome

- _(filled at archive)_ Landed on `main` as a `feat(forge-engine):` commit; the
  derived changelog refreshed via a follow-up `chore(prompts):` bookkeeping
  commit. `S2.4` recorded `done` (phase S2 now 3/8; this unblocks `S2.5`).
