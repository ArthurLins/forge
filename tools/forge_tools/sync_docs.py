#!/usr/bin/env python3
"""sync-docs orchestrator — regenerate all derived docs, idempotently.

Runs the **stack-neutral core generators** (status, traceability, changelog)
and then any **stack hooks** the project declares in ``forge.config.json`` under
``docsHooks``. A hook is just a shell command the project supplies (e.g. build
an OpenAPI contract, regenerate an API client); if none are declared, the hook
phase is skipped and sync-docs still succeeds. This is how Forge keeps the
PedPlus split — text artifacts here, stack-specific steps as optional plugins —
without hardcoding any stack (Forge Principle 6).

A ``--check`` mode runs every generator in check mode and fails on ANY drift in
the generated docs and ``prompts/STATUS.md`` — suitable for a CI docs-freshness
gate.

Usage:
  python3 -m forge_tools.sync_docs              # regenerate everything
  python3 -m forge_tools.sync_docs --check       # fail on any drift (CI)
  python3 -m forge_tools.sync_docs --core-only    # skip declared stack hooks

docsHooks[] entry shape (all in forge.config.json):
  {
    "name": "openapi",                 # label shown in logs
    "command": "<shell to regenerate>", # run in normal mode
    "check": "<shell to verify>",       # OPTIONAL; run in --check mode.
                                        #   If absent, --check re-runs `command`.
    "cwd": "<relative dir>"             # OPTIONAL; defaults to repo root
  }
"""

import os
import subprocess
import sys
from typing import Any, Dict, List

from . import common
from . import status as status_mod
from . import traceability as trace_mod
from . import changelog as changelog_mod


def _run_core(check: bool) -> bool:
    """Run the three core generators. Returns True if all are in sync/written."""
    ok = True
    flags = ["--check"] if check else []
    # status writes a fixed path; traceability/changelog default into generatedDir.
    if status_mod.main(list(flags)) != 0:
        ok = False
    if trace_mod.main(list(flags)) != 0:
        ok = False
    if changelog_mod.main(list(flags)) != 0:
        ok = False
    return ok


def _run_hook(hook: Dict[str, Any], check: bool) -> bool:
    name = hook.get("name") or "hook"
    command = hook.get("command")
    if check:
        # Prefer an explicit verification command; otherwise re-run the writer
        # (idempotent generators leave the tree unchanged when already fresh).
        command = hook.get("check") or hook.get("command")
    if not command:
        sys.stderr.write("[sync-docs] hook '{}' has no command; skipping.\n".format(name))
        return True
    cwd = hook.get("cwd")
    workdir = common.repo_path(cwd) if cwd else common.REPO_ROOT
    label = "{} (check)".format(name) if check else name
    sys.stdout.write("[sync-docs] running stack hook: {}\n".format(label))
    try:
        result = subprocess.run(command, shell=True, cwd=workdir)
    except OSError as exc:
        sys.stderr.write("[sync-docs] FAILED hook '{}': {}\n".format(name, exc))
        return False
    if result.returncode != 0:
        sys.stderr.write(
            "[sync-docs] FAILED hook '{}' (exit {}).\n".format(name, result.returncode)
        )
        return False
    return True


def _run_hooks(check: bool) -> bool:
    hooks = common.docs_hooks()
    if not hooks:
        sys.stdout.write(
            "[sync-docs] no docsHooks declared in forge.config.json; "
            "core generators only.\n"
        )
        return True
    ok = True
    for hook in hooks:
        if not _run_hook(hook, check):
            ok = False
    return ok


def _report_diff() -> None:
    gen_dir = common.generated_dir()
    paths = [gen_dir, "prompts/STATUS.md"]
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"] + paths,
            cwd=common.REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
        )
        diff = (result.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return
    if diff:
        sys.stdout.write("\n[sync-docs] documentation diff:\n" + diff + "\n")
    else:
        sys.stdout.write("\n[sync-docs] nothing to update (idempotent).\n")


def main(argv: List[str]) -> int:
    check = "--check" in argv
    core_only = "--core-only" in argv

    ok = _run_core(check)
    if not core_only:
        ok = _run_hooks(check) and ok

    if not check:
        _report_diff()

    if not ok:
        sys.stderr.write(
            "\n[sync-docs] {}\n".format(
                "Derived docs are STALE. Run the sync-docs orchestrator and commit."
                if check
                else "One or more steps failed (see above)."
            )
        )
        return 1
    sys.stdout.write(
        "\n[sync-docs] {}\n".format(
            "OK: all derived docs are up to date." if check else "Done."
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
