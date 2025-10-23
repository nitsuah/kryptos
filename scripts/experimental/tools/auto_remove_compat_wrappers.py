#!/usr/bin/env python3
"""Auto-detect and remove thin compatibility wrapper scripts under scripts/.

This targets files directly under `scripts/` (not subdirs) that match one or
more patterns:
 - contains 'Compatibility wrapper' or 'forwards to' or 'forward to'
 - contains "subprocess.call([sys.executable, 'scripts/" or similar

It prints matches, deletes them, and exits with 0.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
PATTERNS = [
    re.compile(r"Compatibility wrapper", re.I),
    re.compile(r"forwards to `?scripts/", re.I),
    re.compile(r"forward to `?scripts/", re.I),
    re.compile(r"subprocess\.call\(\[sys\.executable,\s*['\"]scripts/", re.I),
    re.compile(r"sys\.exit\(subprocess\.call\(\[sys\.executable,\s*['\"]scripts/", re.I),
]

removed = []
for p in SCRIPTS.iterdir():
    if not p.is_file():
        continue
    if p.parent != SCRIPTS:
        continue
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    if any(pat.search(text) for pat in PATTERNS):
        print(f"Deleting wrapper: {p.relative_to(ROOT)}")
        try:
            p.unlink()
            removed.append(p.relative_to(ROOT))
        except Exception as e:
            print(f"Failed to delete {p}: {e}")

if not removed:
    print("No compatibility wrappers found.")
else:
    print("Removed files:")
    for r in removed:
        print(' -', r)
