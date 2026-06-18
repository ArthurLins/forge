# AGENTS.md — Forge (repository root)

> This is the **root** layered agent guide for the Forge framework repository
> itself. It is a meta-level instantiation of
> [`templates/agent-guide.template.md`](templates/agent-guide.template.md): the
> same shape every project gets, applied to Forge. When Forge is copied into a
> real project, the genesis interview replaces this file with a project-specific
> root guide (and adds one guide per major area).
>
> Source of truth for Forge's principles: [`FORGE.md`](FORGE.md). Stack profile:
> [`forge.config.json`](forge.config.json) (neutral until `/forge-init` fills it).

## What this is

**Forge** is a replicable, stack-neutral, domain-agnostic, agent-orchestrated,
spec-driven development methodology. A developer copies the `forge/` folder into
an empty project, opens it in their agent, and runs a **genesis interview** that
captures the idea, **chooses the stack first**, writes a right-sized source of
truth, and seeds a roadmap. From there, agents build the project as a suite of
self-contained prompts, each in an isolated subagent, against that source of
truth — with reviewer and docs-sync subagents and CI gates keeping it honest.

This repository is the **framework itself**, not a product. It ships empty
scaffolding, templates, an engine, tools, skills, a manifesto, and a single
domain-neutral example. It must stay **stack-neutral** (never hardcode a
language/framework/datastore) and **domain-agnostic** (no business-domain
residue).

## The stack (from `forge.config.json`)

Forge has **no stack of its own** — that is the whole point. The root
`forge.config.json` ships with neutral/empty values; a real project fills it
during genesis, and from then on every skill and tool reads it.

| Aspect          | Value (Forge repo)                              |
| --------------- | ----------------------------------------------- |
| Language        | none assumed — set by `/forge-init`             |
| Runtime         | none assumed                                    |
| Frameworks      | none assumed                                    |
| Datastore       | none assumed                                    |
| Package manager | none assumed                                    |
| Monorepo tool   | none assumed                                    |

## Source of truth

For a real project, the only source of truth is `docs/requirements/`, seeded by
genesis. **Never invent requirements.** For **Forge's own** design, the source
of truth is [`FORGE.md`](FORGE.md) (the eight principles) plus this guide; the
build is driven by an external harness of build prompts (it lives outside this
repo, in the orchestrator's workspace).

| Where                   | What it holds                                              |
| ----------------------- | ---------------------------------------------------------- |
| `FORGE.md`              | the manifesto — eight non-negotiable principles            |
| `README.md`             | what Forge is + quickstart (`/forge-init`)                 |
| `docs/requirements/`    | a project's source of truth (empty until genesis)          |
| `docs/generated/`       | derived artifacts (status, traceability, …) — never edited |
| `docs/guides/`          | process guides (filled later in the build)                 |

## Non-negotiable rules

1. **Stay stack-neutral and domain-agnostic.** No file in this repo may hardcode
   a language, framework, datastore, or a business domain. Parameterize via
   `forge.config.json` instead.
2. **Uphold the eight principles** in [`FORGE.md`](FORGE.md). Skills, tools and
   templates exist to enforce them; none may contradict them.
3. **English everywhere** in framework content (identifiers, docs, templates).
4. **Derived docs are generated, not edited.** Anything under `docs/generated/`
   is written by a tool; edit the source, then regenerate.
5. **Traceability is the pattern.** Forge teaches `@requirement` tags linking
   requirement → code → test → matrix; keep that mechanism intact.
6. **Conventional Commits**, validated in CI.
7. **Sync derived docs** before finishing a change (the sync skill).
8. **Update tracking** (`prompts/state.json`) when a prompt is done.

## How to find the next work

For a **project built with Forge**:

- Roadmap: `prompts/` (seeded by genesis)
- Current progress: `docs/generated/STATUS.md` (generated)
- Next eligible prompt: the next/run skill, or the prompt selector
- The Definition of Done lives with the prompt engine.

For **building Forge itself**, the build prompts are run from the external
harness in dependency order; each is autonomous.

## Skills catalog

> Prefer a skill over a manual procedure — it keeps the standard and updates the
> derived docs for you. Skills are filled in during the build (F5–F7); the table
> below is the intended catalog.

| Skill / command       | When to use                                           | How to call           |
| --------------------- | ----------------------------------------------------- | --------------------- |
| **forge-init**        | Start a new project: interview → stack → spec → roadmap | `/forge-init`       |
| **forge-plan-phase**  | Plan a new phase (interview + adherence + log)        | `/forge-plan-phase`   |
| **forge-run**         | Execute the next eligible prompt(s)                   | `/forge-run`          |
| **forge-run-phase**   | Execute a whole phase, each prompt in a subagent      | `/forge-run-phase`    |
| **forge-next**        | Execute only the next eligible prompt (safe, 1×)      | `/forge-next`         |
| **forge-review**      | Independent review of a change before integrating     | `/forge-review`       |
| **forge-sync-docs**   | Regenerate derived docs (status, traceability, …)     | `/forge-sync-docs`    |
| **forge-add-requirement** | Add/alter a requirement and propagate the matrix  | `/forge-add-requirement` |

## Language & naming conventions

- **English** in all Forge framework content (docs, templates, identifiers). A
  real project may choose a different docs/UI language in `forge.config.json`;
  code identifiers stay in English.
- File names in `kebab-case`; types/classes in `PascalCase`;
  variables/functions in `camelCase`; constants in `UPPER_SNAKE_CASE`. (These
  are Forge's own defaults; a project may override them in `forge.config.json`.)

## Definition of Done (this layer)

- Every artifact is English, stack-neutral, and domain-agnostic.
- New skills/tools read `forge.config.json` rather than assuming a stack.
- The eight principles in `FORGE.md` remain consistent with the change.
- Derived docs (if any) are regenerated; commits follow Conventional Commits.
