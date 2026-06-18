# Skills & commands catalog

Guide for **any developer** (piloting AI agents) to work on a Forge-built project
in a standardized way. The skills/commands ensure the project's standard and its
source of truth (`docs/requirements/`) are always respected. They are all
**stack-neutral** — each reads [`forge.config.json`](../../forge.config.json) and
adapts, never assuming a language, framework, datastore, or domain.

> In the current agent tooling, "commands" and "skills" produce the same `/<name>`
> entry point. A file in `.claude/commands/<name>.md` and a skill in
> `.claude/skills/<name>/SKILL.md` both create `/<name>`. Skills have their own
> folder, may carry supporting files, and can be auto-suggested by the agent when
> relevant.

## How to invoke

Open the project in your agent and type `/` — the items below appear. You can
also ask in natural language ("plan a new phase for X") and the agent suggests
the matching skill (e.g. `forge-plan-phase`).

## Catalog

| Item                      | Type    | When to use                                                                                          | Call                       |
| ------------------------- | ------- | ---------------------------------------------------------------------------------------------------- | -------------------------- |
| **forge-init**            | skill   | Start a new project: interview → choose the **stack first** → right-sized source of truth → seeded roadmap. Run as the very first thing in an empty repo copied from Forge. | `/forge-init`              |
| **forge-plan-phase**      | skill   | Plan a new phase/feature: interview, adherence check against `docs/requirements/`, then generate on-standard prompts + a planning log. | `/forge-plan-phase`        |
| **forge-run**             | command | Execute the next eligible prompt(s) — one, N, or all — each in an isolated subagent.                  | `/forge-run [1\|N\|all]`   |
| **forge-run-phase**       | command | Execute a whole phase; each prompt runs in an isolated subagent (clean context).                      | `/forge-run-phase <n>`     |
| **forge-next**            | command | Execute only the next eligible prompt (safe, single-step mode).                                       | `/forge-next`              |
| **forge-status**          | command | Show suite progress (done/total), the next eligible prompt, and any blocked prompts. Read-only.      | `/forge-status`            |
| **forge-review**          | command | Run the independent `reviewer` subagent over a diff/branch/commit before integrating. Read-only.     | `/forge-review [<scope>]`  |
| **forge-sync-docs**       | command | Regenerate derived docs (STATUS, traceability, changelog) + any declared stack `docsHooks`.          | `/forge-sync-docs`         |
| **forge-add-requirement** | command | Add/alter a requirement in `docs/requirements/` (the only sanctioned way) and propagate the matrix.  | `/forge-add-requirement`   |
| **forge-new-feature**     | command | Scaffold a feature — runs the project's declared generator, or emits a stack-agnostic checklist.     | `/forge-new-feature <name>`|
| **forge-new-module**      | command | Scaffold a module (modular projects only) — declared generator or stack-agnostic checklist.          | `/forge-new-module <name>` |

**Subagents** (invoked via the skills above, usually not directly): `reviewer`
(quality/conformance, read-only) and `docs-sync` (derived-doc sync).

## Recommended flows

- **Start a project:** `/forge-init` → review the seeded roadmap →
  `/forge-plan-phase` for the first phase → `/forge-run-phase 1`.
- **Plan and build something new:** `/forge-plan-phase` → review the plan →
  `/forge-run-phase <n>` → `/forge-review`.
- **Continue existing work:** `/forge-status` → `/forge-run-phase <n>` (or
  `/forge-next`) → `/forge-review`.
- **Change a requirement:** `/forge-add-requirement` (keeps
  `docs/requirements/` and the matrix coherent) → plan/implement.
- **Add a new area/module (modular projects):** `/forge-new-module <name>` →
  fill its requirement doc → `/forge-plan-phase` for its prompts.

## Global rule — an unstructured request? Ask, then offer the skills

When a developer sends an **unstructured** request (vague, broad, or one that
maps to a skill above), the agent does **not** start executing immediately. It
first **asks** what the developer wants and offers two options: **(a)** continue
with the free-form request, or **(b)** use a skill. Only **after asking**, if the
developer chooses a skill (or is unsure), the agent shows this catalog with
"when to use" / "how to call" and helps pick the right one. If the developer
chooses to continue free-form, the agent proceeds while honoring the
non-negotiable principles in [`FORGE.md`](../../FORGE.md). The agent never lists
the skills before asking. (This rule belongs in the root
[`AGENTS.md`](../../AGENTS.md).)

## Authoring a new skill/command

1. Simple command: `.claude/commands/<name>.md` with frontmatter `description`,
   `argument-hint` (if it takes an argument) and `allowed-tools`.
2. Skill with support files / auto-suggestion: `.claude/skills/<name>/SKILL.md`
   with frontmatter `name` and a `description` that says clearly **when** to use
   it.
3. Body in the project's docs language, self-contained, referencing
   `docs/requirements/` and the standards (`templates/prompt.template.md`,
   `prompts/README.md` §5). **Read the stack/conventions/ci/critical-paths from
   `forge.config.json`** — never hardcode a stack or domain.
4. Add the item to the root `AGENTS.md` catalog and to this guide.
5. Any skill that changes scope/requirements must **update the source of truth**
   (via `/forge-add-requirement`) before code follows.
