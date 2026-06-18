<!--
  Golden example — the TRACEABILITY link (illustrative).
  This is link #5 of the loop: the row the traceability TOOL emits for the Notes
  feature from the @requirement / @rule tags in code/. GENERATED, never written by
  hand — shown here only to close the loop. Format mirrors
  tools/forge_tools/traceability.py output.
-->

# Golden example — traceability row (generated)

> ⚠️ **GENERATED — never hand-edited.** In a real project the traceability tool
> scans the `@requirement` / `@rule` tags across the source (config:
> `forge.config.json → traceability.{globs,tagAliases}`) and writes the matrix to
> `<generatedDir>/traceability.md`. The Notes feature contributes the rows below.
> CI fails if the committed matrix is stale (Principle 6).

## What the tool sees

| Tag in source            | In file                            | Counts as |
| ------------------------ | ---------------------------------- | --------- |
| `@requirement FR01`      | `code/create-note.pseudo`          | code      |
| `@rule BR01`             | `code/create-note.pseudo`          | code      |
| `@requirement FR01`      | `code/create-note.spec.pseudo`     | test (`.spec.`) |
| `@rule BR01`             | `code/create-note.spec.pseudo`     | test (`.spec.`) |

## The emitted row

Because each id has **both** a code file and a test file tagged, its status is
`covered`:

| Requirement ID | Source doc        | Code                                                    | Tests                                                | Status  |
| -------------- | ----------------- | ------------------------------------------------------- | ---------------------------------------------------- | ------- |
| FR01           | `functional.md`   | `examples/golden-example/code/create-note.pseudo`       | `examples/golden-example/code/create-note.spec.pseudo` | covered |
| BR01           | `business-rules.md` | `examples/golden-example/code/create-note.pseudo`     | `examples/golden-example/code/create-note.spec.pseudo` | covered |

> Status legend (from the tool): `covered` (code **and** test) · `partial` (one
> side only) · `gap` (neither). Had the test been missing, `FR01` would show
> `partial` — a visible, enforceable coverage gap, not a silent one (Principle 7).
>
> Note: this row is *illustrative*. The shipped, auto-generated
> `docs/generated/traceability.md` lists only requirements **declared** in a real
> project's `docs/requirements/`; `FR01`/`BR01` here are inlined in
> [`requirement.md`](requirement.md) for the example, so they appear in this
> walkthrough rather than in Forge's own empty matrix.
