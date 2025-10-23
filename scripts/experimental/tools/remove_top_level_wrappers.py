#!/usr/bin/env python3
"""Remove top-level wrapper stubs in scripts/ that point to canonical locations.

This script targets files directly under `scripts/` (not subdirectories) and
removes any file that contains a marker like "removed: use scripts/" or
"moved: scripts/". It prints what it deletes for review.

Run from the repository root or as:
    python scripts/tools/remove_top_level_wrappers.py
"""

from pathlib import Path

_here = Path(__file__).resolve()
REPO_ROOT = _here
for p in _here.parents:
    if (p / 'pyproject.toml').exists():
        REPO_ROOT = p
        break
print(f'[remove_top_level_wrappers] repo root resolved to {REPO_ROOT}')
SCRIPTS_DIR = REPO_ROOT.joinpath("scripts")

markers = ("removed: use scripts/", "moved: scripts/")

removed = []

for p in SCRIPTS_DIR.iterdir():
    if not p.is_file():
        continue
    # Only consider direct children of scripts/ (skip nested folders)
    if p.parent != SCRIPTS_DIR:
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # unreadable file, skip
        continue
    if any(m in text for m in markers):
        try:
            p.unlink()
            removed.append(str(p.relative_to(REPO_ROOT)))
        except OSError as err:
            print(f"Failed to remove {p}: {err}")

if removed:
    print("Removed files:")
    for r in removed:
        print(" -", r)
else:
    print("No top-level wrapper stubs found to remove.")
