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

### `claims` (object) — OPTIONAL

Tunes the **sharded-claim** lifecycle that keeps parallel prompt execution safe
(see [`docs/guides/teams.md`](docs/guides/teams.md) §2). Both fields are
optional; **absent = the defaults below**. Read by the prompt selector
(`prompts/next_prompt.py`) and by `forge-validate`. Stack-neutral.

| Field         | Type   | Default | Meaning                                                                                                  |
| ------------- | ------ | ------- | -------------------------------------------------------------------------------------------------------- |
| `ttlSeconds`  | number | `1800`  | Heartbeat TTL. A claim whose `heartbeatAt` is older than this is **expired**: the selector ignores it (the prompt is eligible again — self-healing for a crashed worker), and `forge-validate` warns. A claim with **no** `heartbeatAt` is never auto-released. |
| `maxAttempts` | number | `3`     | Failed-attempt budget. The orchestrator increments a claim's `attempts` on each failure; after this many it sets the prompt's `status` to `blocked`. `forge-validate` warns on an over-`maxAttempts` claim that is not yet `blocked`. |
| `maxConcurrent` | number | `0` (unlimited) | **WIP limit** — a non-negative integer cap on how many ACTIVE (non-expired) claims may exist at once, i.e. how many prompts the orchestrator runs in parallel. Absent or `0` = unlimited (today's behavior). Bounded WIP keeps the merge queue short and feedback fast. The orchestration commands hold at most this many in-flight claims; `forge-validate` warns (never fails) when the active-claim count exceeds it. Stack-neutral. |

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
| `tagAliases` | object   | `{"requirement":["requirement","req"],"rule":["rule","businessRule"],"convention":["convention","conv"]}`  | Maps a **link kind** to the tag keywords that record it. `requirement` links a requirement id (`FR`/`NFR`/`CR`/`UC`/`EN`); `rule` links a business rule (`BR`); `convention` links an engineering convention (`EC`) from the [Conventions Map](#the-conventions-map-ec-tag). Project-declared aliases are **merged on top of** the defaults, so adding an alias never drops the built-in ones. |

> A generalization of stack-specific, hardcoded tag conventions (such as
> `@requirement RFxx` / `@businessRule RNxx`). In Forge the tag keywords and the
> scanned globs are config, not code.

#### The Conventions Map (`EC`) tag

The `convention` alias (default `@convention` / `@conv`) recognizes tags that
link honoring code/tests to an **engineering convention** (`EC-xx`) from the
project's **Conventions Map** (`docs/requirements/conventions.md`). This is
**lightweight traceability only — NOT a hard gate**: an `EC` with no
`@convention` tag is **not** reported as a coverage gap, because the Conventions
Map is not the requirements matrix. The Conventions Map's real enforcement is the
two teeth described in its template — applicable `EC` rules injected into every
feature-building prompt's context, and the [`reviewer`](../.claude/agents/reviewer.md)
subagent's `EC`-compliance dimension. The tag merely lets a project that wants it
record *which* features honored *which* convention. Neutral default: the alias is
recognized, but no project is required to use it.

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
> fill in your stack's commands. An API-contract build and a generated typed API
> client are exactly the kind of step that becomes a hook here instead of being
> hardcoded.

### `ci` (object)

The continuous-integration profile.

| Field              | Type    | Default | Meaning                                                           |
| ------------------ | ------- | ------- | ----------------------------------------------------------------- |
| `provider`         | string  | `""`    | The CI provider/platform. Empty until set.                        |
| `strictValidation` | boolean | `false` | When `true`, the project opts into a **required static-integrity check** in CI: a PR merges only if `forge-validate` passes (the project's prompt state machine, requirement tags, Conventions Map, config and derived docs are all intact). Selected at `/forge-init`; when on, genesis installs `templates/ci/forge-validate.yml.template` and the developer marks that check **required** in branch protection. Default `false` (off). |
| `commands`         | object  | —       | Shell commands for the gates. Filled by genesis / the CI step.    |

`ci.commands` fields:

| Field       | Default                     | Meaning                                                       |
| ----------- | --------------------------- | ------------------------------------------------------------- |
| `lint`      | `""`                        | Lint command (incl. any boundary/format rules).               |
| `typecheck` | `""`                        | Type-check command.                                           |
| `test`      | `""`                        | Test command (incl. critical paths).                          |
| `build`     | `""`                        | Build command.                                                |
| `docsCheck` | `""`                        | Docs-freshness gate (defaults to the Forge sync-docs check).  |
| `validate`  | `"make forge-validate-check"` | The static-integrity gate run when `strictValidation` is `true`. The shipped default invokes `forge-validate` via the Makefile; a project may override it (e.g. with the direct `PYTHONPATH=tools python3 -m forge_tools validate --check` invocation). |

## Defaults shipped by the placeholder

- **No stack** is assumed (`stack.*` null / empty).
- **No compliance** regimes (`compliance.regimes: []`).
- **No critical paths** (`criticalPaths.paths: []`).
- **No stack docs hooks** (`docsHooks: []`) — `sync-docs` runs the core
  generators only until a project declares one.
- `docs.generatedDir` is `docs/generated`; `traceability.globs` /
  `traceability.tagAliases` carry stack-neutral defaults.
- `requirementTiers.selected` is empty until genesis chooses a tier.
- **No `claims` overrides** — the claim TTL (`1800s`) and attempt budget (`3`)
  use their built-in defaults, and the WIP limit is unlimited
  (`claims.maxConcurrent` absent/`0`), until a project sets `claims.ttlSeconds` /
  `claims.maxAttempts` / `claims.maxConcurrent`.
- Conventions default to English docs/code and Forge's casing rules.
