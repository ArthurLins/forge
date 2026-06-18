#!/usr/bin/env python3
"""Unified CLI: ``python3 -m forge_tools <command> [flags]``.

Commands:
  status         regenerate prompts/STATUS.md
  traceability   regenerate the traceability matrix
  changelog      regenerate the changelog
  sync-docs      run the full orchestrator (core generators + stack hooks)
  selfcheck      enforce Forge's own constitution (self-only gate)
  export         produce a clean adopter copy of Forge (self-only)

Each command accepts the same flags as its module (``--check``, ``--out`` where
applicable). This entrypoint lets Forge run the tools with no install step:
``python3 -m forge_tools sync-docs --check``.
"""

import sys
from typing import List


def _usage() -> int:
    sys.stderr.write(
        "usage: python3 -m forge_tools "
        "{status|traceability|changelog|sync-docs|selfcheck|export} [flags]\n"
    )
    return 2


def main(argv: List[str]) -> int:
    if not argv:
        return _usage()
    command = argv[0]
    rest = argv[1:]

    if command == "status":
        from . import status

        return status.main(rest)
    if command == "traceability":
        from . import traceability

        return traceability.main(rest)
    if command == "changelog":
        from . import changelog

        return changelog.main(rest)
    if command in ("sync-docs", "sync_docs"):
        from . import sync_docs

        return sync_docs.main(rest)
    if command == "selfcheck":
        from . import selfcheck

        return selfcheck.main(rest)
    if command == "export":
        from . import export

        return export.main(rest)

    sys.stderr.write("[forge] unknown command: {}\n".format(command))
    return _usage()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
