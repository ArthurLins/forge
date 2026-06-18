# FORGE — the manifesto

> **Forge** is a replicable, **stack-neutral**, **domain-agnostic**,
> agent-orchestrated, spec-driven development methodology. Copy it into an empty
> project, run the genesis interview, and let agents build the project against a
> single source of truth — one self-contained prompt at a time.

This document states the **non-negotiable principles** Forge enforces. Skills,
tools, templates and CI gates exist to uphold these principles; nothing in the
framework may contradict them. They are phrased as *principles*, never as a
specific tool, language, or domain — your project chooses those during genesis
and records them in [`forge.config.json`](forge.config.json).

---

## The eight principles

### 1. Source of truth before code

Requirements live in [`docs/requirements/`](docs/requirements/) and are written
**before** implementation. Code traces back to a requirement; agents never
invent requirements. If something needed is missing, the work stops and the gap
is recorded in the source of truth first — not filled in by guesswork.

### 2. Stack is chosen first

The very first genesis step records a **Stack ADR** and a
[`forge.config.json`](forge.config.json) profile (language, runtime, frameworks,
datastore, package manager, monorepo tool, conventions). Every skill and tool
reads that profile instead of assuming a stack. Changing the stack is an
explicit, recorded decision — never an ambient default.

### 3. Self-contained prompts + an explicit state machine

Work is a suite of **autonomous prompts**: each carries everything an agent
needs and does not depend on conversation history. The suite is tracked in
`prompts/state.json` and executed by **eligibility** — a prompt becomes runnable
only when its declared dependencies are done. Progress is machine-readable and
deterministic, not tribal knowledge.

### 4. Planning is an interview

No phase is planned without an **exploration interview**, an **adherence check**
against the source of truth, and a **planning log**. Plans are derived from
questions and constraints, then written down — so the reasoning behind a phase
survives the session that produced it.

### 5. Agents are orchestrated in isolation

Each prompt runs in a **clean subagent** with a fresh context. A **reviewer**
subagent guards quality and conformance; a **docs-sync** subagent keeps derived
documentation current. Orchestration is reproducible: the same state yields the
same next step regardless of who runs it.

### 6. Derived docs are code

Status, traceability, changelog and any specification artifacts (API contracts,
data models, etc.) are **generated**, never hand-edited. They are committed and
**CI fails if they are stale**. The generators are the only writers of these
files; humans edit the source, not the output.

### 7. Everything is traceable

`@requirement` tags link **requirement → code → test → matrix**. The
traceability matrix is generated from the code, so coverage gaps are visible and
enforceable. A requirement with no implementing code or test is a tracked gap,
not a silent one.

### 8. Guidance is layered

An [`AGENTS.md`](AGENTS.md) sits at the repository root and one sits in each
major area, each pointing to the layer below it. A consolidated **Definition of
Done** gates what counts as "done". Conventions — commit style, naming, language
of docs vs. code — are stated once and inherited everywhere.

---

## How the principles are enforced

| Principle                       | Upheld by                                                        |
| ------------------------------- | ---------------------------------------------------------------- |
| 1 Source of truth before code   | `docs/requirements/` + the genesis interview                     |
| 2 Stack first                   | Stack ADR + `forge.config.json`, read by every skill/tool        |
| 3 Self-contained prompts        | `prompts/` engine (`prompt.template.md`, `state.json`, selector) |
| 4 Planning is an interview      | the plan-phase skill + a planning log per phase                  |
| 5 Isolated orchestration        | run / run-phase / next skills + reviewer & docs-sync subagents   |
| 6 Derived docs are code         | `tools/*` generators + a CI docs-freshness gate                  |
| 7 Traceability                  | `@requirement` tags + the traceability tool + add-requirement    |
| 8 Layered guidance              | `AGENTS.md` (root + per area) + the Definition of Done           |

> These eight are the contract. Everything else in Forge is an implementation
> detail in service of them.
