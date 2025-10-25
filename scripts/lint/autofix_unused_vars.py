"""Auto-fix unused variables by prefixing with underscore.

This preserves potentially useful code/future foundation by marking
variables as intentionally unused rather than deleting them.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def find_unused_vars(path: Path) -> list[tuple[int, str, str]]:
    """Find unused variables using flake8.

    Returns:
        List of (line_number, var_name, full_line) tuples
    """
    result = subprocess.run(
        ['flake8', '--select=F841', str(path)],
        capture_output=True,
        text=True,
    )

    unused = []
    for line in result.stdout.splitlines():
        # Format: path:line:col: F841 local variable 'name' is assigned to but never used
        match = re.search(r':(\d+):\d+: F841 local variable \'(\w+)\' is assigned', line)
        if match:
            line_num = int(match.group(1))
            var_name = match.group(2)
            unused.append((line_num, var_name, line))

    return unused


def fix_unused_vars(path: Path, dry_run: bool = False) -> int:
    """Fix unused variables by prefixing with underscore.

    Args:
        path: Python file to fix
        dry_run: If True, only print changes without applying them

    Returns:
        Number of fixes applied
    """
    unused = find_unused_vars(path)
    if not unused:
        return 0

    # Read file
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)

    fixes = 0
    for line_num, var_name, _ in unused:
        # Skip if already prefixed
        if var_name.startswith('_'):
            continue

        # Get the line (1-indexed)
        line_idx = line_num - 1
        original = lines[line_idx]

        # Replace variable name with underscore prefix
        # Match whole word boundaries to avoid partial replacements
        pattern = r'\b' + re.escape(var_name) + r'\b'
        new_line = re.sub(pattern, f'_{var_name}', original, count=1)

        if new_line != original:
            if dry_run:
                print(f"Line {line_num}: {var_name} -> _{var_name}")
                print(f"  - {original.rstrip()}")
                print(f"  + {new_line.rstrip()}")
            else:
                lines[line_idx] = new_line
            fixes += 1

    # Write back if not dry run
    if not dry_run and fixes > 0:
        path.write_text(''.join(lines), encoding='utf-8')
        print(f"Fixed {fixes} unused variable(s) in {path}")

    return fixes


def fix_all_unused_vars(root: Path, dry_run: bool = False) -> int:
    """Fix unused variables in all Python files.

    Args:
        root: Root directory to search
        dry_run: If True, only print changes

    Returns:
        Total number of fixes applied
    """
    total = 0
    for py_file in root.rglob('*.py'):
        # Skip __pycache__ and venv
        if '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue

        fixes = fix_unused_vars(py_file, dry_run=dry_run)
        total += fixes

    return total


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python autofix_unused_vars.py <file-or-dir> [--dry-run]")
        print()
        print("Auto-fix unused variables (F841) by prefixing with underscore.")
        print("This preserves potentially useful code for future use.")
        return 1

    dry_run = '--dry-run' in sys.argv
    target = Path(sys.argv[1])

    if not target.exists():
        print(f"Error: {target} does not exist")
        return 1

    if target.is_file():
        fixes = fix_unused_vars(target, dry_run=dry_run)
    else:
        fixes = fix_all_unused_vars(target, dry_run=dry_run)

    if dry_run:
        print(f"\nDry run: {fixes} fix(es) would be applied")
    else:
        print(f"\nTotal: {fixes} fix(es) applied")

    return 0


if __name__ == '__main__':
    sys.exit(main())
