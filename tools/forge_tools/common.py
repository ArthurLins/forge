"""Shared helpers for the Forge derived-docs generators.

Everything here is stack-neutral and reads knobs from `forge.config.json`.
The module locates the repository root by walking up from this file until it
finds `forge.config.json` (the project marker), so the tools work regardless of
the current working directory.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
# Repository layout
# --------------------------------------------------------------------------- #

def _this_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _walk_up_for_marker(start: str) -> Optional[str]:
    cur = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(cur, "forge.config.json")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def find_repo_root(start: Optional[str] = None) -> str:
    """Locate the repository root (the directory holding ``forge.config.json``).

    Resolution order, so the tools operate on the *project*, not on wherever the
    package happens to live:

    1. ``$FORGE_ROOT`` if set (explicit override, used by tests / wrappers).
    2. Walk up from the current working directory (the project being operated
       on). This is what makes the generators work in any project that copied
       them in.
    3. Walk up from this file's location (covers the in-repo case directly).
    4. Two levels above this file (``tools/forge_tools/`` -> repo root) as a
       last resort, so an unconfigured checkout still resolves.
    """
    env = os.environ.get("FORGE_ROOT")
    if env:
        return os.path.abspath(env)
    if start is not None:
        found = _walk_up_for_marker(start)
        if found:
            return found
    found = _walk_up_for_marker(os.getcwd())
    if found:
        return found
    found = _walk_up_for_marker(_this_dir())
    if found:
        return found
    return os.path.dirname(os.path.dirname(_this_dir()))


REPO_ROOT = find_repo_root()


def repo_path(*parts: str) -> str:
    """Absolute path inside the repository."""
    return os.path.join(REPO_ROOT, *parts)


def rel_to_repo(path: str) -> str:
    """Path relative to the repo root, with forward slashes (stable on all OSes)."""
    rel = os.path.relpath(path, REPO_ROOT)
    return rel.replace(os.sep, "/")


# --------------------------------------------------------------------------- #
# forge.config.json
# --------------------------------------------------------------------------- #

# Stack-neutral defaults. A project overrides any of these in forge.config.json;
# Forge never assumes a stack, so the defaults must run with no stack present.
DEFAULT_GENERATED_DIR = "docs/generated"

# Default scan targets are the conventional locations a project's OWN source
# lives. Forge's framework folders (templates/, tools/, docs/) are intentionally
# excluded so the tool does not pick up tag *examples* in Forge's own prose. A
# project widens or narrows this via traceability.globs.
DEFAULT_TRACEABILITY_GLOBS = [
    "apps/**/*",
    "libs/**/*",
    "src/**/*",
    "packages/**/*",
    "modules/**/*",
    "examples/**/*",
]

# Maps a tag keyword found in source -> the kind of link it records.
# "requirement" links a requirement id (FR/NFR/CR/UC/EN); "rule" links a
# business-rule id (BR). Projects may add aliases via traceability.tagAliases.
DEFAULT_TAG_ALIASES = {
    "requirement": ["requirement", "req"],
    "rule": ["rule", "businessRule", "businessrule"],
}


def load_config() -> Dict[str, Any]:
    """Load ``forge.config.json`` if present; otherwise return ``{}``.

    The tools must run on a fresh checkout where genesis has not filled the
    config, so a missing file is not an error.
    """
    path = repo_path("forge.config.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            sys.stderr.write(
                "[forge] forge.config.json is not valid JSON: {}\n".format(exc)
            )
            return {}


def project_name(config: Optional[Dict[str, Any]] = None) -> str:
    cfg = config if config is not None else load_config()
    name = ((cfg.get("project") or {}).get("name") or "").strip()
    return name or "Project"


def generated_dir(config: Optional[Dict[str, Any]] = None) -> str:
    cfg = config if config is not None else load_config()
    docs = cfg.get("docs") or {}
    value = docs.get("generatedDir") or DEFAULT_GENERATED_DIR
    return value


def traceability_globs(config: Optional[Dict[str, Any]] = None) -> List[str]:
    cfg = config if config is not None else load_config()
    trace = cfg.get("traceability") or {}
    globs = trace.get("globs")
    if isinstance(globs, list) and globs:
        return [str(g) for g in globs]
    return list(DEFAULT_TRACEABILITY_GLOBS)


def tag_aliases(config: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
    """Return ``{kind: [keyword, ...]}`` mapping for tag detection.

    Project-declared aliases (``traceability.tagAliases``) are merged on top of
    the stack-neutral defaults. Keys are link kinds (``requirement``/``rule``).
    """
    cfg = config if config is not None else load_config()
    trace = cfg.get("traceability") or {}
    aliases = {k: list(v) for k, v in DEFAULT_TAG_ALIASES.items()}
    declared = trace.get("tagAliases") or {}
    if isinstance(declared, dict):
        for kind, keywords in declared.items():
            if not isinstance(keywords, list):
                continue
            bucket = aliases.setdefault(kind, [])
            for kw in keywords:
                if kw not in bucket:
                    bucket.append(str(kw))
    return aliases


def docs_hooks(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return the declared stack hooks (``docsHooks[]``), or ``[]``.

    Each hook is ``{"name": str, "command": str, ["check": str], ["cwd": str]}``.
    With none declared, sync-docs runs only the stack-neutral core generators.
    """
    cfg = config if config is not None else load_config()
    hooks = cfg.get("docsHooks")
    if isinstance(hooks, list):
        return [h for h in hooks if isinstance(h, dict)]
    return []


# --------------------------------------------------------------------------- #
# Generator I/O — write vs. --check
# --------------------------------------------------------------------------- #

def read_text(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _unified_diff(current: str, expected: str, label: str) -> str:
    import difflib

    diff = difflib.unified_diff(
        current.splitlines(keepends=True),
        expected.splitlines(keepends=True),
        fromfile="{} (on disk)".format(label),
        tofile="{} (expected)".format(label),
    )
    return "".join(diff)


def emit(content: str, out_path: str, check: bool, label: str) -> int:
    """Write ``content`` to ``out_path``, or, in ``check`` mode, compare.

    Returns a process exit code: ``0`` when in sync (or written), ``1`` when a
    drift is detected in ``--check`` mode. In check mode a unified diff is
    printed to stderr so CI logs show exactly what is stale.
    """
    rel = rel_to_repo(out_path)
    if check:
        current = read_text(out_path)
        if current != content:
            sys.stderr.write(
                "[{0}] STALE: {1} does not match the source.\n"
                "Run the sync-docs orchestrator and commit the diff.\n".format(
                    label, rel
                )
            )
            diff = _unified_diff(current, content, rel)
            if diff:
                sys.stderr.write(diff)
                if not diff.endswith("\n"):
                    sys.stderr.write("\n")
            return 1
        sys.stdout.write("[{0}] OK: {1} is up to date.\n".format(label, rel))
        return 0

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    sys.stdout.write("[{0}] wrote {1}\n".format(label, rel))
    return 0


def parse_common_args(
    argv: List[str], default_out: str
) -> Tuple[bool, str]:
    """Parse the shared ``--check`` / ``--out FILE`` flags.

    Returns ``(check, out_path_absolute)``.
    """
    check = False
    out = default_out
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--check":
            check = True
        elif arg == "--out":
            i += 1
            if i < len(argv):
                out = argv[i]
        i += 1
    out_abs = out if os.path.isabs(out) else repo_path(out)
    return check, out_abs
