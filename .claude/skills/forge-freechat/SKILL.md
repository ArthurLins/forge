---
name: forge-freechat
description: The fast lane for a quick, colloquial change — hotfixes, typos, a wrong color, a small copy or config tweak. The developer describes the change in plain language and the agent applies the SMALLEST safe edit, runs only the affected quality gates from forge.config.json, keeps derived docs and @requirement tags in sync, writes a short freechat log, and makes a Conventional Commit. It is NOT for new features or anything that needs a new/changed requirement or scope — those are refused and redirected to /forge-add-requirement or /forge-plan-phase. Use when someone says "just quickly change/fix X", "hotfix Y", "tweak Z" and it is clearly small and behavior-level.
---

# Skill: `/forge-freechat` — the safe fast lane for quick changes

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. A
developer wants a **quick, colloquial change** — a hotfix, a typo, a wrong color,
a small copy/config tweak — **without** the full ceremony of planning a phase and
writing a prompt. Your job is to apply the **smallest safe edit** that satisfies
the request, **fast**, while keeping the framework's safety net intact.

Forge is deliberately disciplined (spec → prompts → Definition of Done →
traceability). FreeChat is the pragmatic complement: a **fast lane** that still
respects the guardrails. It does **not** bypass **Principle 1 — "Source of truth
before code"** (`FORGE.md`): if a request actually needs a new or changed
requirement, scope, business rule, or data model, FreeChat **refuses the fast
lane and redirects** — it never quietly mutates the product's behavior contract.

> **Four hard rules, never broken.**
> 1. **Small & behavior-level only.** FreeChat is for changes that do **not**
>    add or alter a requirement, the scope, a business rule, the data model, or a
>    compliance obligation. If the request crosses that line → **stop** and
>    redirect to `/forge-add-requirement` (requirement/rule/data change) or
>    `/forge-plan-phase` (a feature/phase). See Step 2.
> 2. **Never ship broken.** The affected quality gates from
>    `forge.config.json → ci.commands` **must pass before you commit**. If a gate
>    fails and you cannot fix it within the same small scope, revert your edit and
>    report — do not commit a red change.
> 3. **Stay traceable.** Preserve (and, if the touched code's behavior shifts,
>    update) any `@requirement`/`@rule` tags; run `/forge-sync-docs` whenever a
>    derived doc could be affected; and always write the short **freechat log**.
> 4. **Minimal diff.** Make the **smallest** change that resolves the request.
>    No drive-by refactors, renames, or "while I'm here" cleanups.

This skill runs **in the current thread** (no orchestration subagent) — speed is
the point. For anything that is not a quick, contained fix, use the normal flow.

---

## Reference inputs (read what you need — all paths are repo-relative)

| Input | Path | Used to… |
| ----- | ---- | -------- |
| Stack profile | `forge.config.json` (+ `forge.config.schema.md`) | read the project's `ci.commands` (gates), `criticalPaths.paths`, `conventions` (commit style, casing) and `compliance.regimes` — **never hardcode a tool**. If the file is absent, degrade gracefully (apply the change, skip config-driven gates, and say so). |
| Definition of Done | `prompts/README.md` §5 | the full bar; FreeChat applies a **lightweight** subset of it (gates + tags + sync + commit). |
| Source of truth | `docs/requirements/` | only to **triage** in Step 2 (does this touch a requirement/rule/scope?). FreeChat does **not** edit these — that is what the redirect skills are for. |
| Docs-sync | `/forge-sync-docs` (or `make forge-sync-docs`) | regenerate derived docs if the change could affect them. |
| Redirect skills | `/forge-add-requirement`, `/forge-plan-phase` | where a non-trivial / scope-touching request must go instead. |

---

## The fast flow (keep it quick)

### Step 1 — Read the colloquial request

Take the developer's plain-language ask (it may be informal or terse, e.g. "the
footer year is wrong", "make the primary button blue", "bump the timeout to 30s",
"fix the typo on the login screen"). If it is genuinely ambiguous about **what**
or **where**, ask **one** sharp clarifying question — otherwise proceed. Do not
turn this into an interview; it is a fast lane.

### Step 2 — Triage (the safety net / refusal)

Before editing, classify the request. **Refuse the fast lane and redirect** if it
is any of these:

- It **adds or changes a feature/behavior** a user relies on, i.e. it would need a
  new or altered `FR`/`NFR`/`BR`/`CR`/`UC` → redirect to
  **`/forge-add-requirement`** (then `/forge-plan-phase` to build it).
- It **changes scope**, the **data model**, a **business rule**, or a
  **compliance** obligation (`forge.config.json → compliance.regimes`) → redirect
  to `/forge-add-requirement`.
- It is **large or cross-cutting** (touches many files/areas, or is really a small
  project of its own) → redirect to `/forge-plan-phase`.

Proceed on the fast lane only when the change is **small and behavior-preserving
or trivially corrective**: typos/copy, styling/visual tweaks, config/constant
adjustments, a localized bug fix, a dependency pin, a log message, etc.

> **If the change touches a critical path** (`forge.config.json →
> criticalPaths.paths`): you may still proceed, but treat it as load-bearing —
> run that path's tests (Step 4) and call it out explicitly in the report and log.
> When in doubt about a critical path, prefer redirecting.

State your verdict in one line ("This is a quick fix — proceeding" or "This needs
a requirement — here's why, use `/forge-add-requirement`") so the developer sees
the safety net working.

### Step 3 — Apply the smallest edit

Locate the spot and make the **minimal** change. Honor the project's
`conventions` (casing, language of UI vs code). Preserve any `@requirement`/
`@rule` tags on the touched code; if the change is a bug fix on tagged code, keep
the tag (and update its `@rule` note only if the rule's wording genuinely shifts —
if it does, that is a sign you should have redirected: re-check Step 2).

### Step 4 — Lightweight Definition of Done

Run only what the change touches (read commands from `forge.config.json →
ci.commands`; skip any that are empty/undeclared and say so):

- **Format / lint / type** on the changed files.
- **Tests:** the affected tests; **always** run the tests for any
  `criticalPaths.paths` the edit touches. If the change is behavioral, add or
  adjust the smallest test that locks the fix.
- **Derived docs:** if the change could affect a generated artifact (e.g. it adds
  a tagged line, or changes something the traceability/changelog reflects), run
  **`/forge-sync-docs`** and confirm `--check` is clean.

If any gate is red and the fix is outside this small scope → **revert and report**
(hard rule 2). Never commit a broken change.

### Step 5 — Commit (Conventional)

Make **one** Conventional Commit using the project's `conventions.commitStyle`,
with a type that matches the change: `fix:` (bug/hotfix), `style:` (visual/format),
`docs:` (copy/docs), `chore:` (config/deps), `perf:`, etc. Keep the subject short
and scoped. Reference the relevant requirement id in the body when the fix relates
to one (e.g. `Relates to FR03`). Do not bundle unrelated edits.

### Step 6 — Freechat log (traceability)

Append a short entry to `prompts/.logs/freechat-<date>.md` (create if absent):

- **When** and **who** (the developer, if known).
- **The colloquial request** (verbatim or close).
- **Triage verdict** (quick fix / redirected — and why).
- **What changed** (files + one-line rationale) and the **minimal-diff** note.
- **Gates run** and their result; whether a critical path was touched.
- **Commit** hash.

This keeps even fast-lane changes traceable (hard rule 3) — the framework never
loses the thread of *what changed and why*.

### Step 7 — Report

Briefly: the verdict, what you changed, which gates passed, the commit, and the
log entry. If you **redirected** instead of editing, name the exact skill to run
and the one-line reason.

---

## Non-negotiable rules of this skill

- **Triage first.** Anything that needs a new/changed requirement, scope, business
  rule, data-model, or compliance obligation is **refused and redirected** — never
  applied on the fast lane.
- **Never commit a failing change.** Affected gates from `forge.config.json` must
  be green first.
- **Minimal diff.** The smallest edit that fixes it; no opportunistic refactors.
- **Stay traceable.** Preserve `@requirement`/`@rule` tags, sync derived docs when
  affected, and always write the freechat log.
- **Stack-neutral.** Read gates, conventions, critical paths and compliance from
  `forge.config.json`; never assume a language, framework, datastore, or domain.
  If the config is missing, apply the change, skip what you cannot run, and say so.
- **Stay in the current thread.** No orchestration subagent — this is the fast lane.
