# `state.json` — schema reference

The **machine-readable state machine** for the prompt suite. It is the single
source of tracking: which prompts exist, their dependencies, and their status.
`next_prompt.py` reads it to select the next eligible prompt; `STATUS.md` is a
human-readable view **generated** from it (never edited by hand).

The repository ships an **empty seed** (`project`, `version`, `updatedAt` blank;
`phases` and `prompts` empty). Genesis (`/forge-init`) and phase planning
(`/forge-plan-phase`) fill it. The leading `_comment` key is a documentation
hint and may be deleted once the file is populated.

## Top-level fields

| Field           | Type     | Meaning                                                                 |
| --------------- | -------- | ----------------------------------------------------------------------- |
| `project`       | string   | The project name. Filled by genesis.                                    |
| `version`       | string   | The suite's version (free-form, e.g. `"1.0"`). Starts at `"0"`.         |
| `updatedAt`     | string   | ISO date (`YYYY-MM-DD`) of the last update to this file.                |
| `legend.status` | string[] | The allowed status values, in order: `pending`, `in_progress`, `blocked`, `done`. |
| `phases`        | object[] | The phase index — see below. Empty until planned.                       |
| `prompts`       | object[] | The prompts — see below. Empty until planned.                           |

## `phases[]` — one entry per phase

| Field  | Type            | Meaning                                  |
| ------ | --------------- | ---------------------------------------- |
| `id`   | number \| string | Phase identifier (e.g. `0`, `1`, `2`).  |
| `name` | string          | Human-readable phase name.               |

## `prompts[]` — one entry per prompt

| Field       | Type     | Required | Meaning                                                                                  |
| ----------- | -------- | -------- | ---------------------------------------------------------------------------------------- |
| `id`        | string   | yes      | Prompt id, `P<phase>.<seq>` (e.g. `P0.1`, `P2.3`). Unique across the suite.               |
| `phase`     | number \| string | yes | The phase this prompt belongs to; matches a `phases[].id`.                          |
| `title`     | string   | yes      | Short human-readable title of the prompt.                                                 |
| `status`    | string   | yes      | One of `legend.status`: `pending` → `in_progress` → `blocked` → `done`.                   |
| `dependsOn` | string[] | yes      | Ids of prompts that must be `done` before this one is eligible. Empty `[]` if none.       |
| `refs`      | string[] | yes      | References to the requirement docs (in `docs/requirements/`) this prompt reads/implements. |
| `file`      | string   | yes      | Path to the prompt file, **relative to `prompts/`** (e.g. `phase-0-foundation/P0.1-....md`). |
| `commit`    | string   | when `done` | The Conventional Commit hash that completed the prompt. Empty/omitted until `done`.   |
| `owner`     | string   | no       | Optional owner/assignee (a person, team, agent, or module owner). Routing aid for async work (inverse-Conway); surfaced as an **Owner** column in `STATUS.md` only when at least one prompt declares it. Absent → no Owner column (backward-compatible). |
| `updatedAt` | string   | yes      | ISO date (`YYYY-MM-DD`) of the last status change for this prompt.                        |

## Status semantics

- `pending` — not started; eligible to run once all `dependsOn` are `done`.
- `in_progress` — currently being worked on (still selectable by `next_prompt.py`
  if its dependencies are satisfied).
- `blocked` — cannot proceed (e.g. an external blocker); excluded from selection.
- `done` — completed; carries a `commit`. Contributes to other prompts'
  eligibility.

## Eligibility rule (how `next_prompt.py` selects)

A prompt is **eligible** when its `status` is `pending` or `in_progress` **and**
every id in its `dependsOn` is in the set of `done` prompts. The selector walks
`prompts[]` in file order (which is kept topological by phase/sequence) and
returns the **first** eligible prompt. If none of the pending prompts is
eligible, it reports `BLOCKED` with their ids; if no pending prompts remain, it
reports `DONE`.

## Example (illustrative — not shipped in the seed)

```json
{
  "project": "Acme",
  "version": "1.0",
  "updatedAt": "2026-01-15",
  "legend": { "status": ["pending", "in_progress", "blocked", "done"] },
  "phases": [{ "id": 0, "name": "Foundation" }],
  "prompts": [
    {
      "id": "P0.1",
      "phase": 0,
      "title": "Bootstrap the workspace",
      "status": "done",
      "dependsOn": [],
      "refs": ["architecture", "standards"],
      "file": "phase-0-foundation/P0.1-bootstrap.md",
      "commit": "a0d17135a2d6943a6183ef6a1158d565b59f3aca",
      "updatedAt": "2026-01-14"
    },
    {
      "id": "P0.2",
      "phase": 0,
      "title": "Agent guides",
      "status": "pending",
      "dependsOn": ["P0.1"],
      "refs": ["standards"],
      "file": "phase-0-foundation/P0.2-agent-guides.md",
      "updatedAt": "2026-01-15"
    }
  ]
}
```
