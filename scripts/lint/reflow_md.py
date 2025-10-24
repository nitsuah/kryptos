"""Simple markdown reflow tool.

Usage: python scripts/lint/reflow_md.py <file1.md> [file2.md ...]

Rules:
- Preserve code fences (``` blocks) and indented code blocks.
- Preserve tables (lines containing '|') and lines containing URLs.
- Reflow paragraphs and list-item text to a max width (default 100 chars).
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

MAX_WIDTH = 120  # align with markdownlint configured line length


def should_skip_line(line: str) -> bool:
    s = line.lstrip()
    # code fence
    if s.startswith('```'):
        return True
    # indented code
    if line.startswith('    ') or line.startswith('\t'):
        return True
    # tables
    if '|' in line and not line.strip().startswith('|-'):
        return True
    # lines with URLs
    if 'http://' in line or 'https://' in line:
        return True
    # headers
    if s.startswith('#'):
        return True
    return False


def reflow_file(path: Path) -> None:
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
        if stripped.startswith('```'):
            # toggle code fence
            flush_para()
            out_lines.append(line)
            in_code = not in_code
            continue
        if in_code:
            out_lines.append(line)
            continue
        if should_skip_line(line):
            flush_para()
            out_lines.append(line)
            continue
        # blank line ends paragraph
        if line.strip() == '':
            flush_para()
            out_lines.append('')
            continue
        # list item: preserve bullet and reflow the remainder
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


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Usage: reflow_md.py <file-or-dir> [file-or-dir ...]')
        return 2
    for p in argv[1:]:
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


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
