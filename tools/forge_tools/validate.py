#!/usr/bin/env python3
"""forge-validate — static integrity gate for a Forge-BUILT project.

DISTRIBUTABLE. Unlike ``selfcheck`` (which guards Forge's own constitution and is
self-only), this validator ships to adopters: it asserts that the *project they
built with Forge* is structurally intact, so a broken state machine, a dangling
traceability tag, a malformed Conventions Map, an invalid config, or stale
derived docs are caught before they merge.

It is **deterministic** and **stack-neutral**: every path and knob is read from
``forge.config.json`` (never hardcoded), and it runs on Python 3 alone — the same
neutral runtime the prompt-suite engine already requires. It must PASS trivially
on an empty / pre-genesis project: with no prompts and no requirements there is
nothing to violate.

Checks
------
  state-integrity          (hard) prompts/state.json: unique ids; every `file`
                                  exists; every `dependsOn` id exists; the
                                  dependency graph has no cycles; statuses are
                                  valid; `prompts/next_prompt.py` runs cleanly.
  requirement-tag-integrity (hard) every `@requirement`/`@rule` id referenced in
                                  source is DECLARED in docs/requirements/. A
                                  dangling tag fails; a declared requirement with
                                  no implementing tag is a WARNING, not a failure.
  conventions-integrity    (hard) only if docs/requirements/conventions.md exists:
                                  each `EC-` entry has the required fields and ids
                                  are unique.
  config-integrity         (hard) forge.config.json is valid JSON with the
                                  expected top-level keys.
  docs-freshness           (hard) derived docs are not stale (reuses the sync-docs
                                  --check logic).

Usage
-----
  python3 -m forge_tools.validate            # human-readable report (PASS/FAIL)
  python3 -m forge_tools.validate --check     # same, exit non-zero on hard fail

Warnings never fail the build. ``--check`` returns non-zero only on a hard
failure.
"""

import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

from . import common
from . import sync_docs as sync_docs_mod
from .requirements import parse_requirements
from .traceability import scan as scan_tags

STATE_REL = "prompts/state.json"
NEXT_PROMPT_REL = "prompts/next_prompt.py"
PROMPTS_DIR = "prompts"
CONFIG_REL = "forge.config.json"
CONVENTIONS_REL = "docs/requirements/conventions.md"

VALID_STATUSES = {"pending", "in_progress", "blocked", "done"}

# Top-level keys a Forge stack profile is expected to carry (the placeholder
# ships all of them; genesis fills their values). Documentation-hint keys
# beginning with "_" are ignored.
EXPECTED_CONFIG_KEYS = [
    "forgeVersion",
    "project",
    "stack",
    "conventions",
    "requirementTiers",
    "compliance",
    "docs",
    "traceability",
    "ci",
]

# Fields every EC entry in the Conventions Map must declare, matched against the
# bullet labels in the entry block (see templates/requirements/conventions.md).
REQUIRED_EC_FIELDS = ["Category", "Rule", "Applies to", "Status"]


# --------------------------------------------------------------------------- #
# Result model (mirrors selfcheck's CheckResult so the report reads the same)
# --------------------------------------------------------------------------- #

class CheckResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.failures: List[str] = []   # hard failures
        self.warnings: List[str] = []   # soft warnings (never fail)
        self.skipped: Optional[str] = None

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def skip(self, msg: str) -> None:
        self.skipped = msg

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        if self.skipped is not None:
            return "SKIP  {0}: {1}".format(self.name, self.skipped)
        status = "PASS" if self.ok else "FAIL"
        lines = ["{0}  {1}".format(status, self.name)]
        for f in self.failures:
            lines.append("        - FAIL: {0}".format(f))
        for w in self.warnings:
            lines.append("        - warn: {0}".format(w))
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _load_state() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Return (state, error). A missing file is NOT an error (pre-genesis)."""
    path = common.repo_path(STATE_REL)
    if not os.path.isfile(path):
        return {}, None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except json.JSONDecodeError as exc:
        return None, "{0} is not valid JSON: {1}".format(STATE_REL, exc)


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_state_integrity() -> CheckResult:
    res = CheckResult("state-integrity")
    state, err = _load_state()
    if err:
        res.fail(err)
        return res
    prompts: List[Dict[str, Any]] = (state or {}).get("prompts") or []

    # Empty / pre-genesis suite: trivially intact.
    if not prompts:
        return res

    ids: List[str] = []
    id_set: Set[str] = set()
    for p in prompts:
        pid = p.get("id")
        if pid is None:
            res.fail("a prompt entry is missing its `id`")
            continue
        pid = str(pid)
        if pid in id_set:
            res.fail("duplicate prompt id: {0}".format(pid))
        id_set.add(pid)
        ids.append(pid)

    # Statuses must be valid.
    for p in prompts:
        pid = str(p.get("id", "?"))
        status = p.get("status")
        if status not in VALID_STATUSES:
            res.fail(
                "prompt {0} has invalid status {1!r} (valid: {2})".format(
                    pid, status, ", ".join(sorted(VALID_STATUSES))
                )
            )

    # Every `file` must exist (relative to prompts/).
    for p in prompts:
        pid = str(p.get("id", "?"))
        rel = (p.get("file") or "").strip()
        if not rel:
            res.fail("prompt {0} has no `file`".format(pid))
            continue
        abs_path = common.repo_path(PROMPTS_DIR, rel)
        if not os.path.isfile(abs_path):
            res.fail(
                "prompt {0} -> file does not exist: {1}/{2}".format(
                    pid, PROMPTS_DIR, rel
                )
            )

    # Every `dependsOn` id must exist; collect edges for the cycle check.
    edges: Dict[str, List[str]] = {pid: [] for pid in id_set}
    for p in prompts:
        pid = str(p.get("id", "?"))
        for dep in p.get("dependsOn") or []:
            dep = str(dep)
            if dep not in id_set:
                res.fail(
                    "prompt {0} dependsOn unknown id: {1}".format(pid, dep)
                )
            elif pid in edges:
                edges[pid].append(dep)

    # Detect a cycle in the dependency graph (DFS with a recursion stack).
    cycle = _find_cycle(edges)
    if cycle:
        res.fail(
            "dependency cycle detected: {0}".format(" -> ".join(cycle))
        )

    # next_prompt.py must run without error.
    next_script = common.repo_path(NEXT_PROMPT_REL)
    if os.path.isfile(next_script):
        try:
            proc = subprocess.run(
                [sys.executable, next_script],
                cwd=common.REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
            )
        except OSError as exc:
            res.fail("could not run {0}: {1}".format(NEXT_PROMPT_REL, exc))
        else:
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "").strip()
                res.fail(
                    "{0} exited {1}: {2}".format(
                        NEXT_PROMPT_REL, proc.returncode, detail
                    )
                )
    return res


def _find_cycle(edges: Dict[str, List[str]]) -> Optional[List[str]]:
    """Return one cycle as a node list, or None. Deterministic (sorted order)."""
    WHITE, GREY, BLACK = 0, 1, 2
    color: Dict[str, int] = {n: WHITE for n in edges}

    def visit(node: str, stack: List[str]) -> Optional[List[str]]:
        color[node] = GREY
        stack.append(node)
        for nxt in sorted(edges.get(node, [])):
            if color.get(nxt, BLACK) == GREY:
                # Found a back-edge — slice the stack from nxt to close the loop.
                idx = stack.index(nxt)
                return stack[idx:] + [nxt]
            if color.get(nxt, BLACK) == WHITE:
                found = visit(nxt, stack)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for start in sorted(edges):
        if color[start] == WHITE:
            found = visit(start, [])
            if found:
                return found
    return None


def check_requirement_tag_integrity() -> CheckResult:
    res = CheckResult("requirement-tag-integrity")
    config = common.load_config()
    globs = common.traceability_globs(config)
    aliases = common.tag_aliases(config)

    declared = parse_requirements()
    declared_ids = {r.id for r in declared}

    raw_index = scan_tags(globs, aliases)
    referenced = set(raw_index.keys())

    # A tagged id is OK if it (or a declared ancestor, for dotted sub-ids) is
    # declared. Roll a dotted sub-id up to its nearest declared ancestor.
    def resolves(rid: str) -> bool:
        if rid in declared_ids:
            return True
        parent = rid
        while "." in parent:
            parent = parent.rsplit(".", 1)[0]
            if parent in declared_ids:
                return True
        return False

    dangling = sorted(rid for rid in referenced if not resolves(rid))
    for rid in dangling:
        res.fail(
            "tag references an undeclared requirement: {0} — declare it in "
            "docs/requirements/ or fix the tag".format(rid)
        )

    # A declared requirement with no implementing tag is a WARNING, not a fail.
    def is_covered(rid: str) -> bool:
        if rid in referenced:
            return True
        # A parent is covered if any dotted child id rolls up to it.
        for ref in referenced:
            cur = ref
            while "." in cur:
                cur = cur.rsplit(".", 1)[0]
                if cur == rid:
                    return True
        return False

    untagged = sorted(rid for rid in declared_ids if not is_covered(rid))
    for rid in untagged:
        res.warn("declared requirement has no implementing tag yet: {0}".format(rid))
    return res


def check_conventions_integrity() -> CheckResult:
    res = CheckResult("conventions-integrity")
    path = common.repo_path(CONVENTIONS_REL)
    if not os.path.isfile(path):
        res.skip("no {0} (Conventions Map not present)".format(CONVENTIONS_REL))
        return res

    text = common.read_text(path)
    lines = text.splitlines()

    # Each EC entry starts with a heading "### EC-01 — Title". Collect the body
    # up to the next heading and check the required field bullets are present.
    heading = re.compile(r"^#{2,6}\s+(EC-\d+)\b\s*[—-]\s*(.*)$")
    entries: List[Tuple[str, int]] = []  # (id, start line index)
    for i, line in enumerate(lines):
        m = heading.match(line.strip())
        if m:
            entries.append((m.group(1), i))

    if not entries:
        res.warn(
            "{0} exists but declares no EC- entries".format(CONVENTIONS_REL)
        )
        return res

    seen: Dict[str, int] = {}
    for idx, (ec_id, start) in enumerate(entries):
        if ec_id in seen:
            res.fail(
                "duplicate convention id {0} (first at line {1}, again at line "
                "{2})".format(ec_id, seen[ec_id] + 1, start + 1)
            )
        else:
            seen[ec_id] = start

        end = entries[idx + 1][1] if idx + 1 < len(entries) else len(lines)
        body = "\n".join(lines[start + 1:end])
        for field in REQUIRED_EC_FIELDS:
            # Match a bolded field label, e.g. "- **Category:**" / "**Rule (...)**".
            pattern = re.compile(
                r"\*\*\s*" + re.escape(field) + r"\b[^*]*:?\s*\*\*", re.IGNORECASE
            )
            if not pattern.search(body):
                res.fail(
                    "convention {0} is missing required field '{1}'".format(
                        ec_id, field
                    )
                )
    return res


def check_config_integrity() -> CheckResult:
    res = CheckResult("config-integrity")
    path = common.repo_path(CONFIG_REL)
    if not os.path.isfile(path):
        res.fail("{0} is missing".format(CONFIG_REL))
        return res
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        res.fail("{0} is not valid JSON: {1}".format(CONFIG_REL, exc))
        return res
    if not isinstance(data, dict):
        res.fail("{0} top-level value must be a JSON object".format(CONFIG_REL))
        return res
    for key in EXPECTED_CONFIG_KEYS:
        if key not in data:
            res.fail(
                "{0} is missing expected top-level key '{1}'".format(
                    CONFIG_REL, key
                )
            )
    return res


def check_docs_freshness() -> CheckResult:
    res = CheckResult("docs-freshness")
    # Reuse the sync-docs --check logic. Capture its stdout/stderr so the report
    # stays a single clean PASS/FAIL line; surface a short diagnostic on failure.
    import io
    from contextlib import redirect_stderr, redirect_stdout

    out_buf, err_buf = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = sync_docs_mod.main(["--check"])
    except Exception as exc:  # pragma: no cover - defensive
        res.fail("sync-docs --check raised: {0}".format(exc))
        return res
    if rc != 0:
        res.fail(
            "derived docs are stale — run `make forge-sync-docs` and commit "
            "the diff (run `make forge-sync-docs-check` to see it)"
        )
    return res


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def run_all() -> List[CheckResult]:
    return [
        check_state_integrity(),
        check_requirement_tag_integrity(),
        check_conventions_integrity(),
        check_config_integrity(),
        check_docs_freshness(),
    ]


def _render_report(results: List[CheckResult]) -> Tuple[str, bool, int]:
    """Return (report_text, all_hard_passed, warning_count)."""
    lines: List[str] = []
    lines.append("forge-validate — project integrity gate")
    lines.append("=" * 42)
    lines.append("")
    hard_ok = True
    warn_count = 0
    for r in results:
        lines.append(r.render())
        if not r.ok:
            hard_ok = False
        warn_count += len(r.warnings)
    lines.append("")
    lines.append("-" * 42)
    if hard_ok:
        summary = "RESULT: PASS"
        if warn_count:
            summary += " ({0} warning(s) to review)".format(warn_count)
    else:
        failing = [r.name for r in results if not r.ok]
        summary = "RESULT: FAIL — {0}".format(", ".join(failing))
    lines.append(summary)
    return "\n".join(lines) + "\n", hard_ok, warn_count


def main(argv: List[str]) -> int:
    check = "--check" in argv
    results = run_all()
    report, hard_ok, _warn = _render_report(results)
    sys.stdout.write(report)
    if check and not hard_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
