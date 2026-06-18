# Forge

**Forge** is a replicable, **stack-neutral**, **domain-agnostic**,
agent-orchestrated, **spec-driven** development methodology. It turns a vague
idea into a buildable project: a single source of truth, a stack chosen up
front, and a suite of self-contained prompts that agents execute in isolation —
with review, derived-docs, traceability, and CI gates built in.

You bring the idea. Forge brings the process.

## Quickstart

1. **Copy** the `forge/` folder into an empty project (it becomes the project's
   own repository).
2. **Open** it in your agent (e.g. Claude Code).
3. **Run** the genesis interview:
   ```
   /forge-init
   ```
   It interviews you about the idea, helps you **choose the stack first** (and
   records a Stack ADR + `forge.config.json`), writes a right-sized source of
   truth in `docs/requirements/`, and seeds an initial roadmap in `prompts/`.
4. **Plan & build.** Plan phases with `/forge-plan-phase`, then execute prompts
   with `/forge-run` / `/forge-next` — each runs in a clean subagent. Keep things
   honest with `/forge-review` and `/forge-sync-docs`.

> Read [`FORGE.md`](FORGE.md) for the eight principles, and
> [`AGENTS.md`](AGENTS.md) for the root agent guide.

## What each part is for

```
forge/
├─ README.md                  # this file — what Forge is + quickstart
├─ FORGE.md                   # the manifesto: 8 non-negotiable principles
├─ AGENTS.md                  # root layered agent guide (one per major area)
├─ forge.config.json          # stack profile — filled by /forge-init
├─ forge.config.schema.md     # field-by-field reference for the config
├─ .gitignore                 # stack-neutral ignores
├─ .claude/
│  ├─ skills/                 # genesis / planning / orchestration skills
│  ├─ commands/               # review / sync-docs / add-requirement commands
│  └─ agents/                 # reviewer & docs-sync subagents
├─ templates/
│  ├─ requirements/           # scalable requirement templates (lean↔full)
│  ├─ prompt.template.md      # the self-contained prompt template
│  ├─ adr.template.md         # architecture-decision-record template
│  ├─ agent-guide.template.md # the layered AGENTS.md template
│  └─ ci/                     # CI gate template (commits · quality · docs-freshness)
├─ prompts/                   # the prompt-suite engine + state machine
├─ docs/
│  ├─ requirements/           # YOUR source of truth (seeded by genesis)
│  ├─ generated/              # derived artifacts (status, traceability, …)
│  └─ guides/                 # process guides (contributing · project map · skills)
├─ tools/                     # generators for the derived docs
├─ examples/golden-example/   # a single domain-neutral end-to-end example
└─ scripts/                   # optional helpers
```

- **Source of truth** is `docs/requirements/` — written **before** code, never
  invented.
- **Derived docs** in `docs/generated/` are **generated, never edited**; CI
  fails if they go stale.
- **The stack** is recorded once in `forge.config.json` and read everywhere.

## Guides & the golden example

Once you have run genesis, these stack-neutral guides orient you and your agents:

| Read this…                                                           | …to                                                       |
| -------------------------------------------------------------------- | --------------------------------------------------------- |
| [`docs/guides/contributing-agents.md`](docs/guides/contributing-agents.md) | follow the contribution loop + the Definition of Done. |
| [`docs/guides/project-map.md`](docs/guides/project-map.md)           | find where everything lives.                              |
| [`docs/guides/skills-catalog.md`](docs/guides/skills-catalog.md)     | learn each skill/command and when to use it.              |
| [`examples/golden-example/`](examples/golden-example/)               | see the whole loop on a generic feature (mental template). |

The **CI gate** Forge installs lives in
[`templates/ci/`](templates/ci/README.md): a workflow template with **commits**,
**quality**, and **docs-freshness** jobs whose commands all come from
`forge.config.json`.

## Status of this scaffold

This is the **copyable skeleton**: the manifesto, root agent guide and config
placeholder, plus the prompt-suite engine, the derived-docs tools, the genesis /
planning / orchestration / review skills, the CI gate template, the process
guides, and a single domain-neutral golden example. `docs/requirements/` is empty
until `/forge-init` seeds your project's source of truth.
