# Working on a Forge project as a team

A Forge project is built by agents executing a suite of self-contained prompts
against one source of truth. With a **single** contributor that is already
deterministic. With **several** contributors (or several agents) running in
parallel, three surfaces can collide. This guide names those surfaces and gives
the **exact** mitigations Forge ships — all stack-neutral, all already wired into
the tooling.

> TL;DR: turn on the **merge queue** and make the Forge check **required**, let
> **sharded claims** stop two workers grabbing the same prompt, let
> **union-merge** auto-resolve the regenerated docs, and use **`forge-validate`**
> as the integrity gate. On any derived-doc conflict, run `make forge-sync-docs`.

---

## The conflict surfaces

| Surface | Why it collides in parallel | Mitigation |
| ------- | --------------------------- | ---------- |
| **Shared `prompts/state.json`** | Two PRs each flip a prompt to `done` / bump `updatedAt`; both green alone, the second to merge can clobber or conflict. | Merge queue + required check (test against the merged result). |
| **Regenerated derived docs** (`STATUS.md`, traceability matrix, changelog) | Append-/line-oriented files that every prompt regenerates; two branches adding lines conflict on every overlap. | Union-merge (`.gitattributes`) + regenerate with `make forge-sync-docs`. |
| **Parallel prompt execution** | Two workers run `next_prompt.py` at the same instant and both pick the same eligible prompt. | Sharded claims (one claim file per in-flight prompt). |

The four mitigations below cover all three. They compose: claims prevent the
duplicate-work collision up front; the merge queue prevents the "green alone,
broken together" merge; union-merge removes the most common file conflict; and
`forge-validate` is the gate that catches anything structural that slips through.

---

## 1. Merge queue + required checks

**What it solves.** Two PRs can each pass CI in isolation and still break once
both land (e.g. both edited `state.json`, or each regenerated `STATUS.md` from a
different base). A merge queue re-runs the gate against the **actually-merged**
result and serializes merges, so derived docs are regenerated against the final
order — killing "two PRs green alone, broken together".

**Forge is already wired for it.** Both the framework's own CI
(`.github/workflows/forge-selfcheck.yml`) and the adopter CI templates
(`templates/ci/forge-ci.yml.template`, `templates/ci/forge-validate.yml.template`)
declare a `merge_group:` trigger, so the gate runs as a merge-queue check.

**Enable it (GitHub):**

1. **Settings → Branches → Branch protection rules** for the default branch.
2. **Require status checks to pass before merging**, and select the Forge check:
   - adopters: **"Project integrity"** (the validate workflow) and/or the
     **quality** / **docs-freshness** jobs of the CI workflow;
   - Forge itself: **"Constitution gate (selfcheck + docs-freshness)"**.
3. **Require merge queue** (the "Require merge queue" / "Merge queue" option in
   the same ruleset). With the `merge_group` trigger already present, the queue
   will run the check against the merged candidate before it lands.

Without marking the check **required**, the workflow still runs but does **not**
block merge — so a parallel-broken PR could land. Required + queued is the
package.

---

## 2. Sharded claims (parallel-execution safety)

**What it solves.** Two contributors (or two agents) must never grab the same
prompt. The naive fix — a "who's working on what" field in `state.json` — would
itself become a write-contended file. Instead Forge **shards** the marker: one
small file per in-flight prompt.

**How a claim works.**

- A claim is `prompts/claims/<promptId>.json` =
  `{ "promptId": "<id>", "owner": "<who>", "claimedAt": "<ISO-8601>",
  "heartbeatAt": "<ISO-8601>", "attempts": <int> }`. `heartbeatAt` and `attempts`
  are **optional** self-healing fields (see below); a claim with only
  `promptId`/`owner`/`claimedAt` is fully valid and behaves as before.
- One file per in-progress prompt → claims never conflict with **each other** or
  with `state.json` (different paths, no shared lines).
- `prompts/next_prompt.py` **skips any prompt that has a live claim file**, so a
  second worker selects the next free prompt (or reports `BLOCKED` / `DONE`).
- Fully backward-compatible: if `prompts/claims/` is absent or holds only
  `.gitkeep`, selection behaves exactly as before. Reading claims uses the
  Python-3 stdlib only — no extra dependency.

**Self-healing (heartbeat + TTL).** While a prompt runs, the orchestrator
refreshes the claim's `heartbeatAt` (~every 300s / on each significant step). If
a worker **crashes**, it stops refreshing; once `now − heartbeatAt` exceeds the
TTL (`claims.ttlSeconds`, default **1800s**) the selector treats the claim as
**expired** and the prompt becomes eligible again — **no manual deletion
needed**. Expiry is non-destructive: the stale file is left on disk (a later
worker overwrites it on re-claim, and `forge-validate` warns about it). A
**legacy** claim that carries no `heartbeatAt` is **never** auto-released — it is
honored exactly as before, so old claims keep skipping the prompt until cleared
by hand.

**The convention the orchestration commands follow.** `/forge-next`,
`/forge-run` and `/forge-run-phase` all:

1. **Write the claim** for `<ID>` *before* delegating — `claimedAt` AND an initial
   `heartbeatAt` (both ISO-8601 now). On a **re-claim** of an expired claim, carry
   forward the prior `attempts` value.
2. **Refresh `heartbeatAt`** periodically (~every 300s / on each significant step)
   while the prompt runs, so a live worker keeps the claim from expiring.
3. **Remove the claim** once `<ID>` is marked `done`.
4. On **failure**, **leave the claim in place** alongside the
   `prompts/.logs/<ID>.note.md` note and **increment `attempts`** (carrying any
   prior value), so a parallel worker keeps skipping the still-in-progress prompt.
   After **`claims.maxAttempts`** (default **3**) failures, set the prompt's
   `status` to `blocked` in `state.json` (the selector already skips `blocked`).

**WIP limit + impact-aware scheduling.** Two optional knobs keep a parallel run
healthy without changing default behavior:

- **WIP limit (`claims.maxConcurrent`).** A non-negative cap on how many ACTIVE
  claims (prompts in flight) may exist at once; absent / `0` = unlimited. The
  orchestration commands hold at most this many concurrent claims — count the
  active claims in `prompts/claims/` before claiming another, and wait if you are
  at the cap. Bounded WIP keeps the merge queue short and feedback fast.
  `forge-validate` **warns** (never fails) when the active-claim count exceeds it.
- **Impact-aware picking (`next_prompt.py --by-impact`).** Among the eligible
  prompts, this returns the one that unblocks the **most** still-pending work
  (the id appearing in the most `dependsOn` lists), ties broken by file order. It
  is a pure reordering of the already-eligible set — the default (no flag) is
  unchanged. The orchestrator uses it under parallelism to start high-impact work
  first, widening the dependency frontier for the other workers.

**Integrity is enforced.** `forge-validate`'s **claims-integrity** check fails on
a claim that references a non-existent prompt or a `done` prompt (a stale/leaked
claim), or on a malformed `heartbeatAt`/`attempts` shape; it **warns** on a very
old claim, an **expired** heartbeat (the selector auto-releases it), a claim
that has hit `maxAttempts` without being `blocked`, or more active claims than
the `claims.maxConcurrent` WIP limit. The framework's own
`forge-selfcheck` additionally asserts that the shipped seed's `prompts/claims/`
holds only `.gitkeep` — no leaked claim is ever distributed. `forge-export`
resets `prompts/claims/` to just `.gitkeep` in adopter copies.

**Releasing a stale claim.** Self-healing usually makes this unnecessary: a
crashed worker's claim expires after the TTL and the prompt is picked up again
automatically. For a **legacy** claim without a heartbeat (never auto-released),
delete its `prompts/claims/<ID>.json` (and clear/resolve
`prompts/.logs/<ID>.note.md`); the prompt becomes eligible again on the next
`next_prompt.py`.

---

## 3. Union-merge for derived docs

**What it solves.** The single most common conflict on a busy Forge repo is two
branches each appending to a generated, line-oriented file — the changelog, the
traceability matrix, `prompts/STATUS.md`. These are **generated, never
hand-edited** (FORGE.md, Principle 6), so a textual merge conflict on them is
pure noise.

**The mitigation.** A `.gitattributes` marks those paths `merge=union`, telling
git to keep **both** sides' lines instead of raising a conflict:

```
docs/generated/CHANGELOG.md    merge=union
docs/generated/traceability.md merge=union
prompts/STATUS.md              merge=union
```

(The adopter version is `templates/gitattributes.template`, parameterized to
`docs.generatedDir`; `/forge-init` installs it as the project's `.gitattributes`,
merging into an existing one if present.)

**On any conflict (or after any union-merge), regenerate the canonical form:**

```bash
make forge-sync-docs
git add -A && git commit
```

Union-merge can leave lines slightly out of order or duplicated — harmless,
because the generators are the only real writers of these files. Re-deriving
restores the canonical content, and the docs-freshness gate then passes. The same
`make forge-sync-docs` is what the CI docs-freshness check expects, so this also
keeps the merge queue green.

> Do **not** put source files under `merge=union` — only regenerated, additive
> derived docs. A union-merge of real source would silently keep both sides of a
> genuine conflict.

---

## 4. `forge-validate` — the integrity gate

`forge-validate` is the static-integrity gate that ties the above together. Run
it locally (`make forge-validate-check`) and in CI (the validate workflow, when
`ci.strictValidation` is on). It fails the build on:

- a broken prompt **state machine** (duplicate ids, a missing prompt file, an
  unknown or cyclic `dependsOn`, an invalid status, a failing `next_prompt.py`);
- a **claims-integrity** violation (a claim on a non-existent or `done` prompt);
- a dangling `@requirement` / `@rule` tag, a malformed Conventions Map, an
  invalid config, or **stale derived docs**.

So even if a parallel merge slips a contradiction past review, the required
validate check in the merge queue catches it before it lands. Mark **"Project
integrity"** as a required check (see §1) to make this binding.

---

## 5. Ownership / assignment (inverse-Conway routing)

**What it solves.** A system's structure mirrors the communication structure of
the org that builds it (Conway's Law; empirically confirmed by the "mirroring
hypothesis"). At scale, async work produces clean architecture only if each
module/area has a clear owner — so the partition of *who builds what* is
deliberate, not accidental.

**The optional `owner` field.** Each prompt in `prompts/state.json` may carry an
optional `owner` (a person, team, agent, or module owner) — see
[`../../prompts/state.schema.md`](../../prompts/state.schema.md). It is purely a
routing aid: assign a module's prompts to the agent/contributor that owns that
module's "secret" (the change-prone decision it hides), so interdependent work is
coordinated rather than colliding. When at least one prompt declares an `owner`,
`STATUS.md` renders an **Owner** column; with none declared, the column is absent
and `STATUS.md` is byte-identical to before (fully backward-compatible). Combine
with `--by-impact` scheduling (§2) so each owner picks the highest-leverage prompt
in their area first.

---

## Quick checklist for a team

- [ ] **Enable the merge queue** on the default branch and mark the Forge check
      (**Project integrity** / the selfcheck gate) **required**.
- [ ] Confirm `.gitattributes` carries the three `merge=union` lines (installed by
      `/forge-init`; the template is `templates/gitattributes.template`).
- [ ] Let the orchestration commands write/remove **claims**; never edit
      `prompts/claims/` by hand except to release a crashed worker's stale claim.
- [ ] On a derived-doc conflict, run **`make forge-sync-docs`** and commit — never
      resolve the changelog / matrix / STATUS by hand.
- [ ] Keep **`make forge-validate-check`** green locally before opening a PR.
