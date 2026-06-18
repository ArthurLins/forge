# Forge — framework decisions (self ADRs)

Architecture Decision Records for the **framework itself** (`ADR-S*`). These
record *how Forge maintains Forge*; they serve, and never contradict, the
constitution in [`FORGE.md`](../../FORGE.md). New decisions are added via
[`/forge-contribute`](../../.claude/commands/forge-contribute.md); an Accepted ADR
is never edited in place — it is superseded.

---

## ADR-S1 — Forge is self-hosting (meta-circular)

- **Status:** Accepted
- **Context:** A framework that maintains other projects rigorously must hold
  *itself* to the same bar, or its own changes drift and its invariants rot. The
  external bootstrap harness only *created* Forge; it cannot keep Forge honest
  over time.
- **Decision:** Forge **self-hosts**. It ships a **distributable framework** (what
  adopters copy) and keeps a **self-development workspace** (`self/`, not shipped)
  where Forge's own requirements and improvement roadmap live and evolve using
  Forge's own skills, engine, and gates. An improvement to the framework is made
  *with* the framework, so it is by construction already applied *to* the
  framework.
- **Consequences:** Forge dogfoods itself; its evolution is traceable in `self/`;
  the external harness is now only a one-time bootstrap. Requires a clear
  distribution boundary (`ADR-S2`) and an automated invariant gate (`ADR-S3`).

---

## ADR-S2 — Distribution boundary: a manifest + a clean export

- **Status:** Accepted
- **Context:** Self-development artifacts (the `self/` workspace, the self-only
  tools, Forge's own CI and contributor skill) must never leak into an adopter's
  copy, and an adopter must get a *clean* Forge — not Forge's working state.
- **Decision:** A single **manifest**, [`../../forge.manifest.json`](../../forge.manifest.json),
  declares `selfOnly` (paths excluded from the export) and the `resetOnExport`
  seeds. **`make forge-export DEST=…`** (`tools/forge_tools/export.py`) copies all
  git-tracked files *except* `selfOnly`, then re-blanks the root seeds (empty
  `prompts/state.json`, `docs/requirements/` → only `.gitkeep`, `docs/generated/`
  regenerated/emptied). One command yields a clean Forge — **no copy-paste**.
- **Consequences:** The boundary is declared once and machine-enforced; the gate
  reads the manifest so self-only items are exempt from adopter-facing checks; a
  stale `selfOnly` entry fails `forge-selfcheck` (manifest-coverage).

---

## ADR-S3 — A `forge-selfcheck` gate enforces the constitution

- **Status:** Accepted
- **Context:** The constitution's invariants (stack-neutral, domain-agnostic,
  English, derived-docs-as-code, layered guidance, registration parity, pristine
  seeds) must be *enforced*, not merely documented, on every change to Forge.
- **Decision:** Ship **`tools/forge_tools/selfcheck.py`** — a deterministic Python 3
  checker (no project stack assumed) with `--check` exit codes — asserting:
  seed-purity, registration-parity (distributable skills/commands appear in both
  `AGENTS.md` and the skills catalog; self-only ones exempt), domain-residue
  (hard fail), stack-residue (soft **warning**), manifest-coverage, and
  skill-structure. The `make forge-selfcheck` target runs it **plus**
  `forge-sync-docs-check` so docs freshness is part of the gate. Warnings never
  fail the build.
- **Consequences:** Forge's invariants are continuously verified locally and in
  CI (`ADR-S3` is realized by `.github/workflows/forge-selfcheck.yml`); the gate
  is the hard stop in every `/forge-contribute` landing.

---

## ADR-S4 — `/forge-contribute`: selfcheck-always, PR-optional

- **Status:** Accepted
- **Context:** Improving Forge needs a single, lightweight, meta-circular entry
  point that is safe by default but does not impose heavyweight ceremony (Fowler:
  keep it lean), and that works both for the solo maintainer and for an outside
  contributor.
- **Decision:** **`/forge-contribute`** encodes a lean lifecycle — *scope &
  propose (against the constitution, with explicit human confirmation before
  applying) → record → apply → **gate** (`forge-selfcheck` must pass) → land →
  archive*. **selfcheck is always run; a red change never lands.** Landing is
  **PR-optional**: the default maintainer/solo mode **commits directly** to `main`
  (Conventional Commit); **contributor mode** (`--pr`, or a non-maintainer actor)
  opens a **draft PR** and does not commit to `main`.
- **Consequences:** One command covers solo and contributor flows; the gate is
  mandatory in both; the constitution check and the explicit confirmation are hard
  stops; changes stay minimal and never pollute the root seeds.
