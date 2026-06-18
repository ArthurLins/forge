---
description: Run the independent `reviewer` subagent over a diff, branch, or commit of a Forge-built project, then write its APPROVED/REJECTED report to prompts/.logs/review-<scope>.md. Read-only — it points out issues, it does not fix them.
argument-hint: '[<commit | range | branch>]  (default: working tree / current branch)'
allowed-tools: Task, Bash, Read, Glob, Grep
---

# `/forge-review` — independent review of a change set

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Run the
**`reviewer`** subagent (read-only) over a change set and surface its verdict —
**APPROVED** or **REJECTED** — with the items to fix. Use it before integrating a
prompt's work, or on any diff/branch/commit that must respect the project's
boundaries, critical paths, and conformance.

This command upholds **Principle 5 — "Agents are orchestrated in isolation"**
([`FORGE.md`](../FORGE.md)): the review runs in a **clean subagent**, so only the
verdict and findings return to this thread. Review is **read-only** — to fix
findings, reopen the prompt and run `/forge-next` (or `/forge-run-phase`).

**Review target:** `$ARGUMENTS` — a commit hash, a commit range, or a branch. If
empty, review the **working tree / current branch**.

## Precondition

The `reviewer` subagent exists at `.claude/agents/reviewer.md`. If it is missing,
run the review with a general-purpose subagent following the same criteria
(boundaries / critical-path tests / `@requirement` tags / compliance / standards),
reading every knob from `forge.config.json` and `docs/requirements/`.

## Procedure

1. **Resolve the target.**
   - `$ARGUMENTS` is a commit/range → the subagent uses `git show <commit>` /
     `git diff <range>`.
   - `$ARGUMENTS` is a branch → diff it against the default branch.
   - Empty → the working tree / current branch (`git status`, `git diff`,
     `git diff --staged`).
   - Compute a short **`<scope>`** slug for the log file name (e.g. the short
     commit hash, the branch name, or `worktree`).

2. **Delegate to the `reviewer` subagent** (the `Task` tool, subagent type
   `reviewer`) with this self-contained instruction:

   > You are the independent **reviewer** in a Forge-built repository, with a
   > **clean context** and **read-only**. Review the change set **<target>** (a
   > commit/range/branch, or the working tree if none was given). First read
   > `forge.config.json` (and `forge.config.schema.md`) and the pertinent
   > `docs/requirements/` to learn **this** project's module boundaries
   > (`modularity.md`, if modular), critical paths (`forge.config.json →
   > criticalPaths.paths`), compliance regimes (`compliance.regimes`), CI gate
   > commands (`ci.commands.*`), traceability tag aliases, and standards. Then
   > emit a verdict **APPROVED** or **REJECTED**, rejecting on: module-boundary
   > violations (**only if** boundaries are declared); a touched critical path
   > with no passing test (**only if** `criticalPaths.paths` is non-empty);
   > missing `@requirement` tags in code **and** tests; violations of the
   > **declared** compliance requirements (**only if** `compliance.regimes` is
   > non-empty); standards deviations (type strictness / naming / lint / format /
   > Conventional Commits) as configured. **Skip any check the project has not
   > configured** and say so. Run only the `ci.commands.*` gates that are
   > non-empty. Do **not** modify code or invent requirements. Return: the
   > verdict; one line listing which checks were applied vs. skipped-because-
   > unconfigured; a 1–2 sentence summary; and a findings list (category,
   > `file:line`, problem, suggested fix, severity). Any blocking finding ⇒
   > REJECTED.

3. **Write the report** to `prompts/.logs/review-<scope>.md` (create
   `prompts/.logs/` if needed): the verdict, the applied/skipped checks, the
   summary, the findings table, and the commands the reviewer ran. Print the
   verdict and a short findings summary to this thread.

4. **If REJECTED**, list the recommended actions (e.g. reopen the prompt as
   `in_progress` and fix via `/forge-run-phase` / `/forge-next`). Do **not** apply
   any fix here.

## Notes

- **Read-only & isolated:** the reviewer never edits code; only its report
  returns, keeping this thread lean.
- **Stack-neutral & project-driven:** boundaries, critical paths, compliance, the
  gate commands and the standards all come from `forge.config.json` and
  `docs/requirements/`. Checks the project did not configure are **skipped**, not
  failed. No tool, domain, or compliance regime is hardcoded here.
- Never remove `docs/requirements/` or `prompts/`.
