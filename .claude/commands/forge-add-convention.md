---
description: Guided add/change of an engineering convention (EC) in a Forge project's Conventions Map (docs/requirements/conventions.md) — the registry of cross-cutting engineering/UX defaults every feature must honor. Pick an entry from templates/conventions-catalog.md or define a custom one, set its Applies-to + Parameters, keep ids sequential, and mark its Status. Also the channel for recording an agent's proactive proposal when it spots an uncovered recurring concern.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# `/forge-add-convention` — add or change an engineering convention (`EC`)

You are an agent (Claude, Opus 4.8) at the root of a Forge-built project. Keep the
**Conventions Map** (`docs/requirements/conventions.md`) consistent when adding or
changing an `EC` — the registry of **cross-cutting engineering/UX defaults** that
every feature must honor (pagination, virtualization, async loading/empty/error
states, debounced search, avoid N+1, accessibility, authorization on every
action, …). The map exists so neither the developer nor the agent has to remember
these on every feature; this command is how it **grows**.

The map's enforcement is two-toothed and lives elsewhere — applicable `EC` rules
are injected into every feature-building prompt's context (the prompt reads
`conventions.md` and applies the matching entries), and the
[`reviewer`](../agents/reviewer.md) subagent checks them. This command only
**records** an entry; it does not gate anything itself.

## Inputs

- **What** convention to add or change, in the developer's words — or a
  **proposal an agent raised** while building (see "Proactive-proposal pathway"
  below).
- Whether it is a **new** `EC` or a **change** to an existing one.

## Step 0 — Read the map, the taxonomy, and the catalog

Read, in order:

1. `docs/requirements/conventions.md` — the current map (the `EC` entries already
   recorded, their ids, and the entry format). If it does **not** exist, the
   project has no Conventions Map yet: it is normally created by `/forge-init`.
   Offer to create it from
   [`templates/requirements/conventions.template.md`](../../templates/requirements/conventions.template.md)
   before adding the first entry (do not invent one silently).
2. `docs/requirements/index.md` — confirm the **`EC`** prefix in the ID taxonomy.
3. [`templates/conventions-catalog.md`](../../templates/conventions-catalog.md) —
   the curated seed library to pick from (each entry carries a rule intent,
   default parameters, an "Applies to" trigger, and which project types it suits).
4. `forge.config.json` — the stack/conventions, so a custom entry stays
   **stack-neutral** (a convention is an **intent**, never a named tool/library).

## Procedure

1. **Choose: catalog entry or custom.**
   - **From the catalog** — pick the entry that matches the need. Reuse its
     **Rule (intent)**, **Category**, **Applies to**, and **default Parameters**;
     adjust thresholds to the project if the developer wants.
   - **Custom** — only when the catalog has nothing suitable. Write the rule as a
     **stack-neutral intent** (what, never with-which-tool), give it a Category,
     an **Applies to** scope, and named **Parameters** with values. Keep it
     genuinely cross-cutting (it should apply to many features); a one-feature
     rule belongs in a requirement, not here.

2. **Assign the id.** Use the **next free, zero-padded** `EC` number in
   `conventions.md` (`EC-01`, `EC-02`, …). **Never reuse** a retired number; to
   drop a convention, set its **Status** to `waived` with a reason rather than
   renumbering or deleting. To **change** an existing one, edit that entry in
   place (keep its id).

3. **Write the entry** into `docs/requirements/conventions.md` using the file's
   **EC entry format** exactly — `Category`, `Rule (intent)`, `Applies to`,
   `Parameters`, `Rationale`, `Status`. Keep entries grouped loosely by category.
   Follow the project's `conventions.docsLanguage` for prose; keep the **id and
   code identifiers in English**.

4. **Set the Status.**
   - `active` — adopted and enforced now.
   - `proposed` — raised (often by an agent mid-build) and **awaiting the
     developer's approval**; record it as `proposed` until they confirm, then flip
     it to `active`.
   - `waived` — intentionally **not** applied; **must** carry the reason.

5. **Note the trigger scope precisely.** The **Applies to** line is what the
   feature prompts and the reviewer match against — make it concrete (the kind of
   work that triggers the rule), so an agent can decide objectively whether a
   given change is in scope.

6. **No matrix change.** The Conventions Map is **not** the traceability matrix —
   adding an `EC` does **not** create a requirement gap. (If a project tags
   honoring code with `@convention EC-xx`, that is lightweight traceability, not a
   gate; see `forge.config.json → traceability.tagAliases`.) You do not need to
   regenerate the matrix for an `EC` change. If the surrounding edit also touched
   real requirements, sync docs as usual.

## Proactive-proposal pathway (how agents grow the map)

While building, an agent may **notice a recurring concern the map does not
cover** (e.g. it keeps re-deriving the same retry/backoff or empty-state policy).
It should **not** silently invent a one-off rule. Instead it **proposes** an `EC`
— and this command is how that proposal is **recorded and approved**:

1. The building agent surfaces the proposed convention (its intended rule,
   Applies-to, and parameters).
2. Run `/forge-add-convention` to record it as a **`proposed`** `EC` in the map.
3. The **developer reviews and approves**; on approval flip its Status to
   `active`. Until then it stays `proposed` and does **not** block the reviewer.

## Verification

- The new/changed `EC` appears in `docs/requirements/conventions.md` in the
  correct format, with a sequential id, a concrete **Applies to**, named
  **Parameters**, and a **Status**.
- The rule is a **stack-neutral intent** (no language/framework/datastore/tool
  named) and genuinely **cross-cutting** (not a single-feature requirement in
  disguise).
- Ids are sequential and **none was reused**; a retired convention is `waived`
  with a reason, not deleted.
- Commit the change with the project's commit style, e.g.
  `docs(conventions): add EC-07 debounce high-frequency events`.

## Notes

- **Never invent product scope here.** An `EC` is an engineering/UX *default*, not
  a feature — product capabilities go through
  [`/forge-add-requirement`](forge-add-requirement.md).
- **Stack-neutral & domain-agnostic:** rules are intents parameterized by named
  thresholds; the stack lives only in `forge.config.json`.
- The map is grown **incrementally** — add a few entries at a time as the project
  surfaces them; you do not need to mirror the whole catalog.
- Never remove `docs/requirements/` or `prompts/`.
