# Forge — task runner for the derived-docs generators.
#
# Runtime is Python 3 (the same the prompt-suite engine already requires via
# prompts/next_prompt.py), so Forge adds no stack to regenerate docs. The
# generators live in tools/forge_tools/ and are run as a module with PYTHONPATH
# pointed at tools/. Stack-specific steps are NOT here — a project wires them in
# via forge.config.json -> docsHooks, which `forge-sync-docs` invokes.
#
# Usage:
#   make forge-status            make forge-status:check  (and so on)
#   make forge-sync-docs         make forge-sync-docs:check
#   make help

PYTHON ?= python3
FORGE  := PYTHONPATH=tools $(PYTHON) -m forge_tools

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show the available targets
	@echo "Forge derived-docs tasks (runtime: $(PYTHON)):"
	@echo "  make forge-status            regenerate prompts/STATUS.md"
	@echo "  make forge-status-check      fail if STATUS.md is stale"
	@echo "  make forge-traceability      regenerate the traceability matrix"
	@echo "  make forge-traceability-check  fail if the matrix is stale"
	@echo "  make forge-changelog         regenerate the changelog"
	@echo "  make forge-changelog-check   fail if the changelog is stale"
	@echo "  make forge-sync-docs         run all generators + declared stack hooks"
	@echo "  make forge-sync-docs-check   fail on any drift (CI docs-freshness gate)"
	@echo "  make forge-docs-gen          core text artifacts only (no stack hooks)"
	@echo ""
	@echo "Self-hosting (self-only — maintaining Forge itself):"
	@echo "  make forge-selfcheck         constitution gate: selfcheck + docs-fresh (fails on drift)"
	@echo "  make forge-selfcheck-report  human-readable selfcheck (non-failing)"
	@echo "  make forge-export DEST=<dir> produce a clean adopter copy of Forge"
	@echo ""
	@echo "Colon-style aliases also work: 'make forge-status:check', etc."

# --- core generators -------------------------------------------------------- #

.PHONY: forge-status
forge-status: ## Regenerate prompts/STATUS.md from state.json
	@$(FORGE) status

.PHONY: forge-status-check forge-status\:check
forge-status-check forge-status\:check: ## Fail if STATUS.md is stale
	@$(FORGE) status --check

.PHONY: forge-traceability
forge-traceability: ## Regenerate the traceability matrix
	@$(FORGE) traceability

.PHONY: forge-traceability-check forge-traceability\:check
forge-traceability-check forge-traceability\:check: ## Fail if the matrix is stale
	@$(FORGE) traceability --check

.PHONY: forge-changelog
forge-changelog: ## Regenerate the changelog
	@$(FORGE) changelog

.PHONY: forge-changelog-check forge-changelog\:check
forge-changelog-check forge-changelog\:check: ## Fail if the changelog is stale
	@$(FORGE) changelog --check

# --- orchestrator ----------------------------------------------------------- #

.PHONY: forge-sync-docs
forge-sync-docs: ## Run all core generators + any declared stack hooks
	@$(FORGE) sync-docs

.PHONY: forge-sync-docs-check forge-sync-docs\:check
forge-sync-docs-check forge-sync-docs\:check: ## Fail on any drift (CI docs-freshness gate)
	@$(FORGE) sync-docs --check

.PHONY: forge-docs-gen
forge-docs-gen: ## Core text artifacts only (skip stack hooks) — the "docs-gen" subset
	@$(FORGE) sync-docs --core-only

# --- self-hosting (self-only) ----------------------------------------------- #
# These targets maintain FORGE ITSELF. They are part of Forge's self-development
# tooling (forge.manifest.json -> selfOnly) and are NOT shipped to adopters.

.PHONY: forge-selfcheck
forge-selfcheck: ## Constitution gate — run selfcheck AND the docs-freshness check (fails on drift)
	@$(FORGE) selfcheck --check
	@$(FORGE) sync-docs --check

.PHONY: forge-selfcheck-report
forge-selfcheck-report: ## Human-readable selfcheck report (never fails — for inspection)
	@$(FORGE) selfcheck

.PHONY: forge-export
forge-export: ## Produce a clean adopter copy of Forge: make forge-export DEST=<dir>
	@if [ -z "$(DEST)" ]; then \
		echo "usage: make forge-export DEST=<path>"; exit 2; \
	fi
	@$(FORGE) export --dest "$(DEST)"
