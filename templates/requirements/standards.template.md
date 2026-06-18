<!--
  Forge — standards template (tier: full). Code & process standards. Genesis
  copies this to docs/requirements/standards.md, seeding it from the conventions
  in forge.config.json. Replace every {{PLACEHOLDER}}; delete these comments once
  filled.
-->

# {{PROJECT_NAME}} — Code & Process Standards

> **Purpose:** the consolidated standards — repository structure, naming
> conventions, testing strategy, CI/CD gates, versioning, and operations. The
> baseline values come from [`forge.config.json`](../../forge.config.json)
> (`conventions`, `ci`); this document is the human-readable expansion.

<!-- No ID prefix of its own; reference NFR/ADR IDs where a standard derives
     from a requirement or decision. -->

---

## 1. Repository structure

{{REPO_STRUCTURE}}
<!-- The top-level layout and what each area holds. -->

## 2. Naming & language conventions

| Aspect              | Convention                  | Config field                       |
| ------------------- | --------------------------- | ---------------------------------- |
| Docs / UI language  | {{DOCS_LANGUAGE}}           | `conventions.docsLanguage`         |
| Code language       | English                     | `conventions.codeLanguage`         |
| File names          | {{FILE_CASING}}            | `conventions.fileCasing`           |
| Types / classes     | {{TYPE_CASING}}            | `conventions.typeCasing`           |
| Variables / fns     | {{IDENTIFIER_CASING}}      | `conventions.identifierCasing`     |
| Constants           | {{CONSTANT_CASING}}        | `conventions.constantCasing`       |

## 3. Testing strategy

- {{TESTING_APPROACH}}
- **Critical paths** (from [non-functional.md](non-functional.md) /
  [business-rules.md](business-rules.md) and `forge.config.json` →
  `criticalPaths.paths`) **must** have tests; a change that breaks one does not
  integrate.

## 4. Traceability

Tag implementing code and tests with `@requirement <ID>` (and `@businessRule
<ID>`); the [traceability matrix](traceability.md) is generated from these tags
and CI fails if it is stale.

## 5. CI/CD gates

| Gate       | Command (`forge.config.json` → `ci.commands`) |
| ---------- | --------------------------------------------- |
| Lint       | {{CI_LINT}}                                   |
| Type-check | {{CI_TYPECHECK}}                              |
| Test       | {{CI_TEST}}                                   |
| Build      | {{CI_BUILD}}                                  |
| Docs fresh | {{CI_DOCS_CHECK}}                             |

## 6. Versioning & commits

- **Commits:** {{COMMIT_STYLE}} (default Conventional Commits;
  `conventions.commitStyle`).
- **Versioning:** {{VERSIONING_STRATEGY}}.

---

### Worked stub (generic — replace or delete)

> **Structure:** one app area + a shared area + tooling. **Naming:** Forge
> defaults (kebab-case files, PascalCase types, camelCase identifiers,
> UPPER_SNAKE_CASE constants). **Testing:** unit tests for logic; critical paths
> covered. **CI gates:** lint → type-check → test → build → docs-fresh, all from
> `forge.config.json`. **Commits:** Conventional Commits. **Versioning:**
> SemVer via tags.
