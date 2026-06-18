# Forge — self-development requirements (index)

This is the **source of truth for Forge's own evolution** — lean by design
(heeding Fowler: avoid spec bloat; document the decisions and capabilities, not
every detail). It describes the framework as a *thing being maintained*, while the
framework's **constitution** is, and remains, [`FORGE.md`](../../FORGE.md).

> **The constitution is `FORGE.md`.** Its eight principles are non-negotiable and
> are *not* restated here. These documents record Forge's **capabilities**
> (`FR-S*`) and its **framework decisions** (`ADR-S*`); none may contradict the
> constitution.

## Documents (taxonomy)

| Doc                              | Holds                                                        |
| -------------------------------- | ----------------------------------------------------------- |
| [`vision.md`](vision.md)         | Forge's purpose (points to `FORGE.md`).                     |
| [`functional.md`](functional.md) | the framework's capabilities as `FR-S*` items (one per skill/tool/template family). |
| [`decisions.md`](decisions.md)   | the framework ADRs (`ADR-S*`) — self-hosting model, manifest + export, the selfcheck gate, `/forge-contribute`. |

## ID taxonomy (self-development)

| Prefix    | Kind                                  | Document        |
| --------- | ------------------------------------- | --------------- |
| **FR-S**  | Framework capability (self)           | `functional.md` |
| **ADR-S** | Framework architecture decision (self)| `decisions.md`  |

> The `-S` suffix marks these as **self-development** ids, distinct from a
> project's `FR/NFR/BR/CR/UC/EN` taxonomy. They never appear in an adopter export.
