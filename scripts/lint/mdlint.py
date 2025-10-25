"""Markdown linting and formatting tool.

Usage:
    python scripts/lint/mdlint.py check [files...]  # Check style (used by pre-commit)
    python scripts/lint/mdlint.py reflow [files...] # Reflow paragraphs to 120 chars
    python scripts/lint/mdlint.py fix [files...]    # Auto-fix MD032, MD036, etc.

Rules:
- No trailing whitespace
- Max line length 120 chars (outside code/tables/URLs)
- No leading-space list markers (" - ")
- Reflow paragraphs to 120 chars while preserving code/tables/headers
- MD032: Lists should be surrounded by blank lines
- MD036: Emphasis used instead of a heading (bold text on its own line)
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATHS = [ROOT / 'docs', ROOT / 'README.md']
IGNORED_DIRS = [ROOT / 'docs' / 'sources']
CONFIG_FILE = ROOT / '.markdownlint.json'

MAX_WIDTH = 120
if CONFIG_FILE.exists():
    try:
        import json

        cfg = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        md013 = cfg.get('MD013') or {}
        MAX_WIDTH = int(md013.get('line_length', MAX_WIDTH))
    except Exception:
        MAX_WIDTH = 120


# ============================================================================
# CHECK: Style validation
# ============================================================================


def check_file(path: Path) -> int:
    """Check a single markdown file for style issues."""
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
            # skip URLs and tables
            if 'http://' in line or 'https://' in line:
                continue
            if '|' in line and not line.strip().startswith('|-'):
                continue
            # check issues
            if line.endswith(' '):
                print(f"{path}:{i}: trailing whitespace")
                errs_local += 1
            if len(line) > MAX_WIDTH:
                print(f"{path}:{i}: line too long ({len(line)})")
                errs_local += 1
            if line.startswith(' - ') or line.startswith(' * '):
                print(f"{path}:{i}: leading-space list marker")
                errs_local += 1
    return errs_local


def iter_md_files():
    """Iterate over all markdown files in the repository."""
    for p in MD_PATHS:
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob('*.md'):
                if any(str(f).startswith(str(d)) for d in IGNORED_DIRS):
                    continue
                yield f


def cmd_check(argv: list[str]) -> int:
    """Run style checks on markdown files."""
    if len(argv) > 2:
        # Check specific files
        files = [Path(p) for p in argv[2:]]
    else:
        # Check all files
        files = list(iter_md_files())

    total = 0
    for f in files:
        if f.exists():
            total += check_file(f)
    if total:
        print(f"Found {total} markdown issues")
        return 2
    print("No markdown issues detected")
    return 0


# ============================================================================
# REFLOW: Paragraph reformatting
# ============================================================================


def should_skip_line(line: str) -> bool:
    """Check if a line should not be reflowed."""
    s = line.lstrip()
    return (
        s.startswith('```')  # code fence
        or line.startswith('    ')  # indented code
        or line.startswith('\t')  # indented code
        or ('|' in line and not line.strip().startswith('|-'))  # table
        or 'http://' in line  # URL
        or 'https://' in line  # URL
        or s.startswith('#')  # header
    )


def reflow_file(path: Path) -> None:
    """Reflow paragraphs in a markdown file to MAX_WIDTH."""
    txt = path.read_text(encoding='utf-8')
    lines = txt.splitlines()
    out_lines: list[str] = []
    in_code = False
    para_acc: list[str] = []

    def flush_para():
        nonlocal para_acc
        if not para_acc:
            return
        para = ' '.join([p.strip() for p in para_acc])
        wrapped = textwrap.fill(para, width=MAX_WIDTH)
        out_lines.extend(wrapped.splitlines())
        para_acc = []

    for line in lines:
        stripped = line.lstrip()
        # toggle code fence
        if stripped.startswith('```'):
            flush_para()
            out_lines.append(line)
            in_code = not in_code
            continue
        if in_code:
            out_lines.append(line)
            continue
        # skip special lines
        if should_skip_line(line):
            flush_para()
            out_lines.append(line)
            continue
        # blank line ends paragraph
        if line.strip() == '':
            flush_para()
            out_lines.append('')
            continue
        # list item: preserve bullet and reflow remainder
        if stripped.startswith(('- ', '* ', '+ ')):
            flush_para()
            marker = line[: line.find(stripped)] + stripped[:2]
            rest = stripped[2:]
            if rest.strip() == '':
                out_lines.append(line)
            else:
                wrapped = textwrap.fill(rest.strip(), width=MAX_WIDTH - len(marker))
                wrapped_lines = wrapped.splitlines()
                out_lines.append(marker + wrapped_lines[0])
                indent = ' ' * len(marker)
                for wl in wrapped_lines[1:]:
                    out_lines.append(indent + wl)
            continue
        # normal paragraph line: accumulate
        para_acc.append(line)

    flush_para()
    new_txt = '\n'.join(out_lines) + '\n'
    path.write_text(new_txt, encoding='utf-8')


def cmd_reflow(argv: list[str]) -> int:
    """Reflow markdown files to MAX_WIDTH."""
    if len(argv) < 3:
        print('Usage: mdlint.py reflow <file-or-dir> [file-or-dir ...]')
        return 2
    for p in argv[2:]:
        fp = Path(p)
        if not fp.exists():
            print(f'Skipping missing: {p}')
            continue
        if fp.is_dir():
            for f in fp.rglob('*.md'):
                print(f'Reflowing: {f}')
                reflow_file(f)
        else:
            print(f'Reflowing: {fp}')
            reflow_file(fp)
    return 0


# ============================================================================
# FIX: Auto-fix common issues (MD032, MD036)
# ============================================================================


def is_list_line(line: str) -> bool:
    """Check if line is a list item."""
    s = line.lstrip()
    if s.startswith(('- ', '* ', '+ ')):
        return True
    if s and s[0].isdigit() and '. ' in s[:4]:
        return True
    return False


def is_emphasis_heading(line: str) -> bool:
    """Check if line is bold/italic text that should be a heading (MD036)."""
    s = line.strip()
    # Check for **text** or __text__ on its own line
    if (s.startswith('**') and s.endswith('**') and len(s) > 4) or (
        s.startswith('__') and s.endswith('__') and len(s) > 4
    ):
        # Not if it's in a list or after a colon
        return True
    return False


def fix_file(path: Path) -> int:
    """Auto-fix MD032 (blanks around lists) and MD036 (emphasis headings)."""
    txt = path.read_text(encoding='utf-8')
    lines = txt.splitlines()
    out_lines: list[str] = []
    in_code = False
    fixes = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()

        # Toggle code fence
        if stripped.startswith('```'):
            in_code = not in_code
            out_lines.append(line)
            continue

        if in_code:
            out_lines.append(line)
            continue

        # Fix MD036: Convert **Heading** to ### Heading
        if is_emphasis_heading(line):
            inner = line.strip()[2:-2].strip()
            # Use ### for emphasis headings (h3)
            out_lines.append(f"### {inner}")
            fixes += 1
            continue

        # Fix MD032: Ensure blank line before list
        if is_list_line(line):
            prev_idx = len(out_lines) - 1
            # Check if previous line is not blank and not a list item
            if prev_idx >= 0:
                prev = out_lines[prev_idx]
                if prev.strip() != '' and not is_list_line(prev):
                    out_lines.append('')  # Add blank line before list
                    fixes += 1

        out_lines.append(line)

        # Fix MD032: Ensure blank line after list
        if is_list_line(line) and i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.lstrip()
            # If next line is not blank, not a list, and not a code fence
            if (
                next_stripped != ''
                and not is_list_line(next_line)
                and not next_stripped.startswith('```')
                and not next_stripped.startswith('#')
            ):
                # Look ahead to see if we're at end of list
                if i + 1 < len(lines):
                    out_lines.append('')  # Add blank line after list item
                    fixes += 1

    new_txt = '\n'.join(out_lines) + '\n'
    if fixes > 0:
        path.write_text(new_txt, encoding='utf-8')
        print(f"Fixed {fixes} issues in {path}")
    return fixes


def cmd_fix(argv: list[str]) -> int:
    """Auto-fix common markdown issues."""
    if len(argv) < 3:
        # Fix all files
        files = list(iter_md_files())
    else:
        # Fix specific files
        files = [Path(p) for p in argv[2:]]

    total_fixes = 0
    for f in files:
        if f.exists():
            total_fixes += fix_file(f)

    if total_fixes:
        print(f"Fixed {total_fixes} total issues")
    else:
        print("No issues to fix")
    return 0


# ============================================================================
# CLI
# ============================================================================


def main(argv: list[str]) -> int:
    """Main entry point."""
    if len(argv) < 2 or argv[1] not in ('check', 'reflow', 'fix'):
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == 'check':
        return cmd_check(argv)
    if cmd == 'reflow':
        return cmd_reflow(argv)
    if cmd == 'fix':
        return cmd_fix(argv)
    return 2


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
