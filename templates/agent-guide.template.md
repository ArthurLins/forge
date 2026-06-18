<!--
  Forge — layered agent-guide template.

  Copy this file to create an `AGENTS.md` at any layer of the project:
    - the repository root (the highest layer), and
    - one inside each major area (e.g. each app, package, or module).

  Each guide points to the layer below it and inherits the layers above it.
  Replace every {{PLACEHOLDER}} with project-specific content. Delete the
  guidance comments (<!-- ... -->) once filled. Keep it short — a guide is a
  map, not a manual. Values that describe the stack come from
  `forge.config.json`; do not hardcode a stack that contradicts the profile.
-->

# AGENTS.md — {{LAYER_NAME}}

<!-- For a non-root guide, link up to the parent guide first: -->
> Read the [parent guide]({{PARENT_GUIDE_PATH}}) first. Source of truth:
> [`docs/requirements/`]({{REQUIREMENTS_PATH}}). Stack profile:
> [`forge.config.json`]({{FORGE_CONFIG_PATH}}).

## What this is

{{PROJECT_OR_LAYER_PURPOSE}}

<!--
  Root layer: one paragraph on what the whole project is and the problem it
  solves. Area layer: the role of THIS app/package/module and what must NOT
  live here (its boundaries).
-->

## The stack (from `forge.config.json`)

<!-- Summarize only — the config is authoritative. Omit fields the project
     does not use. -->

| Aspect          | Value                          |
| --------------- | ------------------------------ |
| Language        | {{STACK_LANGUAGE}}             |
| Runtime         | {{STACK_RUNTIME}}              |
| Frameworks      | {{STACK_FRAMEWORKS}}           |
| Datastore       | {{STACK_DATASTORE}}            |
| Package manager | {{STACK_PACKAGE_MANAGER}}      |
| Monorepo tool   | {{STACK_MONOREPO_TOOL}}        |

## Source of truth

The **only** source of truth for requirements is
[`docs/requirements/`]({{REQUIREMENTS_PATH}}). **Never invent requirements.**
Before coding, read the documents referenced by the prompt/task. Start at the
index: [`{{REQUIREMENTS_INDEX}}`]({{REQUIREMENTS_INDEX}}).

{{KEY_REQUIREMENT_DOCS_TABLE}}
<!-- Optional: a small table mapping requirement docs to their subject. -->

## Non-negotiable rules

<!-- The rules an agent must never break at this layer. Generalize, do not
     invent. Typical entries: -->

1. **Respect the boundaries.** {{BOUNDARY_RULES}}
2. **Do not invent requirements.** If it is not in `docs/requirements/`, stop and
   record the gap — do not fill it in.
3. **Conventions are enforced.** {{TYPE_SAFETY_OR_STYLE_RULE}}
4. **Critical paths are tested.** {{CRITICAL_PATH_RULE}}
5. **Traceability.** Add `@requirement {{ID_PREFIX}}xx` tags in code **and**
   tests that implement a requirement; the matrix is generated from them.
6. **Conventional Commits**, validated in CI.
7. **Sync derived docs** before finishing (see the sync skill).
8. **Update the tracking** (`prompts/state.json`) when a prompt is done.

## How to find the next work

The build is guided by a suite of self-contained prompts:

- Roadmap: [`{{ROADMAP_PATH}}`]({{ROADMAP_PATH}})
- Current progress: [`{{STATUS_PATH}}`]({{STATUS_PATH}}) (generated)
- Next eligible prompt: `{{NEXT_PROMPT_COMMAND}}`
- The **Definition of Done** is in [`{{DOD_PATH}}`]({{DOD_PATH}}).

## Skills catalog

<!-- List the skills/commands available, with "when to use" and "how to call".
     Always prefer a skill over a manual procedure — it keeps the standard. -->

| Skill / command       | When to use            | How to call             |
| --------------------- | ---------------------- | ----------------------- |
| {{SKILL_NAME}}        | {{SKILL_WHEN}}         | {{SKILL_INVOCATION}}    |

## Language & naming conventions

- **{{DOCS_UI_LANGUAGE}}** in documentation and UI text.
- **English** in code: identifiers, file names, and symbols.
- File names in {{FILE_CASING}}; types/classes in {{TYPE_CASING}};
  variables/functions in {{VAR_CASING}}; constants in {{CONST_CASING}}.

## Definition of Done (this layer)

<!-- What "done" means HERE, on top of the consolidated DoD. Keep it concrete. -->

- {{LAYER_DOD_ITEM_1}}
- {{LAYER_DOD_ITEM_2}}
