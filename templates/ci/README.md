# Forge — CI gate template

This folder holds the **CI gate** Forge installs into a project. It is a
**template** (not a live workflow): nothing about a specific toolchain is
hardcoded. The gate's commands and provider come from
[`forge.config.json`](../../forge.config.json); the same file the rest of Forge
reads.

| File                                | What it is                                                        |
| ----------------------------------- | ----------------------------------------------------------------- |
| `forge-ci.yml.template`             | The CI workflow (default: GitHub Actions) — three jobs.           |
| `commitlint.config.template.md`     | Spec + illustrative config for the Conventional-Commits checker.  |
| `README.md`                         | This guide.                                                       |

## The three jobs

The template enforces three of Forge's principles as CI gates:

| Job              | Enforces                                            | Forge principle |
| ---------------- | --------------------------------------------------- | --------------- |
| **commits**      | Conventional Commits on every PR commit message.    | 8 (layered guidance / conventions) |
| **quality**      | lint · type-check · test · build.                   | the Definition of Done's quality gates |
| **docs-freshness** | derived docs are fresh (`forge-sync-docs --check`). | 6 (derived docs are code) |

## How instantiation works (genesis / CI setup)

The CI step of `/forge-init` (or a later setup) instantiates the template:

1. **Copy** `forge-ci.yml.template` to the path your provider expects. For the
   default GitHub Actions provider that is `.github/workflows/ci.yml`. If
   `forge.config.json → ci.provider` names a different platform, translate the
   **same three jobs** into that platform's syntax — the job *shape* is the
   contract, not the YAML dialect.
2. **Fill the placeholders** from `forge.config.json`:

   | Placeholder                    | Source                                              |
   | ------------------------------ | --------------------------------------------------- |
   | `{{DEFAULT_BRANCH}}`           | the repository's default branch (e.g. `main`).      |
   | `{{CI_COMMANDS_LINT}}`         | `ci.commands.lint`                                  |
   | `{{CI_COMMANDS_TYPECHECK}}`    | `ci.commands.typecheck`                             |
   | `{{CI_COMMANDS_TEST}}`         | `ci.commands.test`                                  |
   | `{{CI_COMMANDS_BUILD}}`        | `ci.commands.build`                                 |
   | `{{CI_COMMANDS_DOCSCHECK}}`    | `ci.commands.docsCheck` (defaults to the Forge sync-docs check) |
   | `{{COMMIT_LINT_COMMAND}}`      | the project's Conventional-Commits checker invocation |
   | `{{DOCS_GENERATED_DIR}}`       | `docs.generatedDir` (default `docs/generated`)      |
   | `{{TOOLCHAIN_SETUP}}`          | the setup/install steps for the stack in `forge.config.json` |

3. **Empty commands skip cleanly.** Each `quality` step is guarded by an
   `if:` that skips it when its command is the empty string. A project that has
   not yet defined, say, a type-check command still passes the job — the gate
   covers exactly the commands the project declared, no more.

## Why no toolchain is hardcoded

- The five quality commands are read from `ci.commands`, not written in the
  workflow. Toolchain names that appear in the template (Nx, Jest, Node, npm …)
  live **only in comments** as illustrative examples and must never be copied
  into the real commands.
- The **docs-freshness** gate runs the Forge sync-docs orchestrator in
  `--check` mode (Python 3 only — no project stack required). It re-derives
  `STATUS.md`, the traceability matrix and the changelog, **plus** any stack
  `docsHooks` the project declared, and fails on drift. See
  [`tools/README.md`](../../tools/README.md) and
  [`forge.config.schema.md`](../../forge.config.schema.md#docshooks-array--optional-stack-plugins).
- The **commits** gate calls the project's chosen checker; the message grammar
  it must enforce is specified in `commitlint.config.template.md`.

> A generalization of a typical CI shape (Conventional Commits + a quality gate +
> a docs-freshness gate); illustrative stack tooling such as `nx affected` is only
> an example. In Forge, the provider and every command are configuration, not code.
