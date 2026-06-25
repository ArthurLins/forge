<!-- GENERATED from prompts/state.json by tools/forge_tools/status.py.
     Do not edit by hand: run `make forge-status` or `make forge-sync-docs`. -->

# Forge (self) — Status

> Human-readable view of [`state.json`](state.json). **Generated — do not edit by hand.** The plan index is [`ROADMAP.md`](ROADMAP.md).

**Updated:** 2026-06-25 · **Legend:** `[ ]` pending · `[~]` in_progress · `[x]` blocked · `[v]` done

## Summary

| Metric | Count |
| ------ | ----- |
| Total prompts | 12 |
| Done | 9 |
| In progress | 0 |
| Blocked | 0 |
| Pending | 3 |

**Overall progress:** 9/12 done (75%)

**Next eligible:** `S2.3` — Module-scoped requirements + scoped/incremental derived-docs regeneration (per-module traceability/changelog/status)

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

## Phase S2 — Scale & async-collaboration readiness (5/8)

| Status | ID | Title | Depends on | Refs | Commit |
| ------ | -- | ----- | ---------- | ---- | ------ |
| [v] | S2.1 | Readiness audit: scale + async-collaboration gap review with an evidence-grounded improvement backlog (ADR-S5) | — | decisions | `0ca8329` |
| [v] | S2.2 | Prompt context discipline: just-in-time @requirement retrieval + load-bearing instructions at start/end + worked examples (context budget) | S2.1 | functional, decisions | `98c8eb9` |
| [ ] | S2.3 | Module-scoped requirements + scoped/incremental derived-docs regeneration (per-module traceability/changelog/status) | S2.1 | functional, decisions | — |
| [v] | S2.4 | Claim lifecycle hardening: heartbeat/TTL + retry count + auto-release of dead claims + auto-blocked after N failures | S2.1 | functional, decisions | `7233382` |
| [v] | S2.5 | WIP limits + dependency-aware scheduling: forge.config WIP cap, claim at most N, prefer prompts that unblock the most dependents | S2.4 | functional, decisions | `3789444` |
| [v] | S2.6 | Source-of-truth conflict guard: forge-validate fails on git conflict markers + verifies ref->requirement consistency pre-merge | S2.1 | functional, decisions | `f98e495` |
| [ ] | S2.7 | Optional module/requirement ownership metadata (inverse-Conway routing) surfaced in STATUS and the teams guide | S2.3 | functional, decisions | — |
| [ ] | S2.8 | Reviewer scaling: per-module review scoping (parallelizable) + a review->reflect->retry self-correction loop | S2.3 | functional, decisions | — |
