# `forge.config.json` — schema reference

The **stack profile** for a Forge project. It is the single place that records
*what this project is built with and how it is run*. Every Forge skill and tool
**reads this file** instead of hardcoding a stack — that is how Forge stays
stack-neutral.

The repository ships a **placeholder** with neutral defaults (no stack assumed,
compliance and critical paths empty). The genesis interview
(**`/forge-init`**) fills it and records a corresponding **Stack ADR** in
`docs/requirements/`. Keys beginning with `_comment` are documentation hints and
may be deleted once the file is filled.

## Fields

### `forgeVersion` (string)

The Forge schema version this config targets. Starts at `"0"`.

### `project` (object)

| Field     | Type   | Filled by | Meaning                                   |
| --------- | ------ | --------- | ----------------------------------------- |
| `name`    | string | genesis   | Human-readable project name.              |
| `purpose` | string | genesis   | One-line description of what it does.     |

### `stack` (object) — all fields optional / nullable

A project may use **none, some, or all** of these. Leave a field `null` (or the
array empty) when it does not apply.

| Field           | Type            | Example values (illustrative only)              |
| --------------- | --------------- | ----------------------------------------------- |
| `language`      | string \| null  | the primary programming language                |
| `runtime`       | string \| null  | the execution runtime / platform                |
| `frameworks`    | string[]        | application/UI/server frameworks in use          |
| `datastore`     | string \| null  | the primary data store                          |
| `packageManager`| string \| null  | the dependency manager                          |
| `monorepoTool`  | string \| null  | the monorepo/build orchestrator, if any          |

> The examples column is intentionally abstract. Forge never prescribes a
> stack; genesis writes whatever the project chooses.

### `conventions` (object)

Casing and process conventions. Defaults are Forge's own and may be overridden.

| Field             | Type   | Default              | Meaning                                  |
| ----------------- | ------ | -------------------- | ---------------------------------------- |
| `fileCasing`      | string | `kebab-case`         | Casing for file names.                   |
| `typeCasing`      | string | `PascalCase`         | Casing for types/classes.                |
| `identifierCasing`| string | `camelCase`          | Casing for variables/functions.          |
| `constantCasing`  | string | `UPPER_SNAKE_CASE`   | Casing for constants.                    |
| `commitStyle`     | string | `conventional`       | Commit-message convention.               |
| `docsLanguage`    | string | `en`                 | Language of docs and UI text.            |
| `codeLanguage`    | string | `en`                 | Language of code identifiers/symbols.    |

### `requirementTiers` (object)

The **spec weight** genesis used, so the depth of the source of truth scales
with project size.

| Field       | Type     | Meaning                                              |
| ----------- | -------- | ---------------------------------------------------- |
| `selected`  | string   | One of `lean` \| `standard` \| `full`. Empty until chosen. |
| `available` | string[] | The tiers Forge offers (`lean`, `standard`, `full`). |

### `compliance` (object)

| Field     | Type     | Default | Meaning                                                    |
| --------- | -------- | ------- | ---------------------------------------------------------- |
| `regimes` | string[] | `[]`    | Compliance regimes this project must honor. **None** by default. |

### `criticalPaths` (object)

| Field   | Type     | Default | Meaning                                                       |
| ------- | -------- | ------- | ------------------------------------------------------------- |
| `paths` | string[] | `[]`    | Named flows that **must** be covered by tests (gated by the DoD). **None** by default. |

### `docs` (object)

Where the derived-docs generators write their output.

| Field          | Type   | Default          | Meaning                                                      |
| -------------- | ------ | ---------------- | ------------------------------------------------------------ |
| `generatedDir` | string | `docs/generated` | Directory for generated artifacts (traceability matrix, changelog, and any stack-hook output). Committed and CI-checked. |

### `traceability` (object)

Knobs for the traceability generator (`tools/forge_tools/traceability.py`).

| Field        | Type     | Default                                                                 | Meaning                                                                                       |
| ------------ | -------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `globs`      | string[] | `["apps/**/*","libs/**/*","src/**/*","packages/**/*","modules/**/*","examples/**/*"]` | Repo-relative source patterns scanned for tags. `**` is recursive; `*` does not cross `/`. The defaults are the conventional locations a project's **own** source lives; Forge's framework folders (`templates/`, `tools/`, `docs/`) are excluded so tag *examples* in Forge's prose are not picked up. |
| `tagAliases` | object   | `{"requirement":["requirement","req"],"rule":["rule","businessRule"]}`  | Maps a **link kind** to the tag keywords that record it. `requirement` links a requirement id (`FR`/`NFR`/`CR`/`UC`/`EN`); `rule` links a business rule (`BR`). Project-declared aliases are **merged on top of** the defaults, so adding an alias never drops the built-in ones. |

> Generalized from PedPlus's hardcoded `@requirement RFxx` / `@businessRule
> RNxx`. In Forge the tag keywords and the scanned globs are config, not code.

### `docsHooks` (array) — OPTIONAL stack plugins

The **extension point** that keeps `sync-docs` stack-neutral. The core
generators (status, traceability, changelog) always run; **stack-specific**
derived docs (e.g. building an OpenAPI contract or regenerating a typed API
client) are declared here as shell commands and run by `forge-sync-docs`
**after** the core. With `docsHooks: []` (the default) the orchestrator runs
the core only and still succeeds — so Forge never assumes a stack.

Each entry:

| Field     | Type   | Required | Meaning                                                                                   |
| --------- | ------ | -------- | ----------------------------------------------------------------------------------------- |
| `name`    | string | yes      | Label shown in logs.                                                                      |
| `command` | string | yes      | Shell command that **regenerates** the artifact (run in normal mode).                     |
| `check`   | string | no       | Shell command run in `--check` mode that must fail if the committed artifact is stale. If omitted, `--check` re-runs `command` (idempotent generators leave the tree unchanged when fresh). |
| `cwd`     | string | no       | Working directory for the command, relative to the repo root. Defaults to the repo root.  |

> `_docsHooksExample` in the shipped config is an inert documentation block
> (note the leading underscore): copy an entry from it into `docsHooks[]` and
> fill in your stack's commands. PedPlus's OpenAPI build and Hey-API client
> generation are exactly the kind of step that becomes a hook here instead of
> being hardcoded.

### `ci` (object)

The continuous-integration profile.

| Field      | Type   | Meaning                                                           |
| ---------- | ------ | ----------------------------------------------------------------- |
| `provider` | string | The CI provider/platform. Empty until set.                        |
| `commands` | object | Shell commands for the gates: `lint`, `typecheck`, `test`, `build`, `docsCheck`. Filled by genesis / the CI step. |

## Defaults shipped by the placeholder

- **No stack** is assumed (`stack.*` null / empty).
- **No compliance** regimes (`compliance.regimes: []`).
- **No critical paths** (`criticalPaths.paths: []`).
- **No stack docs hooks** (`docsHooks: []`) — `sync-docs` runs the core
  generators only until a project declares one.
- `docs.generatedDir` is `docs/generated`; `traceability.globs` /
  `traceability.tagAliases` carry stack-neutral defaults.
- `requirementTiers.selected` is empty until genesis chooses a tier.
- Conventions default to English docs/code and Forge's casing rules.
