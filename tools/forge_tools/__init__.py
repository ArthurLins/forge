"""Forge derived-docs generators.

Stack-neutral, domain-agnostic Python 3 generators that produce Forge's
"derived docs as code" (Principle 6): STATUS, the traceability matrix, the
changelog, and a pluggable sync-docs orchestrator. Every generator runs
WITHOUT a real project stack present and is driven by `forge.config.json`
rather than a hardcoded toolchain.

Runtime choice: Python 3 — the same runtime the prompt-suite engine already
requires (`prompts/next_prompt.py`), so Forge adds no extra toolchain just to
regenerate docs. Node is used only if a project declares a Node toolchain and
wires it in as an optional `docsHooks` entry.
"""
