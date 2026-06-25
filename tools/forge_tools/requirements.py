"""Parse the canonical requirement IDs from ``docs/requirements/``.

The traceability matrix is derived from these IDs (Forge Principle 7). The
parser is taxonomy-driven (FR/NFR/BR/CR/UC/EN, per the F2 taxonomy) and
domain-agnostic: it understands the two shapes Forge's requirement templates
use —

  * heading form  ``## FR01 — Title``           (functional, non-functional,
                                                  compliance, use cases,
                                                  entities)
  * table row     ``| **BR01** | Rule | ... |``  (business rules)

A requirement's **declared id** is its top-level id (``FR01``, ``BR01``). Dotted
sub-items (``FR01.1``, ``NFR01.2``) listed under a heading are *part of* their
parent, not separate matrix rows — matching the templates and the golden example,
which tag implementing code with the parent id (``@requirement FR01``). A tag that
points at a sub-id is **rolled up to the parent** by the traceability tool, so it
still resolves to a declared requirement (it is not reported as "undeclared").

Each requirement document maps to a prefix; the parser reads whichever
documents exist (a fresh checkout may have none) and returns the declared IDs
with their titles and the source document.
"""

import os
import re
from typing import Dict, Iterable, List, NamedTuple, Optional, Set

from . import common

REQ_DIR_REL = "docs/requirements"


class Requirement(NamedTuple):
    id: str
    title: str
    source_doc: str  # repo-relative path of the document that declares it
    kind: str  # "requirement" | "rule"


# Document file name -> (prefix, link-kind). Stack-neutral; these are the F2
# template file names (with the .template suffix dropped by genesis).
DOC_PREFIXES = [
    ("functional.md", "FR", "requirement"),
    ("non-functional.md", "NFR", "requirement"),
    ("compliance.md", "CR", "requirement"),
    ("use-cases.md", "UC", "requirement"),
    ("data-model.md", "EN", "requirement"),
    ("business-rules.md", "BR", "rule"),
]


def _heading_pattern(prefix: str) -> "re.Pattern[str]":
    # "## FR01 — Title"  (em dash or hyphen separator)
    return re.compile(
        r"^#{1,6}\s+(" + re.escape(prefix) + r"\d+)\s*[—-]\s*(.+?)\s*$"
    )


def _table_row_pattern(prefix: str) -> "re.Pattern[str]":
    # "| **BR01** | Rule statement | ... |"  -> id + first cell after id
    return re.compile(
        r"^\|\s*\**\s*(" + re.escape(prefix) + r"\d+)\s*\**\s*\|\s*(.+?)\s*\|"
    )


def _parse_doc(path: str, prefix: str, kind: str, source_doc: str) -> List[Requirement]:
    out: List[Requirement] = []
    seen = set()
    heading = _heading_pattern(prefix)
    row = _table_row_pattern(prefix)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = heading.match(line)
            if not m:
                m = row.match(line)
            if not m:
                continue
            rid = m.group(1)
            if rid in seen:
                continue
            seen.add(rid)
            title = m.group(2).strip()
            # Strip trailing markdown emphasis/markers from table titles.
            title = title.strip("* ")
            out.append(Requirement(rid, title, source_doc, kind))
    return out


def _natural_key(rid: str):
    m = re.match(r"^([A-Za-z]+)[-]?(\d+)", rid)
    if m:
        return (m.group(1), int(m.group(2)))
    return (rid, 0)


def _normalize_doc_basenames(docs: Iterable[str]) -> Set[str]:
    """Accept ``"functional.md"`` or ``"functional"`` and return a basename set.

    Lets a scope's ``reqDocs`` list the requirement documents it owns by either
    the bare stem or the full ``.md`` basename; both forms are matched.
    """
    out: Set[str] = set()
    for raw in docs:
        base = os.path.basename(str(raw).strip())
        if not base:
            continue
        out.add(base)
        if base.endswith(".md"):
            out.add(base[: -len(".md")])
        else:
            out.add(base + ".md")
    return out


def parse_requirements(
    req_dir: Optional[str] = None,
    source_docs: Optional[Iterable[str]] = None,
) -> List[Requirement]:
    """Return all declared requirement IDs across the requirement documents.

    A missing requirements folder (fresh checkout) yields an empty list — not
    an error, since the generators must run with no project content present.

    ``source_docs`` is an OPTIONAL allow-list of requirement-document basenames
    (e.g. ``"functional.md"`` or ``"functional"``): when given, only requirements
    declared in those documents are returned. It is used only by scoped
    traceability; the default (``None``) returns every declared requirement —
    unchanged behavior.
    """
    base = req_dir or common.repo_path(REQ_DIR_REL)
    result: List[Requirement] = []
    if not os.path.isdir(base):
        return result
    allow = _normalize_doc_basenames(source_docs) if source_docs is not None else None
    by_id: Dict[str, Requirement] = {}
    for filename, prefix, kind in DOC_PREFIXES:
        if allow is not None and filename not in allow:
            continue
        path = os.path.join(base, filename)
        if not os.path.isfile(path):
            continue
        source_doc = common.rel_to_repo(path)
        for req in _parse_doc(path, prefix, kind, source_doc):
            # First declaration wins (a doc owns its prefix).
            by_id.setdefault(req.id, req)
    result = list(by_id.values())
    result.sort(key=lambda r: _natural_key(r.id))
    return result
