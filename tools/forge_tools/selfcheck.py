#!/usr/bin/env python3
"""forge-selfcheck — enforce Forge's own constitution as automated assertions.

SELF-ONLY. This checker is part of Forge's self-development tooling (see
``forge.manifest.json`` -> ``selfOnly``); it is NOT shipped to adopters. It keeps
Forge honest to the eight principles in ``FORGE.md`` by asserting a set of
invariants on every change to the framework.

Runtime: Python 3 only — no project stack assumed (same neutral runtime the
prompt-suite engine already requires). It reads ``forge.manifest.json`` to learn
the self-only / distributable boundary.

Checks
------
  seed-purity         (hard) root prompts/state.json has empty phases & prompts;
                             docs/requirements/ contains only .gitkeep.
  registration-parity (hard) every DISTRIBUTABLE skill/command appears in BOTH
                             the AGENTS.md catalog table and the skills catalog.
  domain-residue      (hard) no business-domain / medical / PedPlus tokens in
                             distributable files.
  stack-residue       (warn) hardcoded stack tokens in distributable files are
                             reported for review — they NEVER fail the build.
  manifest-coverage   (hard) every manifest.selfOnly path exists (no stale entry).
  skill-structure     (hard) each skill SKILL.md has name+description frontmatter;
                             each command .md has a description.

Usage
-----
  python3 -m forge_tools.selfcheck            # human-readable report (PASS/FAIL)
  python3 -m forge_tools.selfcheck --check     # same, exit non-zero on hard fail

Warnings never fail the build. ``--check`` returns non-zero only on a hard
failure.
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from . import common

MANIFEST_REL = "forge.manifest.json"
STATE_REL = "prompts/state.json"
REQUIREMENTS_DIR = "docs/requirements"
AGENTS_REL = "AGENTS.md"
SKILLS_CATALOG_REL = "docs/guides/skills-catalog.md"
SKILLS_DIR = ".claude/skills"
COMMANDS_DIR = ".claude/commands"
GENERATED_DIR = "docs/generated"
GOLDEN_EXAMPLE_DIR = "examples/golden-example"

# Business-domain / medical / PedPlus residue. A hit in any distributable file
# means Forge is no longer domain-agnostic (FORGE.md, "domain-agnostic"). These
# are matched case-insensitively as substrings.
DOMAIN_TOKENS = [
    "LGPD",
    "SBIS",
    "TISS",
    "CFM",
    "ICP-Brasil",
    "vacina",
    "pediatr",
    "dosage",
    "percentile",
    "PedPlus",
]

# Hardcoded stack tokens — Forge is stack-neutral, but these may legitimately
# appear in COMMENTED illustrative examples, so they are reported as WARNINGS to
# review, never as failures (FORGE.md, "stack-neutral"; the CI template lists
# several on purpose as "illustrative only").
STACK_TOKENS = [
    "Nx",
    "NestJS",
    "Prisma",
    "Jest",
    "React",
    "Keycloak",
    "Hey API",
]

# Only scan textual files for residue; skip binary-ish extensions.
SKIP_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".zip",
    ".gz",
    ".lock",
    ".DS_Store",
)


# --------------------------------------------------------------------------- #
# Result model
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

    @property
    def ok(self) -> bool:
        return not self.failures

    def render(self) -> str:
        if self.skipped is not None:
            head = "SKIP  {0}: {1}".format(self.name, self.skipped)
            return head
        status = "PASS" if self.ok else "FAIL"
        lines = ["{0}  {1}".format(status, self.name)]
        for f in self.failures:
            lines.append("        - FAIL: {0}".format(f))
        for w in self.warnings:
            lines.append("        - warn: {0}".format(w))
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Manifest + path helpers
# --------------------------------------------------------------------------- #

def _load_manifest() -> Dict[str, Any]:
    path = common.repo_path(MANIFEST_REL)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _self_only(manifest: Dict[str, Any]) -> List[str]:
    entries = manifest.get("selfOnly") or []
    return [str(e) for e in entries]


def _is_self_only(rel: str, self_only: List[str]) -> bool:
    """True if ``rel`` (repo-relative, forward slashes) is covered by selfOnly.

    A selfOnly entry ending in ``/`` is a directory prefix; otherwise it is an
    exact file path.
    """
    norm = rel.replace(os.sep, "/")
    for entry in self_only:
        e = entry.replace(os.sep, "/")
        if e.endswith("/"):
            if norm == e[:-1] or norm.startswith(e):
                return True
        else:
            if norm == e:
                return True
    return False


def _git_tracked_files() -> List[str]:
    """Repo-relative, forward-slash paths of git-tracked files."""
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "ls-files"], cwd=common.REPO_ROOT, encoding="utf-8"
        )
    except Exception:  # pragma: no cover - git always present in this repo
        return []
    return [line.strip().replace(os.sep, "/") for line in out.splitlines() if line.strip()]


def _distributable_files(self_only: List[str]) -> List[str]:
    """Git-tracked files that are distributable text and worth scanning.

    Excludes selfOnly, docs/generated/, and examples/golden-example/ (the golden
    example is domain-neutral PROSE whose @requirement tags illustrate the
    mechanism; it is intentionally exempt from residue scans).
    """
    files = []
    for rel in _git_tracked_files():
        if _is_self_only(rel, self_only):
            continue
        if rel.startswith(GENERATED_DIR + "/") or rel == GENERATED_DIR:
            continue
        if rel.startswith(GOLDEN_EXAMPLE_DIR + "/"):
            continue
        if rel.endswith(SKIP_SUFFIXES):
            continue
        files.append(rel)
    return files


def _read(rel: str) -> str:
    return common.read_text(common.repo_path(rel))


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_seed_purity() -> CheckResult:
    res = CheckResult("seed-purity")
    # root prompts/state.json must have empty phases & prompts
    state_path = common.repo_path(STATE_REL)
    if not os.path.isfile(state_path):
        res.fail("{0} is missing".format(STATE_REL))
    else:
        try:
            with open(state_path, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            res.fail("{0} is not valid JSON: {1}".format(STATE_REL, exc))
            data = None
        if data is not None:
            phases = data.get("phases")
            prompts = data.get("prompts")
            if phases:
                res.fail(
                    "{0} -> phases must be empty (found {1})".format(
                        STATE_REL, len(phases)
                    )
                )
            if prompts:
                res.fail(
                    "{0} -> prompts must be empty (found {1})".format(
                        STATE_REL, len(prompts)
                    )
                )
    # docs/requirements/ must contain only .gitkeep
    req_dir = common.repo_path(REQUIREMENTS_DIR)
    if not os.path.isdir(req_dir):
        res.fail("{0}/ is missing".format(REQUIREMENTS_DIR))
    else:
        entries = sorted(os.listdir(req_dir))
        unexpected = [e for e in entries if e != ".gitkeep"]
        if unexpected:
            res.fail(
                "{0}/ must contain only .gitkeep (found: {1})".format(
                    REQUIREMENTS_DIR, ", ".join(unexpected)
                )
            )
    return res


def _frontmatter(text: str) -> Dict[str, str]:
    """Parse a leading YAML-ish frontmatter block (key: value lines)."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: Dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def _distributable_skill_and_command_names(self_only: List[str]) -> Tuple[List[str], List[str]]:
    """Return (skill_names, command_names) for DISTRIBUTABLE entries only."""
    skills: List[str] = []
    skills_root = common.repo_path(SKILLS_DIR)
    if os.path.isdir(skills_root):
        for name in sorted(os.listdir(skills_root)):
            folder = os.path.join(skills_root, name)
            if not os.path.isdir(folder):
                continue
            if not os.path.isfile(os.path.join(folder, "SKILL.md")):
                continue
            rel = "{0}/{1}".format(SKILLS_DIR, name)
            if _is_self_only(rel + "/", self_only) or _is_self_only(rel, self_only):
                continue
            skills.append(name)

    commands: List[str] = []
    commands_root = common.repo_path(COMMANDS_DIR)
    if os.path.isdir(commands_root):
        for fname in sorted(os.listdir(commands_root)):
            if not fname.endswith(".md"):
                continue
            rel = "{0}/{1}".format(COMMANDS_DIR, fname)
            if _is_self_only(rel, self_only):
                continue
            commands.append(fname[: -len(".md")])
    return skills, commands


def check_registration_parity(self_only: List[str]) -> CheckResult:
    res = CheckResult("registration-parity")
    skills, commands = _distributable_skill_and_command_names(self_only)
    names = sorted(set(skills) | set(commands))

    agents = _read(AGENTS_REL)
    catalog = _read(SKILLS_CATALOG_REL)
    if not agents:
        res.fail("{0} is missing or empty".format(AGENTS_REL))
    if not catalog:
        res.fail("{0} is missing or empty".format(SKILLS_CATALOG_REL))

    for name in names:
        # Match the bolded catalog-table form **name** (used in both files).
        token = "**{0}**".format(name)
        if token not in agents:
            res.fail("{0} not registered in {1} catalog".format(name, AGENTS_REL))
        if token not in catalog:
            res.fail("{0} not registered in {1}".format(name, SKILLS_CATALOG_REL))
    return res


def _scan_residue(
    files: List[str], tokens: List[str]
) -> List[Tuple[str, str]]:
    """Return [(file, token)] for each distributable file containing a token.

    Case-insensitive substring match. One hit per (file, token) pair.
    """
    hits: List[Tuple[str, str]] = []
    lowered = [(t, t.lower()) for t in tokens]
    for rel in files:
        text = _read(rel).lower()
        if not text:
            continue
        for orig, low in lowered:
            if low in text:
                hits.append((rel, orig))
    return hits


def check_domain_residue(self_only: List[str]) -> CheckResult:
    res = CheckResult("domain-residue")
    files = _distributable_files(self_only)
    for rel, token in _scan_residue(files, DOMAIN_TOKENS):
        res.fail("domain token '{0}' in distributable file {1}".format(token, rel))
    return res


def check_stack_residue(self_only: List[str]) -> CheckResult:
    res = CheckResult("stack-residue")
    files = _distributable_files(self_only)
    for rel, token in _scan_residue(files, STACK_TOKENS):
        res.warn(
            "stack token '{0}' in {1} (review — OK if a commented example)".format(
                token, rel
            )
        )
    return res


def check_manifest_coverage(self_only: List[str]) -> CheckResult:
    res = CheckResult("manifest-coverage")
    if not self_only:
        res.fail("manifest.selfOnly is empty or missing")
        return res
    for entry in self_only:
        norm = entry.rstrip("/")
        path = common.repo_path(norm)
        if not os.path.exists(path):
            res.fail("stale selfOnly entry — path does not exist: {0}".format(entry))
    return res


def check_skill_structure(self_only: List[str]) -> CheckResult:
    res = CheckResult("skill-structure")
    # Skills: frontmatter name + description.
    skills_root = common.repo_path(SKILLS_DIR)
    if os.path.isdir(skills_root):
        for name in sorted(os.listdir(skills_root)):
            folder = os.path.join(skills_root, name)
            skill_md = os.path.join(folder, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            fm = _frontmatter(common.read_text(skill_md))
            rel = "{0}/{1}/SKILL.md".format(SKILLS_DIR, name)
            if not fm.get("name"):
                res.fail("{0} missing frontmatter 'name'".format(rel))
            if not fm.get("description"):
                res.fail("{0} missing frontmatter 'description'".format(rel))
    # Commands: a description (frontmatter). Self-only ones are checked too —
    # /forge-contribute must be well-formed even though it is exempt from parity.
    commands_root = common.repo_path(COMMANDS_DIR)
    if os.path.isdir(commands_root):
        for fname in sorted(os.listdir(commands_root)):
            if not fname.endswith(".md"):
                continue
            cmd_md = os.path.join(commands_root, fname)
            fm = _frontmatter(common.read_text(cmd_md))
            rel = "{0}/{1}".format(COMMANDS_DIR, fname)
            if not fm.get("description"):
                res.fail("{0} missing frontmatter 'description'".format(rel))
    return res


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def run_all() -> List[CheckResult]:
    manifest = _load_manifest()
    self_only = _self_only(manifest)
    results: List[CheckResult] = []
    if not manifest:
        miss = CheckResult("manifest")
        miss.fail("forge.manifest.json is missing or empty")
        results.append(miss)
        return results
    results.append(check_seed_purity())
    results.append(check_registration_parity(self_only))
    results.append(check_domain_residue(self_only))
    results.append(check_stack_residue(self_only))
    results.append(check_manifest_coverage(self_only))
    results.append(check_skill_structure(self_only))
    return results


def _render_report(results: List[CheckResult]) -> Tuple[str, bool, int]:
    """Return (report_text, all_hard_passed, warning_count)."""
    lines: List[str] = []
    lines.append("forge-selfcheck — Forge constitution gate")
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
