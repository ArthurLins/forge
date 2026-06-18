<!--
  Forge — non-functional requirements template (tier: standard). Quality
  attributes. Genesis copies this to docs/requirements/non-functional.md.
  Replace every {{PLACEHOLDER}}; delete these comments once filled.
-->

# {{PROJECT_NAME}} — Non-Functional Requirements

> **Purpose:** the quality attributes the system must meet — performance,
> availability, security, usability, accessibility, and so on. These constrain
> *how* the functional requirements are realized.

**ID convention:** non-functional requirements use the prefix **`NFR`** (e.g.
`NFR01`), with dotted sub-items (`NFR01.1`). Tag implementing code/tests with
`@requirement NFR01`. See the [index](index.md) for the full taxonomy.

**Priority convention:** **[Must]**, **[Should]**, **[Later]**.

---

## NFR01 — {{QUALITY_ATTRIBUTE}}

- NFR01.1 — {{MEASURABLE_REQUIREMENT}} **[Must]**
- NFR01.2 — {{MEASURABLE_REQUIREMENT}} **[Should]**

<!-- Make NFRs measurable: a number, a threshold, a target. "Fast" is not a
     requirement; "responds in ≤ 2 s under normal load" is. Repeat per
     attribute (performance, availability, security, usability, …). -->

---

## Critical paths

<!--
  PROJECT-FILLED, EMPTY BY DEFAULT. List the flows whose failure is most costly
  and that therefore MUST be covered by tests. Forge ships NO defaults — only
  the project knows which paths are critical. These entries are also mirrored in
  forge.config.json (criticalPaths.paths) and are read by the reviewer subagent,
  which fails a change that touches a critical path without a test.
-->

> No critical paths are defined yet. Add the flows that **must** be covered by
> tests below; keep this list in sync with `forge.config.json` →
> `criticalPaths.paths`.

| Critical path        | Why it is critical | Covered by (test ref)   |
| -------------------- | ------------------ | ----------------------- |
| {{CRITICAL_PATH}}    | {{WHY}}            | {{TEST_REFERENCE}}      |

---

### Worked stub (generic — replace or delete)

## NFR01 — Performance

- NFR01.1 — Interactive screens respond in ≤ 2 s under normal load. **[Must]**
- NFR01.2 — Item search returns results in ≤ 1 s for up to 100k items. **[Should]**

> *Critical paths example (project decides):* "create item" and "authenticate"
> would be listed above with a test reference each — left empty here on purpose.
