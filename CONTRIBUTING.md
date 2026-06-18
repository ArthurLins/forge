# Contributing to Forge

**Forge is self-hosting.** It maintains itself *with* itself: a change to the
framework is scoped against the constitution ([`FORGE.md`](FORGE.md)), applied
minimally, gated by `forge-selfcheck`, and landed — so an update to Forge is, by
construction, already applied *to* Forge.

> **To improve Forge, run [`/forge-contribute`](.claude/commands/forge-contribute.md).**
> It is the single, meta-circular entry point: scope & propose → record → apply →
> **gate** (`forge-selfcheck`) → land → archive.

## The model: distributable framework + self-development workspace

Forge ships a **distributable framework** (what adopters copy) and keeps a
**self-development workspace** (used to maintain Forge, never shipped). The two are
separated by a manifest:

- **[`forge.manifest.json`](forge.manifest.json)** declares `selfOnly` — the paths
  excluded from the adopter export — and `resetOnExport` (the root seeds rebuilt on
  export). Everything not in `selfOnly` is distributable.
- **[`self/`](self/README.md)** is *Forge of Forge*: the framework's own
  requirements and improvement roadmap. The constitution is `FORGE.md`; `self/`
  records Forge's **capabilities** (`FR-S*`, in `self/requirements/functional.md`)
  and its **framework decisions** (`ADR-S*`, in `self/requirements/decisions.md`),
  plus the improvement roadmap engine in `self/prompts/`.

## How to improve Forge

1. Run **`/forge-contribute`** (add `--pr` for contributor mode). It:
   - reads the constitution + `self/requirements/`, classifies the change, and
     verifies it does **not** violate a principle — then **stops for your explicit
     confirmation before applying anything**;
   - records a work item in `self/prompts/state.json` and a contribution log;
   - applies the **minimal** change (registering a new distributable skill in
     **both** `AGENTS.md` and `docs/guides/skills-catalog.md`, which the gate
     enforces);
   - runs the gate `make forge-selfcheck` — **a red change never lands**;
   - lands it: **direct commit** to `main` (maintainer/solo) or a **draft PR**
     (`--pr` / non-maintainer);
   - archives the work item and finalizes the log.

You can also do these steps by hand, but `/forge-contribute` keeps the standard
and the self-development tracking consistent.

## The selfcheck gate (Forge's invariants)

`make forge-selfcheck` runs `tools/forge_tools/selfcheck.py` **and** the
docs-freshness check. It asserts Forge's constitution as automated checks:

| Check                 | Tier    | Enforces                                                              |
| --------------------- | ------- | -------------------------------------------------------------------- |
| **seed-purity**       | hard    | root `prompts/state.json` empty; `docs/requirements/` only `.gitkeep`. |
| **registration-parity** | hard  | every distributable skill/command is in **both** `AGENTS.md` and the skills catalog (self-only ones, e.g. `forge-contribute`, are exempt). |
| **domain-residue**    | hard    | no business-domain residue in distributable files.                   |
| **stack-residue**     | warning | hardcoded stack tokens flagged for review (never fail the build).    |
| **manifest-coverage** | hard    | every `manifest.selfOnly` path exists (no stale entry).              |
| **skill-structure**   | hard    | each skill/command has its required frontmatter.                     |
| **docs-freshness**    | hard    | derived docs (STATUS, traceability, changelog) are not stale.        |

Use `make forge-selfcheck-report` for a non-failing, human-readable view.

## Shipping a clean copy to a new project

```bash
make forge-export DEST=/path/to/new-project
```

This produces a **clean adopter copy** of Forge: every git-tracked file **except**
the `selfOnly` paths, with the root seeds reset (empty `prompts/state.json`,
`docs/requirements/` only `.gitkeep`, `docs/generated/` emptied). One command, **no
copy-paste**. The new project then runs `/forge-init` to seed its own source of
truth.

## Conventions

- **Conventional Commits** (validated by Forge's own CI).
- **English**, **stack-neutral**, **domain-agnostic** in all framework content —
  enforced by `forge-selfcheck`.
- Derived docs are **generated, never hand-edited** (`docs/generated/`,
  `prompts/STATUS.md`).

## CI

Forge's own CI — [`.github/workflows/forge-selfcheck.yml`](.github/workflows/forge-selfcheck.yml)
— runs `make forge-selfcheck` on pull requests and pushes to `main`. (This is
distinct from the adopter CI **template** in `templates/ci/`, which an adopter
project installs for *its* build.)
