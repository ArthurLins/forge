# Contribution log — 2026-06-18

**Work item:** `S0.2` (phase S0 — Self-hosting infrastructure)
**Command:** `/forge-contribute` (maintainer / solo mode → direct commit)
**Area:** tool/generator — `tools/forge_tools/export.py` (self-only)
**Touches:** `FR-S18` (clean export), `ADR-S2` (distribution boundary + clean export)

## Proposal

`make forge-export DEST=<dir>` produced an adopter copy with two defects that
made a fresh export internally inconsistent:

1. **Dead Make targets.** The copied `Makefile` still carried the self-only
   targets `forge-selfcheck`, `forge-selfcheck-report` and `forge-export` (plus
   their `help`/`@echo` lines). Those invoke `selfcheck.py` / `export.py`, which
   are excluded from the export (`forge.manifest.json → selfOnly`) → broken
   targets for an adopter.
2. **Not docs-fresh.** `resetOnExport` empties `docs/generated/` to a `.gitkeep`,
   so running `make forge-sync-docs-check` in a fresh export FAILED immediately
   (missing `traceability.md` / `CHANGELOG.md`).

**Fix (minimal, confined to `export.py`):**

- `_strip_self_only_makefile_targets(dest)` — post-process the copied `Makefile`:
  drop the "Self-hosting (self-only …)" help block (header echo + per-target
  `@echo` lines + the blank `@echo ""` that opened it) and the
  `# --- self-hosting (self-only) --- #` section (marker → EOF), which holds the
  three target definitions.
- `_seed_fresh_derived_docs(dest)` — run the stack-neutral core generators
  (`forge_tools.sync_docs`) inside DEST with `FORGE_ROOT=DEST`, writing the
  baseline `docs/generated/*` and `prompts/STATUS.md` for the empty-seed state so
  `forge-sync-docs-check` passes.

**Implementation note (simpler than the suggested git-init path).** The task
suggested `git init` + an initial commit so the changelog generator (which reads
`git log`) has a repo. Verified that the changelog generator already *tolerates*
a non-repo directory: `subprocess.run(["git","log",…])` returns a non-zero exit
with empty stdout, yielding "_No commits in history yet._". So the export needs
**no** `git init` — running the generators directly is enough, leaves no `.git`
in the adopter copy, and is more adopter-friendly. Verified end to end (below).

## Constitution check (FORGE.md)

- **Stack-neutral:** Python 3 only; git-independent; no stack assumed. PASS.
- **Domain-agnostic:** no domain tokens introduced. PASS.
- **English:** all code/comments English. PASS.
- **Derived-docs-as-code:** the fix *produces* derived docs via the canonical
  generators; it never hand-edits them. PASS.
- **Root seeds untouched:** root `prompts/state.json` stays the empty seed and
  `docs/requirements/` stays `.gitkeep`; only the self-only `export.py` changed.
  PASS.
- **Minimal:** single self-only file edited (plus the required `self/` records).
  PASS.

**Result: PASS — no principle violated.** Explicit human confirmation: granted
(maintainer approved this fix in the task brief).

## Gate + verification

- `make forge-selfcheck` → PASS (hard checks green; docs fresh).
- `make forge-export DEST=/tmp/fx2`, then in `/tmp/fx2`:
  - `grep -E 'forge-selfcheck|forge-export' Makefile` → no matches.
  - `make forge-sync-docs-check` → exit 0.
- `/tmp/fx2` deleted after verification.

## Outcome

- Landed as one Conventional Commit
  `fix(forge-export): adopter copy has no dead targets and is docs-fresh`
  on `main` (maintainer mode, direct commit). Commit: `de25e72`.
- `make forge-selfcheck` clean post-commit; working tree clean; not pushed.
- Work item `S0.2` marked `done`; self STATUS regenerated.

## Negative demonstration (gate has teeth)

Injected a constitution-violating change (domain token `LGPD` in a distributable
file), ran `make forge-selfcheck` → it FAILED on `domain-residue` (exit ≠ 0), then
reverted with `git checkout --` — proving `/forge-contribute` would not land a red
change. No residue left.
