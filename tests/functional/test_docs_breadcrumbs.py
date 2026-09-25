from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / "docs"
EXCLUDE = {"CHANGELOG.md", "PLAN.md", "archive"}
# Linked breadcrumb nav line (2026-09-24 pmo-ff pass), e.g.
# > 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · ... <!-- nav -->
NAV = re.compile(r"^> .*\[kryptos\]\((?:\.\./)+README\.md\).*<!-- nav -->$", re.M)


def test_all_docs_have_breadcrumb():
    missing: list[str] = []
    for md in DOCS.rglob("*.md"):
        rel = md.relative_to(DOCS)
        # skip archived and excluded
        if rel.parts[0] == "archive" or rel.name in EXCLUDE:
            continue
        text = md.read_text(encoding="utf-8")
        if not NAV.search(text):
            missing.append(str(rel))
    assert not missing, f"Missing breadcrumb in: {missing}"
