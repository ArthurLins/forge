<!--
  Forge — Conventional Commits config template (for the CI `commits` job).

  GENERATED-FROM-TEMPLATE. The `commits` job in `forge-ci.yml.template` calls a
  project-supplied checker (`{{COMMIT_LINT_COMMAND}}`) that validates every PR
  commit message against the Conventional Commits convention. This file is a
  STACK-NEUTRAL specification of what that config must enforce, plus an
  illustrative concrete form. Forge does NOT prescribe a particular checker tool;
  use whatever your stack offers. Genesis records the choice in
  `forge.config.json → ci.provider` / the CI setup.
-->

# Conventional Commits — checker config (template)

This is the contract the `commits` CI job enforces (Forge **Principle 8**). Pick
any checker your stack provides; it must accept the message grammar below and run
over the PR's commit range (`COMMIT_RANGE_FROM..COMMIT_RANGE_TO`, exported by the
workflow).

## Message grammar (the rules to enforce)

```
<type>(<optional scope>): <subject>

<optional body>

<optional footer>
```

- **type** — one of the allowed set (see below); required; lower-case.
- **scope** — optional; lower-case; the area touched (e.g. the feature/module
  name).
- **subject** — required; imperative mood; no trailing period; bounded length
  (a ~72-char header is a common cap).

### Allowed types

| Type       | Use for                                            |
| ---------- | -------------------------------------------------- |
| `feat`     | A new capability.                                  |
| `fix`      | A bug fix.                                          |
| `docs`     | Documentation only.                                |
| `refactor` | Code change that neither fixes a bug nor adds one. |
| `test`     | Adding or correcting tests.                        |
| `chore`    | Tooling, deps, derived-doc syncs, housekeeping.    |
| `build`    | Build system or external dependencies.             |
| `ci`       | CI configuration and scripts.                      |
| `perf`     | Performance improvement.                           |
| `revert`   | Reverting a previous commit.                       |

> A project MAY extend this set in its own config, but the `commits` job must
> reject anything outside the allowed set it declares. Breaking changes use the
> `!` marker (`feat!:`) or a `BREAKING CHANGE:` footer, per SemVer.

## Illustrative concrete config (replace with your stack's equivalent)

The following is **one** way to express the rules above with a popular checker.
It is an EXAMPLE only — do not assume this tool; substitute your stack's
checker and its native config format.

```jsonc
// Example config consumed by a Conventional-Commits checker.
{
  "extends": ["<your-conventional-config-preset>"],
  "rules": {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "docs", "refactor", "test", "chore", "build", "ci", "perf", "revert"]
    ],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "header-max-length": [2, "always", 72]
  }
}
```

## Wiring it into CI

In `forge-ci.yml.template`, set `{{COMMIT_LINT_COMMAND}}` to your checker's
invocation. It must lint the range the workflow exports, e.g. conceptually:

```bash
<your-commit-checker> --from "$COMMIT_RANGE_FROM" --to "$COMMIT_RANGE_TO"
```

If your checker reads a config file, commit that file at the path the tool
expects and keep its allowed `type` set aligned with the table above.
