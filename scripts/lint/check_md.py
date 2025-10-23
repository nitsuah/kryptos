"""Small markdown checker for common style issues.

Rules:
- No leading-space list markers (lines starting with ' - ' or ' * ')
- No trailing whitespace
- Max line length 120

Run from repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATHS = [ROOT / 'docs', ROOT / 'README.md']
IGNORED_DIRS = [ROOT / 'docs' / 'sources']

errs = 0


def check_file(path: Path) -> int:
    global errs
    in_code = False
    with path.open(encoding='utf-8') as fh:
        for i, ln in enumerate(fh, start=1):
            line = ln.rstrip('\n')
            ls = line.lstrip()
            # toggle code-fence state
            if ls.startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                continue
            # skip obvious non-paragraph lines: URLs, tables
            if 'http://' in line or 'https://' in line:
                continue
            if '|' in line and not line.strip().startswith('|-'):
                continue
            if line.endswith(' '):
                print(f"{path}:{i}: trailing whitespace")
                errs += 1
            if len(line) > 120:
                print(f"{path}:{i}: line too long ({len(line)})")
                errs += 1
            if line.startswith(' - ') or line.startswith(' * '):
                print(f"{path}:{i}: leading-space list marker")
                errs += 1
    return 0


def iter_md_files():
    for p in MD_PATHS:
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob('*.md'):
                # skip large source docs that intentionally contain long lines
                if any(str(f).startswith(str(d)) for d in IGNORED_DIRS):
                    continue
                yield f


def main():
    for f in iter_md_files():
        check_file(f)
    if errs:
        print(f"Found {errs} markdown issues")
        sys.exit(2)
    print("No markdown issues detected")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
