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
- `requirementTiers.selected` is empty until genesis chooses a tier.
- Conventions default to English docs/code and Forge's casing rules.
