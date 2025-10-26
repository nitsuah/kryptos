#!/usr/bin/env python3
"""Remove log.info and log.debug lines from all Python files."""

from pathlib import Path

files = list(Path('src/kryptos').rglob('*.py'))
total_removed = 0

for f in files:
    if '__init__' in str(f) or 'examples' in str(f):
        continue

    with open(f, encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    removed = 0
    for line in lines:
        stripped = line.strip()
        if (
            stripped.startswith('log.info(')
            or stripped.startswith('log.debug(')
            or stripped.startswith('self.log.info(')
            or stripped.startswith('self.log.debug(')
        ):
            removed += 1
            continue
        new_lines.append(line)

    if removed > 0:
        with open(f, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        rel_path = str(f.relative_to('src/kryptos'))
        print(f'{rel_path}: removed {removed} log lines')
        total_removed += removed

print(f'\nTotal: {total_removed} log.info/debug lines removed')
