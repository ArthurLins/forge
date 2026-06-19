<!-- GENERATED from prompts/state.json by tools/forge_tools/status.py.
     Do not edit by hand: run `make forge-status` or `make forge-sync-docs`. -->

# Forge (self) — Status

> Human-readable view of [`state.json`](state.json). **Generated — do not edit by hand.** The plan index is [`ROADMAP.md`](ROADMAP.md).

**Updated:** 2026-06-18 · **Legend:** `[ ]` pending · `[~]` in_progress · `[x]` blocked · `[v]` done

## Summary

| Metric | Count |
| ------ | ----- |
| Total prompts | 4 |
| Done | 4 |
| In progress | 0 |
| Blocked | 0 |
| Pending | 0 |

**Overall progress:** 4/4 done (100%)

**Next eligible:** DONE — every prompt is complete.

---

## Phase S0 — Self-hosting infrastructure (2/2)

| Status | ID | Title | Depends on | Refs | Commit |
| ------ | -- | ----- | ---------- | ---- | ------ |
| [v] | S0.1 | Make Forge self-hosting (self/ workspace, manifest + export, forge-selfcheck gate, /forge-contribute, framework CI) | — | vision, functional, decisions | — |
| [v] | S0.2 | forge-export: adopter copy has no dead self-only targets and is docs-fresh | S0.1 | functional, decisions | `de25e72` |

## Phase S1 — Team hardening (multi-contributor) (2/2)

| Status | ID | Title | Depends on | Refs | Commit |
| ------ | -- | ----- | ---------- | ---- | ------ |
| [v] | S1.1 | forge-validate: adopter project integrity gate + optional strict-validation CI selectable at /forge-init | S0.1 | functional, decisions | `ff1952a` |
| [v] | S1.2 | Multi-contributor hardening: sharded claims + merge queue/required checks + union-merge for derived docs + teams guide | S1.1 | functional, decisions | `1ddddcb` |
