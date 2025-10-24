"""Small markdown checker for common style issues.

Rules enforced (lightweight superseding markdownlint baseline):
- No trailing whitespace.
- Max line length (default 120) outside code fences / tables / URLs.
- Disallow list markers with a leading space before bullet (" - ", " * ").

Explicitly ALLOW fenced code blocks (MD046 style=fenced in .markdownlint.json).
We DO NOT enforce indented code style.

Run from repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATHS = [ROOT / 'docs', ROOT / 'README.md']
IGNORED_DIRS = [ROOT / 'docs' / 'sources']
CONFIG_FILE = ROOT / '.markdownlint.json'

MAX_LINE = 120
if CONFIG_FILE.exists():
    try:
        import json

        cfg = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        md013 = cfg.get('MD013') or {}
        MAX_LINE = int(md013.get('line_length', MAX_LINE))
    except Exception:  # pragma: no cover - config parse failures fall back silently
        MAX_LINE = 120


def check_file(path: Path) -> int:
    errs_local = 0
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
            if 'http://' in line or 'https://' in line:
                continue
            if '|' in line and not line.strip().startswith('|-'):
                continue
            if line.endswith(' '):
                print(f"{path}:{i}: trailing whitespace")
                errs_local += 1
            if len(line) > MAX_LINE:
                print(f"{path}:{i}: line too long ({len(line)})")
                errs_local += 1
            if line.startswith(' - ') or line.startswith(' * '):
                print(f"{path}:{i}: leading-space list marker")
                errs_local += 1
    return errs_local


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
    total = 0
    for f in iter_md_files():
        total += check_file(f)
    if total:
        print(f"Found {total} markdown issues")
        sys.exit(2)
    print("No markdown issues detected")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
