# Forge readiness review — scaling to very large projects & asynchronous multi-contributor work

> **Self-development artifact (S2.1).** Produced by `/forge-contribute` as the
> grounding for phase **S2 — Scale & async-collaboration readiness**. Self-only
> (excluded from the adopter export per [`../../forge.manifest.json`](../../forge.manifest.json)).
> The constitution it is scoped against is [`FORGE.md`](../../FORGE.md); the
> design stance it crystallizes is **ADR-S5** in
> [`../requirements/decisions.md`](../requirements/decisions.md).

- **Date:** 2026-06-25
- **Scope of the audit:** Is Forge ready to (A) scale to very large projects
  (hundreds/thousands of requirements and prompts, many modules, large
  traceability matrices, long-running roadmaps) and (B) support **asynchronous**
  multi-contributor / multi-agent collaboration?
- **Method:** a read of the framework source (engine, generators, skills/commands,
  templates, guides, CI), cross-checked against two evidence bases — authoritative
  guidance on building **efficient tools for AI agents** and **validated CS/SE
  literature**. Every recommendation below is tied to a concrete gap *and* a
  citation. The full reference list is at the end.
- **Baseline already shipped:** phase **S1 — Team hardening** already provides
  sharded claims, union-merge for derived docs, a merge queue + required checks,
  and the `forge-validate` integrity gate (see
  [`../../docs/guides/teams.md`](../../docs/guides/teams.md)). This review looks
  for what is *missing beyond that baseline* — it does not re-propose it.

---

## 1. Thesis

Forge's readiness for scale and async collaboration is, at its core, a
**context-engineering** and a **coordination** problem — not a "bigger model /
more agents" problem. Three convergent bodies of evidence frame every gap and
fix below:

1. **Context is a finite, degrading resource — engineer it, do not fill it.**
   Long-context recall is empirically unreliable: accuracy degrades as input grows
   *even on simple tasks* and mid-context information is lost (a U-shaped position
   bias). → *Context Rot* (Chroma 2025); *Lost in the Middle* (Liu et al., TACL
   2024); *Effective context engineering* (Anthropic 2025); *Code execution with
   MCP* (Anthropic 2025). **Implication:** never bulk-load a huge requirements doc
   or roadmap into a prompt; retrieve the relevant slice just-in-time off Forge's
   machine-readable source of truth and `@requirement` tags.

2. **Coordination overhead caps parallelism, and the contributor partition
   becomes the architecture.** Communication channels grow as *n(n−1)/2*; the
   serial fraction bounds any speed-up; and a system's structure mirrors the
   communication structure of the org that builds it. → *Conway* (1968) + the
   empirically-validated *Mirroring Hypothesis* (MacCormack et al. 2012); *Parnas*
   information hiding (1972); *Brooks* (1975); *Amdahl* (1967); *Cataldo* on
   socio-technical congruence (2006); *Accelerate/DORA* (2018); *Reinertsen*
   (2009); *Software Engineering at Google* (2020). **Implication:** define module
   boundaries first and assign agents/contributors to them (the inverse-Conway
   maneuver), keep WIP bounded and the trunk green, and schedule async work off
   the dependency graph — not an org chart.

3. **Multi-agent reliability depends on shared context and independence.**
   Parallel subagents excel at independent, read-heavy work but fail when they
   must share context or coordinate decisions (coding is named a poor fit);
   conflicting implicit decisions produce incoherent output. → *Multi-agent
   research system* (Anthropic 2025); *Don't build multi-agents* (Cognition 2025);
   *ReAct* (2023); *Reflexion* (2023); *Self-Consistency* (2023); *SWE-bench* /
   *SWE-agent* (2024). **Implication:** parallelize only genuinely independent
   prompts, share the full trace via the single source of truth, add a
   review→reflect→retry loop, and reserve multi-sample reconciliation for
   high-stakes decisions.

This thesis is recorded as **ADR-S5** and governs the whole S2 backlog: prefer
**scoping and retrieval over a bigger context**, and **do not re-shard
`state.json`** until contention is *measured*, not assumed.

---

## 2. What Forge already does well

**On scale.** Requirements already split across typed docs (FR/NFR/BR/CR/UC/EN/EC);
generators read knobs from `forge.config.json` rather than hardcoding a stack;
each prompt declares its `refs`; eligibility selection is a linear topological
scan with early exit and per-prompt claim sharding (no central lock).

**On async.** The S1 baseline is the industry-standard package: sharded claims
(`prompts/claims/<id>.json`) so two workers never grab the same prompt;
`merge=union` on the regenerated line-oriented docs (the most common conflict);
merge queue + required checks (test against the *merged* result); and
`forge-validate` as the static integrity gate. The single machine-readable source
of truth + `@requirement` tags are exactly the "shared full trace" (Cognition) and
the "lightweight identifiers for just-in-time retrieval" (Anthropic context
engineering) that the literature calls for.

These are **not** re-proposed below.

---

## 3. Gap analysis

Severity is relative to the stated axis: **blocker** (breaks at scale/async),
**major** (bites hard, common), **minor** (friction / latent edge case).

### 3.1 Scale axis

| # | Gap | Evidence in repo | Sev. |
| - | --- | ---------------- | ---- |
| SC-1 | The traceability matrix and changelog are regenerated **in full** on every sync — `traceability.py` walks the whole tree (`os.walk(common.REPO_ROOT)`, global globs); `changelog.py` runs `git log` over the whole history. Output grows unbounded. | `tools/forge_tools/traceability.py`, `tools/forge_tools/changelog.py` | major |
| SC-2 | `sync-docs` always runs all core generators together — no scoped / incremental regeneration ("only this module's matrix", "skip the changelog"). | `tools/forge_tools/sync_docs.py` (`_run_core` runs all three unconditionally) | major |
| SC-3 | Requirements and traceability are **not partitionable by module** — globs and the requirement parser are global, so a large monorepo cannot regenerate or scope one module in isolation. | `traceability.py` (global `scan(globs)`); `tools/forge_tools/requirements.py` (walks all of `docs/requirements/`) | major |
| SC-4 | The prompt template tells the agent to "read the docs this prompt touches" with **no subsetting guidance** — a prompt touching a large `functional.md` pulls the whole doc into context. | `templates/prompt.template.md` (Reference docs / Context sections) | major |
| SC-5 | Prompt eligibility selection is O(N) with no phase index — negligible at small N, additive at thousands of prompts × high invocation frequency. | `prompts/next_prompt.py` (linear scan in file order) | minor |
| SC-6 | The single reviewer subagent loads the whole project (config + all requirement docs + diff) — context pressure grows with project size; no per-module review. | `.claude/agents/reviewer.md` | minor |

### 3.2 Async multi-contributor axis

| # | Gap | Evidence in repo | Sev. |
| - | --- | ---------------- | ---- |
| AS-1 | **Claims have no heartbeat/TTL and no auto-release.** A crashed worker's claim blocks its prompt indefinitely; `forge-validate` only *warns* after 7 days. No retry count, no auto-`blocked` after N failures. | `docs/guides/teams.md` (claim = `{promptId, owner, claimedAt}`); `tools/forge_tools/validate.py` (`STALE_CLAIM_AGE_DAYS = 7`, warning only) | major |
| AS-2 | **No pre-merge guard on the source of truth.** `forge-validate` does not detect git **conflict markers** in requirement docs or `state.json`, nor verify ref↔requirement consistency before merge — a silently mis-merged spec can land. Source docs are (correctly) *not* union-merged, so they can conflict. | `tools/forge_tools/validate.py` (validates after merge; no conflict-marker scan) | major |
| AS-3 | **No WIP limit or dependency-aware scheduling.** Marking one phase-completing prompt `done` can make 50 dependents eligible at once; nothing bounds concurrent in-flight prompts or orders them by the dependency graph. | `prompts/next_prompt.py` (returns first eligible, no priority/cap); `forge.config.json` (no WIP knob) | major |
| AS-4 | **No ownership / assignment of modules or requirements.** `state.json` records status and commit but not who owns a module's spec; claims are ephemeral and leave no assignment trail — so async routing relies on a side channel. | `prompts/state.schema.md` (no `owner`/`assignee`); claims deleted on `done` | minor |
| AS-5 | The reviewer is a single agent (see SC-6) — for async, many small per-module reviews would parallelize better and keep each review's context tight. | `.claude/agents/reviewer.md` | minor |

> A note on `state.json` write contention: it is real in principle (one shared
> file), but the S1 merge-queue + claims already serialize the dangerous case, and
> the literature (see ADR-S5) says **measure before re-sharding**. The S2 backlog
> therefore attacks the *derived-doc* growth and the *coordination* surfaces
> first, and explicitly defers any `state.json` re-shard.

---

## 4. The grounded improvement backlog (phase S2)

Each item names the gap it closes, the **stack-neutral, domain-agnostic** shape of
the change (no stack is assumed; all knobs live in `forge.config.json`), the
**rationale with citations**, the severity, and its dependency. Items are
recorded as pending prompts `S2.2…S2.8` in
[`../prompts/state.json`](../prompts/state.json); they are *planned here*, to be
built later via `/forge-contribute` (or `/forge-run`).

### S2.2 — Prompt context discipline (just-in-time retrieval)
- **Closes:** SC-4 (and lowers context cost everywhere).
- **Change (shape):** revise `templates/prompt.template.md` and the
  `forge-plan-phase` guidance so a prompt (a) retrieves only the *specific*
  `@requirement` ids it implements rather than whole docs, (b) places the
  load-bearing instructions/spec at the **start and end** of the prompt, and (c)
  carries worked examples, not just field lists. Add a short "context budget" note
  to the Definition of Done.
- **Rationale:** mid-context information is lost (*Lost in the Middle*, Liu et al.
  2024) and accuracy degrades with input length even on simple tasks (*Context
  Rot*, Chroma 2025); curate the token set deliberately (*Effective context
  engineering*, Anthropic 2025); worked examples beat bare schemas for parameter
  accuracy (*Advanced tool use*, Anthropic 2025).
- **Severity:** major · **Depends on:** S2.1 · low risk, high leverage → do first.

### S2.3 — Module-scoped requirements + scoped/incremental derived docs
- **Closes:** SC-1, SC-2, SC-3.
- **Change (shape):** let `forge.config.json` declare module/area scopes; teach
  `traceability.py`, `changelog.py` and `sync_docs.py` to regenerate **one scope**
  (and bound the changelog by range) so a large monorepo re-derives only the
  affected module. Derived docs stay generated, never hand-edited (Principle 6).
- **Rationale:** decompose around hidden, change-prone decisions so a module can be
  worked in isolation (*Parnas* 1972); module boundaries should mirror the
  contributor/agent partition (*Conway* 1968; *Mirroring*, MacCormack et al.
  2012); progressive, on-demand disclosure instead of loading everything (*Code
  execution with MCP*, Anthropic 2025; context engineering 2025).
- **Severity:** major (biggest scale lever) · **Depends on:** S2.1.

### S2.4 — Claim lifecycle hardening (self-healing async)
- **Closes:** AS-1.
- **Change (shape):** extend the claim record with a heartbeat timestamp, a TTL,
  and a retry count; have the orchestration commands refresh the heartbeat; have
  `next_prompt.py` treat a claim past its TTL as releasable; and move a prompt to
  `blocked` after N failed attempts. Keep it Python-3 stdlib + plain files
  (no new dependency); `forge-validate` enforces the new invariants.
- **Rationale:** long-running agent systems need **durable, resumable execution**
  and self-healing rather than manual intervention (*Multi-agent research system*,
  Anthropic 2025); make queues visible and bounded (*Reinertsen* 2009). A
  review→reflect→retry loop is a validated reliability lever (*Reflexion*, Shinn
  et al. 2023).
- **Severity:** major (deadlock risk in unattended CI) · **Depends on:** S2.1.

### S2.5 — WIP limits + dependency-aware scheduling
- **Closes:** AS-3.
- **Change (shape):** add a `forge.config.json` WIP cap (max concurrent in-flight
  prompts/claims); have the orchestration commands claim at most N at a time and
  prefer prompts that unblock the most dependents (schedule off the `dependsOn`
  graph). No stack assumed.
- **Rationale:** the serial fraction bounds speed-up (*Amdahl* 1967) and
  communication overhead grows combinatorially (*Brooks* 1975); elite delivery
  uses small batches + WIP limits + trunk-based flow (*Accelerate/DORA* 2018;
  *Reinertsen* 2009); schedule from the dependency graph to maximize
  socio-technical congruence (*Cataldo* 2006); parallelize only independent work
  (*Multi-agent research system*, Anthropic 2025).
- **Severity:** major · **Depends on:** S2.4 (builds on the claim record).

### S2.6 — Source-of-truth conflict guard (pre-merge)
- **Closes:** AS-2.
- **Change (shape):** extend `forge-validate` to **fail** on git conflict markers
  in any requirement doc or `state.json`, and to verify that every prompt `ref`
  resolves to a real requirement id, *before* a merge lands (it already runs as a
  required merge-queue check). Explicitly keep source docs **out** of union-merge.
- **Rationale:** keep the trunk green with quality gates and small batches
  (*Accelerate/DORA* 2018); every behavior should be a CI contract — the Beyoncé
  Rule (*Software Engineering at Google* 2020); conflicting implicit decisions on a
  shared artifact produce bad results, so guard the shared source (*Don't build
  multi-agents*, Cognition 2025).
- **Severity:** major (prevents a silently broken spec) · **Depends on:** S2.1.

### S2.7 — Ownership / assignment metadata (inverse-Conway routing)
- **Closes:** AS-4.
- **Change (shape):** add an **optional** `owner` to a module/requirement (and
  surface it in `STATUS`/`teams.md`) so async work can be routed to the agent that
  owns the module's secret. Optional → backward compatible; no stack/domain added.
- **Rationale:** assign the partition first so the architecture mirrors it
  intentionally (*Conway* 1968; *Mirroring*, MacCormack et al. 2012); high
  socio-technical congruence cuts completion time (*Cataldo* 2006).
- **Severity:** minor · **Depends on:** S2.3 (needs the module partition).

### S2.8 — Reviewer scaling (per-module review + reflect→retry)
- **Closes:** SC-6, AS-5.
- **Change (shape):** allow the reviewer to be scoped to one module (one focused
  review per module's diff + that module's boundaries/conventions), enabling
  parallel reviews; and feed a rejection back for one self-correcting retry before
  re-review.
- **Rationale:** orchestrator-worker parallelism for independent, read-heavy work
  with condensed summaries to the coordinator (*Multi-agent research system*,
  Anthropic 2025); a well-designed agent-computer interface is itself a primary
  lever on success (*SWE-agent*, Yang et al. 2024); reflect-then-retry improves
  outcomes (*Reflexion*, Shinn et al. 2023).
- **Severity:** minor · **Depends on:** S2.3.

---

## 5. Limitations & non-goals (honest scope)

- **No `state.json` re-shard yet.** It is a single shared file, but S1's
  merge-queue + claims already serialize the dangerous write, and the evidence says
  *measure before adding architecture* (ADR-S5; *Building effective agents*,
  Anthropic 2024 — "add complexity only when it demonstrably improves outcomes").
  Re-sharding is deferred until contention is observed.
- **No stack and no domain are added.** Every S2 change stays stack-neutral
  (knobs in `forge.config.json`) and domain-agnostic; derived docs remain
  generated, never hand-edited; orchestration stays isolated; guidance stays
  layered. The constitution (`FORGE.md`) is intact.
- **Multi-agent is used surgically, not by default.** Per Cognition and the
  Anthropic research-system caveat, parallel agents are reserved for genuinely
  independent work (per-module derivation/review); dependent or shared-state work
  stays sequential through claims + the merge queue.
- **This review is a snapshot.** S2.1 should, over time, become a *repeatable*
  readiness check; for now it is a one-time, evidence-grounded audit.

---

## 6. References

### 6.1 Building efficient tools/systems for AI agents
1. Anthropic (E. Schluntz, B. Zhang). *Building Effective Agents.* 2024-12-19.
   https://www.anthropic.com/engineering/building-effective-agents
2. Anthropic (K. Aizawa). *Writing effective tools for agents — with agents.*
   2025-09-11. https://www.anthropic.com/engineering/writing-tools-for-agents
3. Anthropic (Applied AI). *Effective context engineering for AI agents.*
   2025-09-29. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
4. Anthropic (A. Jones, C. Kelly). *Code execution with MCP: Building more
   efficient agents.* 2025-11-04. https://www.anthropic.com/engineering/code-execution-with-mcp
5. Anthropic. *How we built our multi-agent research system.* 2025-06-13.
   https://www.anthropic.com/engineering/multi-agent-research-system
6. W. Yan (Cognition). *Don't Build Multi-Agents.* 2025-06-12.
   https://cognition.com/blog/dont-build-multi-agents
7. K. Hong, A. Troynikov, J. Huber (Chroma). *Context Rot: How Increasing Input
   Tokens Impacts LLM Performance.* 2025-07-14.
   https://www.trychroma.com/research/context-rot
8. Anthropic (J. Young). *Effective harnesses for long-running agents.*
   2025-11-26. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
9. Anthropic (B. Wu). *Introducing advanced tool use on the Claude Developer
   Platform.* 2025-11-24. https://www.anthropic.com/engineering/advanced-tool-use

### 6.2 Validated CS / software-engineering literature
10. M. E. Conway. *How Do Committees Invent?* Datamation 14(4), 1968.
    https://www.melconway.com/Home/pdf/committees.pdf
11. A. MacCormack, J. Rusnak, C. Y. Baldwin. *Exploring the Duality between Product
    and Organizational Architectures: A Test of the "Mirroring" Hypothesis.*
    Research Policy 41(8):1309–1324, 2012. doi:10.1016/j.respol.2011.11.005
12. D. L. Parnas. *On the Criteria To Be Used in Decomposing Systems into Modules.*
    CACM 15(12):1053–1058, 1972. doi:10.1145/361598.361623
13. F. P. Brooks Jr. *The Mythical Man-Month.* Addison-Wesley, 1975 (anniv. 1995).
14. F. P. Brooks Jr. *No Silver Bullet — Essence and Accidents of Software
    Engineering.* IEEE Computer 20(4):10–19, 1987. doi:10.1109/MC.1987.1663532
15. G. M. Amdahl. *Validity of the Single Processor Approach to Achieving Large
    Scale Computing Capabilities.* AFIPS 1967. doi:10.1145/1465482.1465560
16. M. Cataldo, P. Wagstrom, J. Herbsleb, K. Carley. *Identification of
    Coordination Requirements.* ACM CSCW 2006. doi:10.1145/1180875.1180929
17. N. Forsgren, J. Humble, G. Kim. *Accelerate: The Science of Lean Software and
    DevOps.* IT Revolution, 2018.
18. T. Winters, T. Manshreck, H. Wright. *Software Engineering at Google.*
    O'Reilly, 2020.
19. D. G. Reinertsen. *The Principles of Product Development Flow.* Celeritas, 2009.
20. N. F. Liu et al. *Lost in the Middle: How Language Models Use Long Contexts.*
    TACL 12:157–173, 2024. doi:10.1162/tacl_a_00638
21. J. Wei et al. *Chain-of-Thought Prompting Elicits Reasoning in LLMs.*
    NeurIPS 2022. arXiv:2201.11903
22. S. Yao et al. *ReAct: Synergizing Reasoning and Acting in Language Models.*
    ICLR 2023. arXiv:2210.03629
23. N. Shinn et al. *Reflexion: Language Agents with Verbal Reinforcement
    Learning.* NeurIPS 2023. arXiv:2303.11366
24. X. Wang et al. *Self-Consistency Improves Chain of Thought Reasoning.*
    ICLR 2023. arXiv:2203.11171
25. C. E. Jimenez et al. *SWE-bench: Can Language Models Resolve Real-World GitHub
    Issues?* ICLR 2024. arXiv:2310.06770
26. J. Yang et al. *SWE-agent: Agent-Computer Interfaces Enable Automated Software
    Engineering.* NeurIPS 2024. arXiv:2405.15793
