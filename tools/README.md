# Forge tools — derived docs as code

This folder holds the generators that make **"derived docs are code"**
([FORGE.md](../FORGE.md), Principle 6) real: STATUS, the traceability matrix and
the changelog are **generated**, committed, and **CI fails if they are stale**.
Humans edit the *source* (requirements, `state.json`, commits); the generators
are the only writers of the output.

## Runtime: Python 3 (and why)

The generators are a small Python package, `forge_tools/`. Python 3 is chosen
because:

- The prompt-suite engine already requires it (`prompts/next_prompt.py`), so
  Forge adds **no extra toolchain** just to regenerate docs.
- It is **stack-neutral**: the generators run on a fresh checkout with **no
  project stack present** (no Node, no compiler, nothing installed).
- Forge never assumes a stack. Stack-specific derived docs (e.g. an OpenAPI
  build) are **not** baked in here — a project declares them as
  [`docsHooks`](../forge.config.schema.md#docshooks-array--optional-stack-plugins)
  in `forge.config.json`, and the orchestrator runs them after the core.

> If a project's declared toolchain is Node, it may still add Node-based derived
> docs — as a `docsHooks` entry — without changing these core generators.

## The generators

| Tool                       | Reads                                    | Writes                              |
| -------------------------- | ---------------------------------------- | ----------------------------------- |
| `forge_tools/status.py`    | `prompts/state.json`                     | `prompts/STATUS.md`                 |
| `forge_tools/traceability.py` | `@requirement`/`@rule` tags in source + `docs/requirements/` | `<generatedDir>/traceability.md` |
| `forge_tools/changelog.py` | git history (Conventional Commits, SemVer tags) | `<generatedDir>/CHANGELOG.md`   |
| `forge_tools/sync_docs.py` | the above + `forge.config.json → docsHooks` | all of the above (orchestrated)  |

`<generatedDir>` is `forge.config.json → docs.generatedDir` (default
`docs/generated`). Shared helpers (config loading, repo-root discovery, the
`--check`/diff machinery) live in `forge_tools/common.py`.

Every generator supports a **`--check`** mode: it re-derives the artifact and,
instead of writing, compares it to what is on disk — exiting non-zero **and
printing a unified diff** when they differ. That is the CI docs-freshness gate.

## Task runner

A [`Makefile`](../Makefile) at the repo root exposes the tasks (a `Makefile` is
runtime-agnostic; `package.json` scripts are used only when a project declares a
Node toolchain). Targets:

| Task                          | Does                                                          |
| ----------------------------- | ------------------------------------------------------------ |
| `make forge-status`           | regenerate `prompts/STATUS.md`                               |
| `make forge-traceability`     | regenerate the traceability matrix                          |
| `make forge-changelog`        | regenerate the changelog                                    |
| `make forge-sync-docs`        | run all core generators **+** any declared stack hooks      |
| `make forge-docs-gen`         | core text artifacts only (skip hooks) — the "docs-gen" subset |
| `make forge-<task>-check`     | the `--check` variant of any of the above (also `forge-<task>:check`) |
| `make forge-sync-docs-check`  | fail on **any** drift — the CI docs-freshness gate          |

Equivalently, run a generator directly (no install step):

```bash
PYTHONPATH=tools python3 -m forge_tools sync-docs          # regenerate all
PYTHONPATH=tools python3 -m forge_tools sync-docs --check   # CI: fail on drift
PYTHONPATH=tools python3 -m forge_tools status              # one generator
PYTHONPATH=tools python3 -m forge_tools traceability --out docs/generated/traceability.md
```

## Traceability tags

A generalization of stack-specific tag conventions (such as `@requirement RFxx` /
`@businessRule RNxx`) to the Forge ID taxonomy (`FR`/`NFR`/`BR`/`CR`/`UC`/`EN`):

- `@requirement <ID>` — links a requirement (e.g. `@requirement FR01`).
- `@rule <ID>` (alias `@businessRule <ID>`) — links a business rule
  (e.g. `@rule BR03`).

The accepted keywords and the scanned source globs are **config**, not code —
see `forge.config.json → traceability.{globs,tagAliases}`. A tag pointing at an
**undeclared** requirement is reported as a gap in the matrix.

## `docs-gen` vs full `sync-docs`

Forge separates the **text artifacts** (status, traceability, changelog — always
runnable, no stack) from the **full sync** (text artifacts **plus** the project's
stack hooks):

- `make forge-docs-gen` → core text artifacts only (`--core-only`).
- `make forge-sync-docs` → core **+** declared `docsHooks`.

With no `docsHooks` declared, the two are equivalent and both succeed with no
stack present.

## Self-hosting tools (self-only)

These two tools maintain **Forge itself** and are **not** shipped to adopters
(`forge.manifest.json → selfOnly`). They run on Python 3 alone, like the
generators above.

| Tool                       | Reads                                       | Does                                                |
| -------------------------- | ------------------------------------------- | --------------------------------------------------- |
| `forge_tools/selfcheck.py` | `forge.manifest.json` + the framework files | assert Forge's constitution (seed-purity, registration-parity, domain-residue, stack-residue warnings, manifest-coverage, skill-structure). |
| `forge_tools/export.py`    | `forge.manifest.json` + git-tracked files   | produce a **clean adopter copy** of Forge: tracked files minus `selfOnly`, with the root seeds reset. |

### `make forge-selfcheck` — the constitution gate

| Task                          | Does                                                              |
| ----------------------------- | ---------------------------------------------------------------- |
| `make forge-selfcheck`        | run `selfcheck --check` **and** `forge-sync-docs-check` — the full gate (invariants + docs-fresh). **Fails** on any hard violation or doc drift; **warnings never fail**. |
| `make forge-selfcheck-report` | run `selfcheck` without `--check` — a human-readable PASS/FAIL report that **never fails** (for inspection while iterating). |

The hard checks: **seed-purity** (root `prompts/state.json` empty,
`docs/requirements/` only `.gitkeep`), **registration-parity** (every
distributable skill/command is in both `AGENTS.md` and the skills catalog;
self-only ones are exempt), **domain-residue** (no business-domain tokens in
distributable files), **manifest-coverage** (no stale `selfOnly` entry), and
**skill-structure** (required frontmatter present). The soft tier,
**stack-residue**, reports hardcoded stack tokens as **warnings** to review (they
may be legitimate commented examples) and never fails the build.

### `make forge-export DEST=<dir>` — clean adopter copy

Copies all git-tracked files **except** `selfOnly` into `DEST`, then applies
`resetOnExport` (empty `prompts/state.json`, `docs/requirements/` → only
`.gitkeep`, `docs/generated/` emptied) and prints an included/excluded summary.
One command yields a clean Forge for a new project — **no copy-paste**.

```bash
make forge-export DEST=/path/to/new-project
# or directly:
PYTHONPATH=tools python3 -m forge_tools export --dest /path/to/new-project
```
