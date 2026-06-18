# Forge — vision (self)

## Purpose

**Forge** is a replicable, **stack-neutral**, **domain-agnostic**,
agent-orchestrated, spec-driven development methodology. An adopter copies it into
an empty project, runs the genesis interview, and lets agents build the project
against a single source of truth — one self-contained prompt at a time.

The full statement of what Forge *is* and the non-negotiable principles it upholds
live in the constitution, **[`FORGE.md`](../../FORGE.md)**. This document does not
duplicate them; it frames the purpose of the **self-development** workspace.

## Why a self-development workspace exists

Forge ships a methodology for maintaining *other* projects rigorously. The risk
for a framework is that it does not hold *itself* to the same bar — its own
changes drift, its catalogs go stale, domain or stack residue creeps in.

The `self/` workspace closes that gap: Forge maintains Forge **with** Forge. A
change to the framework is scoped against the constitution, recorded as a work
item, applied minimally, gated by `forge-selfcheck`, and landed via
`/forge-contribute`. Because the framework is improved *using itself*, an
improvement is — by construction — already applied *to* itself. That is the
meta-circular property: **use the library to maintain itself; when it is updated,
it is already updated for itself.**

## Non-goals

- This workspace does **not** add a stack or a domain to Forge — Forge stays
  stack-neutral and domain-agnostic (constitution, principles 1–2 and the
  `domain-agnostic`/`stack-neutral` invariants).
- It is **not** shipped to adopters — it is excluded from the export per
  [`../../forge.manifest.json`](../../forge.manifest.json).
