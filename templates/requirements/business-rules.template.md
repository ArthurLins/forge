<!--
  Forge — business rules template (tier: standard). The invariants the system
  must enforce. Genesis copies this to docs/requirements/business-rules.md.
  Replace every {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Business Rules

> **Purpose:** the consolidated, numbered rules the system must always enforce.
> Business rules are referenced by functional requirements, use cases, and the
> [traceability matrix](traceability.md).

**ID convention:** business rules use the prefix **`BR`** (e.g. `BR01`). Tag the
enforcing code and its tests with `@businessRule BR01`. See the
[index](index.md) for the full taxonomy.

---

## Rules

| ID       | Rule                          | Related (FR/EN/CR) |
| -------- | ----------------------------- | ------------------ |
| **BR01** | {{RULE_STATEMENT}}            | {{RELATED_IDS}}    |
| **BR02** | {{RULE_STATEMENT}}            | {{RELATED_IDS}}    |

<!-- One row per rule. Phrase a rule as an invariant ("X must always…",
     "Y is not allowed when…"), not as a feature. -->

---

## Critical rules / paths

<!--
  PROJECT-FILLED, EMPTY BY DEFAULT. The subset of rules whose violation is most
  costly and that therefore MUST be covered by tests. Forge ships NO defaults.
  Keep in sync with forge.config.json (criticalPaths.paths). The reviewer
  subagent reads this and fails a change that touches a critical rule without a
  test.
-->

> No critical rules are flagged yet. Add the rules that **must** be covered by
> tests below; keep this list in sync with `forge.config.json` →
> `criticalPaths.paths` and with the critical paths in
> [`non-functional.md`](non-functional.md).

| Critical rule (BR) | Why it is critical | Covered by (test ref) |
| ------------------ | ------------------ | --------------------- |
| {{BR_ID}}          | {{WHY}}            | {{TEST_REFERENCE}}    |

---

### Worked stub (generic — replace or delete)

| ID       | Rule                                                          | Related      |
| -------- | ------------------------------------------------------------ | ------------ |
| **BR01** | An item must have a non-empty name; creation is rejected otherwise. | FR01, EN01 |
| **BR02** | An archived item cannot be edited; it must be restored first. | FR01, EN01   |

> *Critical rules example (project decides):* `BR01` might be flagged critical
> with a test reference — left empty above on purpose.
