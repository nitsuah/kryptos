#!/usr/bin/env python3
"""Safe cleanup: Remove docstrings and excessive logging WITHOUT breaking code."""

from pathlib import Path


def clean_file(file_path: Path) -> tuple[int, int]:
    """Clean a single file. Returns (lines_before, lines_after)."""

    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()

    original_count = len(lines)

    # Skip files that should be preserved
    if any(x in str(file_path) for x in ['__init__.py', 'deprecation.py', 'examples/']):
        return (original_count, original_count)

    cleaned_lines = []
    i = 0
    in_multiline_docstring = False
    docstring_delimiter = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect triple-quote docstrings
        if '"""' in line or "'''" in line:
            # Which delimiter?
            if '"""' in line:
                delim = '"""'
            else:
                delim = "'''"

            # Count occurrences in this line
            count = line.count(delim)

            if not in_multiline_docstring:
                # Starting a docstring
                if count == 2:
                    # One-line docstring - check if it's after def/class
                    if i > 0:
                        prev_stripped = lines[i - 1].strip()
                        if (
                            prev_stripped.startswith('def ')
                            or prev_stripped.startswith('class ')
                            or prev_stripped.startswith('async def ')
                        ):
                            # Skip this docstring line
                            i += 1
                            continue
                elif count == 1:
                    # Starting multiline docstring
                    if i > 0:
                        prev_stripped = lines[i - 1].strip()
                        if (
                            prev_stripped.startswith('def ')
                            or prev_stripped.startswith('class ')
                            or prev_stripped.startswith('async def ')
                        ):
                            in_multiline_docstring = True
                            docstring_delimiter = delim
                            i += 1
                            continue
            else:
                # Ending multiline docstring
                if delim == docstring_delimiter:
                    in_multiline_docstring = False
                    docstring_delimiter = None
                    i += 1
                    continue

        # Skip lines inside multiline docstrings
        if in_multiline_docstring:
            i += 1
            continue

        # Remove log.info/debug lines (but keep error/warning/exception)
        if stripped.startswith(('log.info(', 'log.debug(', 'self.log.info(', 'self.log.debug(')):
            i += 1
            continue

        # Remove standalone comment lines (keep type hints, noqa, etc)
        if stripped.startswith('#'):
            if any(
                x in stripped for x in ['type:', 'noqa', 'pylint:', 'mypy:', 'fmt:', 'coding:', 'Copyright', 'License']
            ):
                cleaned_lines.append(line)
            i += 1
            continue

        # Remove inline comments (keep special ones)
        if '#' in line and not any(x in line for x in ['type:', 'noqa', 'pylint:', 'mypy:', 'fmt:']):
            # Only remove if it's actually a comment (not in string)
            # Simple heuristic: if # is after code and not in quotes
            code_part = line.split('#')[0].rstrip()
            if code_part and code_part.count('"') % 2 == 0 and code_part.count("'") % 2 == 0:
                cleaned_lines.append(code_part + '\n')
                i += 1
                continue

        # Keep everything else
        cleaned_lines.append(line)
        i += 1

    # Remove excessive blank lines (max 2 consecutive)
    final_lines = []
    blank_count = 0
    for line in cleaned_lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 2:
                final_lines.append(line)
        else:
            blank_count = 0
            final_lines.append(line)

    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)

    return (original_count, len(final_lines))


def main():
    """Clean all Python files in src/kryptos."""
    src_path = Path('src/kryptos')
    python_files = list(src_path.rglob('*.py'))

    print(f"Cleaning {len(python_files)} Python files...")
    print("=" * 80)

    total_before = 0
    total_after = 0
    files_changed = 0

    for file_path in sorted(python_files):
        before, after = clean_file(file_path)
        total_before += before
        total_after += after

        reduction = before - after
        if reduction > 0:
            files_changed += 1
            pct = (reduction / before * 100) if before > 0 else 0
            rel_path = str(file_path.relative_to('src/kryptos'))
            print(f"✓ {rel_path}: {before} → {after} (-{reduction}, -{pct:.1f}%)")

    print("=" * 80)
    total_reduction = total_before - total_after
    total_pct = (total_reduction / total_before * 100) if total_before > 0 else 0
    print(f"TOTAL: {files_changed} files changed")
    print(f"Lines: {total_before} → {total_after} (-{total_reduction}, -{total_pct:.1f}%)")


if __name__ == '__main__':
    main()
