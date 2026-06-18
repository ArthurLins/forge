#!/usr/bin/env python3
"""forge-export — produce a clean adopter copy of Forge.

SELF-ONLY. Part of Forge's self-development tooling (see ``forge.manifest.json``
-> ``selfOnly``); not shipped to adopters. This is the "no copy-paste" path: one
command yields a clean Forge for a new project, derived from the same source Forge
maintains in place.

What it does
------------
1. Read ``forge.manifest.json`` for ``selfOnly`` (paths to EXCLUDE) and
   ``resetOnExport`` (seeds to re-blank).
2. Copy every git-tracked file EXCEPT the ``selfOnly`` paths into ``DEST``.
3. Apply ``resetOnExport``:
     - DEST ``prompts/state.json``  -> the empty seed,
     - DEST ``docs/requirements/``  -> only ``.gitkeep``,
     - DEST ``docs/generated/``     -> emptied (kept with a ``.gitkeep``).
4. Print a summary of included / excluded paths.

Runtime: Python 3 only — no project stack assumed.

Usage
-----
  python3 -m forge_tools.export --dest <path>
  make forge-export DEST=<path>
"""

import json
import os
import shutil
import sys
from typing import Any, Dict, List, Optional

from . import common
from . import selfcheck

EMPTY_STATE_SEED = (
    "{\n"
    '  "_comment": "Forge prompt-suite state machine. Empty seed — genesis '
    "(/forge-init) and phase planning (/forge-plan-phase) populate phases[] and "
    "prompts[]. next_prompt.py reads this file to select the next eligible prompt "
    "by topological dependsOn order. Field-by-field documentation: state.schema.md."
    " The leading underscore key is a documentation hint and may be removed once "
    'filled.",\n'
    '  "project": "",\n'
    '  "version": "0",\n'
    '  "updatedAt": "",\n'
    '  "legend": {\n'
    '    "status": ["pending", "in_progress", "blocked", "done"]\n'
    "  },\n"
    '  "phases": [],\n'
    '  "prompts": []\n'
    "}\n"
)


def _load_manifest() -> Dict[str, Any]:
    path = common.repo_path(selfcheck.MANIFEST_REL)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _git_tracked() -> List[str]:
    import subprocess

    out = subprocess.check_output(
        ["git", "ls-files"], cwd=common.REPO_ROOT, encoding="utf-8"
    )
    return [
        line.strip().replace(os.sep, "/")
        for line in out.splitlines()
        if line.strip()
    ]


def _copy(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    shutil.copy2(src, dst)


def _ensure_dir_with_gitkeep(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    for entry in os.listdir(path):
        full = os.path.join(path, entry)
        if os.path.isdir(full):
            shutil.rmtree(full)
        else:
            os.remove(full)
    open(os.path.join(path, ".gitkeep"), "w", encoding="utf-8").close()


def export(dest: str) -> int:
    manifest = _load_manifest()
    if not manifest:
        sys.stderr.write("[export] forge.manifest.json is missing — aborting.\n")
        return 1
    self_only = [str(e) for e in (manifest.get("selfOnly") or [])]
    reset = manifest.get("resetOnExport") or {}

    dest_abs = os.path.abspath(dest)
    if os.path.exists(dest_abs) and os.listdir(dest_abs):
        sys.stderr.write(
            "[export] DEST '{0}' exists and is not empty — aborting "
            "(choose a fresh directory).\n".format(dest_abs)
        )
        return 1

    tracked = _git_tracked()
    included: List[str] = []
    excluded: List[str] = []
    for rel in tracked:
        if selfcheck._is_self_only(rel, self_only):
            excluded.append(rel)
            continue
        src = common.repo_path(rel)
        if not os.path.isfile(src):
            continue
        _copy(src, os.path.join(dest_abs, rel))
        included.append(rel)

    # --- apply resetOnExport ------------------------------------------------ #
    reset_actions: List[str] = []

    # prompts/state.json -> empty seed
    if "prompts/state.json" in reset:
        state_dst = os.path.join(dest_abs, "prompts", "state.json")
        os.makedirs(os.path.dirname(state_dst), exist_ok=True)
        with open(state_dst, "w", encoding="utf-8") as fh:
            fh.write(EMPTY_STATE_SEED)
        reset_actions.append("prompts/state.json -> empty seed")

    # docs/requirements/ -> only .gitkeep
    if "docs/requirements/" in reset or "docs/requirements" in reset:
        req_dst = os.path.join(dest_abs, "docs", "requirements")
        _ensure_dir_with_gitkeep(req_dst)
        reset_actions.append("docs/requirements/ -> only .gitkeep")

    # docs/generated/ -> emptied (kept with .gitkeep)
    if "docs/generated/" in reset or "docs/generated" in reset:
        gen_dst = os.path.join(dest_abs, "docs", "generated")
        _ensure_dir_with_gitkeep(gen_dst)
        reset_actions.append("docs/generated/ -> emptied (.gitkeep)")

    # --- summary ------------------------------------------------------------ #
    sys.stdout.write("forge-export -> {0}\n".format(dest_abs))
    sys.stdout.write("=" * 42 + "\n")
    sys.stdout.write("Included: {0} git-tracked file(s).\n".format(len(included)))
    sys.stdout.write("Excluded (selfOnly): {0} file(s):\n".format(len(excluded)))
    for rel in sorted(excluded):
        sys.stdout.write("  - {0}\n".format(rel))
    if not excluded:
        sys.stdout.write("  (none — selfOnly matched no tracked files)\n")
    sys.stdout.write("Reset seeds:\n")
    for action in reset_actions:
        sys.stdout.write("  - {0}\n".format(action))
    sys.stdout.write(
        "\nDone. A clean Forge copy is at: {0}\n".format(dest_abs)
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    dest: Optional[str] = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--dest":
            i += 1
            if i < len(args):
                dest = args[i]
        elif a.startswith("--dest="):
            dest = a[len("--dest="):]
        elif not a.startswith("-") and dest is None:
            dest = a
        i += 1
    if not dest:
        sys.stderr.write(
            "usage: python3 -m forge_tools.export --dest <path>\n"
            "   or: make forge-export DEST=<path>\n"
        )
        return 2
    return export(dest)


if __name__ == "__main__":
    sys.exit(main())
