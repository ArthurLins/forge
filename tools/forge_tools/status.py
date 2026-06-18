#!/usr/bin/env python3
"""Status generator — regenerate ``prompts/STATUS.md`` from ``prompts/state.json``.

STATUS.md is 100% derived from state.json and is never edited by hand
(Forge Principle 6, "derived docs are code"). This generator mirrors the
prompt-suite engine: it reads the same state machine ``next_prompt.py`` reads
and renders the per-phase tables, a progress count, and the next-eligible
prompt.

Usage:
  python3 -m forge_tools.status            # write prompts/STATUS.md
  python3 -m forge_tools.status --check     # exit 1 + diff if STATUS.md is stale

Stack-neutral: no project-specific logic; the only input is state.json.
"""

import json
import os
import sys
from typing import Any, Dict, List

from . import common

STATE_REL = "prompts/state.json"
STATUS_REL = "prompts/STATUS.md"

STATUS_ICON = {
    "pending": "[ ]",
    "in_progress": "[~]",
    "blocked": "[x]",
    "done": "[v]",
}
STATUS_ORDER = ["pending", "in_progress", "blocked", "done"]

HEADER = (
    "<!-- GENERATED from prompts/state.json by tools/forge_tools/status.py.\n"
    "     Do not edit by hand: run `make forge-status` or `make forge-sync-docs`. -->"
)


def _load_state() -> Dict[str, Any]:
    path = common.repo_path(STATE_REL)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _deps_label(deps: List[str]) -> str:
    return ", ".join(deps) if deps else "—"


def _refs_label(refs: List[str]) -> str:
    return ", ".join(refs) if refs else "—"


def _commit_label(prompt: Dict[str, Any]) -> str:
    commit = (prompt.get("commit") or "").strip()
    return "`{}`".format(commit[:9]) if commit else "—"


def _next_eligible(prompts: List[Dict[str, Any]]) -> str:
    """Same eligibility rule as next_prompt.py: first runnable in file order."""
    done = {p.get("id") for p in prompts if p.get("status") == "done"}
    runnable = {"pending", "in_progress"}
    pending = [p for p in prompts if p.get("status") in runnable]
    if not pending:
        return "DONE — every prompt is complete."
    for p in pending:
        deps = p.get("dependsOn") or []
        if all(d in done for d in deps):
            return "`{}` — {}".format(p.get("id", "?"), p.get("title", ""))
    ids = ", ".join(p.get("id", "?") for p in pending)
    return "BLOCKED — pending prompts have unsatisfied dependencies: {}".format(ids)


def build_status() -> str:
    data = _load_state()
    prompts: List[Dict[str, Any]] = data.get("prompts") or []
    phases: List[Dict[str, Any]] = data.get("phases") or []

    total = len(prompts)
    counts = {s: 0 for s in STATUS_ORDER}
    for p in prompts:
        st = p.get("status", "pending")
        counts[st] = counts.get(st, 0) + 1
    done = counts.get("done", 0)
    pct = round((done / total) * 100) if total else 0

    updated = (data.get("updatedAt") or "").strip() or "—"
    name = (data.get("project") or "").strip() or common.project_name()

    lines: List[str] = []
    lines.append(HEADER)
    lines.append("")
    lines.append("# {} — Status".format(name))
    lines.append("")
    lines.append(
        "> Human-readable view of [`state.json`](state.json). "
        "**Generated — do not edit by hand.** The plan index is "
        "[`ROADMAP.md`](ROADMAP.md)."
    )
    lines.append("")
    lines.append(
        "**Updated:** {} · **Legend:** `[ ]` pending · `[~]` in_progress · "
        "`[x]` blocked · `[v]` done".format(updated)
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("| ------ | ----- |")
    lines.append("| Total prompts | {} |".format(total))
    lines.append("| Done | {} |".format(counts.get("done", 0)))
    lines.append("| In progress | {} |".format(counts.get("in_progress", 0)))
    lines.append("| Blocked | {} |".format(counts.get("blocked", 0)))
    lines.append("| Pending | {} |".format(counts.get("pending", 0)))
    lines.append("")
    lines.append("**Overall progress:** {}/{} done ({}%)".format(done, total, pct))
    lines.append("")
    lines.append("**Next eligible:** {}".format(_next_eligible(prompts)))
    lines.append("")
    lines.append("---")
    lines.append("")

    if not prompts:
        lines.append(
            "_No prompts have been planned yet. Run `/forge-init` to seed the "
            "first phase._"
        )
        lines.append("")
        return _join(lines)

    # Per-phase tables, in the order phases are declared. Any prompt whose phase
    # is not declared is grouped under an "Unassigned" bucket so nothing is lost.
    declared_phase_ids = [ph.get("id") for ph in phases]
    seen_phase_ids = set()

    for phase in phases:
        pid = phase.get("id")
        seen_phase_ids.add(pid)
        phase_prompts = [p for p in prompts if p.get("phase") == pid]
        if not phase_prompts:
            continue
        _render_phase(lines, phase.get("name", str(pid)), pid, phase_prompts)

    orphan = [
        p
        for p in prompts
        if p.get("phase") not in declared_phase_ids
    ]
    if orphan:
        _render_phase(lines, "Unassigned", "—", orphan)

    return _join(lines)


def _render_phase(
    lines: List[str], name: str, pid: Any, phase_prompts: List[Dict[str, Any]]
) -> None:
    phase_done = sum(1 for p in phase_prompts if p.get("status") == "done")
    has_refs = any(p.get("refs") for p in phase_prompts)
    lines.append(
        "## Phase {} — {} ({}/{})".format(pid, name, phase_done, len(phase_prompts))
    )
    lines.append("")
    if has_refs:
        lines.append("| Status | ID | Title | Depends on | Refs | Commit |")
        lines.append("| ------ | -- | ----- | ---------- | ---- | ------ |")
    else:
        lines.append("| Status | ID | Title | Depends on | Commit |")
        lines.append("| ------ | -- | ----- | ---------- | ------ |")
    for p in phase_prompts:
        icon = STATUS_ICON.get(p.get("status", "pending"), "[ ]")
        if has_refs:
            lines.append(
                "| {} | {} | {} | {} | {} | {} |".format(
                    icon,
                    p.get("id", "?"),
                    p.get("title", ""),
                    _deps_label(p.get("dependsOn") or []),
                    _refs_label(p.get("refs") or []),
                    _commit_label(p),
                )
            )
        else:
            lines.append(
                "| {} | {} | {} | {} | {} |".format(
                    icon,
                    p.get("id", "?"),
                    p.get("title", ""),
                    _deps_label(p.get("dependsOn") or []),
                    _commit_label(p),
                )
            )
    lines.append("")


def _join(lines: List[str]) -> str:
    text = "\n".join(lines)
    return text.rstrip("\n") + "\n"


def main(argv: List[str]) -> int:
    check = "--check" in argv
    content = build_status()
    return common.emit(content, common.repo_path(STATUS_REL), check, "status")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
