# `self/` — Forge maintaining Forge (the dogfood)

This is **Forge of Forge**: the workspace where the Forge framework is used to
maintain **itself**. Forge ships a methodology for building projects against a
single source of truth; here that same methodology is turned inward — Forge's own
requirements and improvement roadmap live in this folder and evolve through the
very skills, engine, and gates Forge ships.

> **Forge is self-hosting (meta-circular).** When the framework improves itself,
> it does so *with* itself — so an update to Forge is, by construction, already
> updated *for* Forge. There is no copy-paste bootstrap step that drifts.

## What lives here

| Path                 | What it holds                                                       |
| -------------------- | ------------------------------------------------------------------ |
| `requirements/`      | Forge's **own** source of truth — lean: vision, the framework's capabilities as `FR-S*`, and the framework ADRs (`ADR-S*`). The constitution itself is [`FORGE.md`](../FORGE.md). |
| `prompts/`           | the **improvement roadmap engine** — `state.json` + `next_prompt.py` + generated `STATUS.md`, scoped to Forge's own evolution (phase `S0` and beyond). |
| `prompts/.logs/`     | contribution logs written by `/forge-contribute`.                  |
| `reviews/`           | evidence-grounded readiness/gap reviews that justify a planned phase (e.g. the scale & async-collaboration audit behind phase `S2`). |

## The constitution

The non-negotiable source of truth for Forge's design is **[`FORGE.md`](../FORGE.md)**
— the eight principles. The requirements in `requirements/` describe the
framework's *capabilities* and *decisions*; they never contradict the
constitution. Every change here is scoped against `FORGE.md` before it is applied.

## How a change happens

Improvements are made through **[`/forge-contribute`](../.claude/commands/forge-contribute.md)**
(the meta-circular contributor entry point): scope & propose against the
constitution → record a work item here → apply the minimal change → **gate** with
`make forge-selfcheck` → land (direct commit for the maintainer, draft PR for a
contributor) → archive. See [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## Self-development only — NOT shipped to adopters

Everything under `self/` is **excluded from the adopter export**. The
distribution boundary is declared in
[`../forge.manifest.json`](../forge.manifest.json) (`selfOnly`), and
`make forge-export DEST=…` produces a clean Forge copy with this workspace (and
the other self-only paths) removed and the root seeds re-blanked. Adopters get the
framework; they do not get Forge's own working state.
