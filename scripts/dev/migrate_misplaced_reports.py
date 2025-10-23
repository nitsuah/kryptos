"""Move any mistakenly created src/artifacts/reports/* files to root artifacts/reports.

Safe to run multiple times; skips if destinations already exist.
"""

from __future__ import annotations

import shutil

from kryptos.paths import _PROJECT_ROOT, REPORTS_DIR, ensure_reports_dir  # type: ignore[attr-defined]

MISPLACED = _PROJECT_ROOT / 'src' / 'artifacts' / 'reports'


def migrate() -> None:
    if not MISPLACED.exists() or not MISPLACED.is_dir():
        print('No misplaced reports directory found.')
        return
    ensure_reports_dir()
    moved = 0
    for item in MISPLACED.iterdir():
        if item.is_file():
            dest = REPORTS_DIR / item.name
            if dest.exists():
                print(f'Skip {item.name} (already exists at destination)')
                continue
            shutil.move(str(item), str(dest))
            moved += 1
    print(f'Migrated {moved} files to {REPORTS_DIR}')
    # Optionally remove empty tree
    try:
        if not any(MISPLACED.iterdir()):
            MISPLACED.rmdir()
            parent = MISPLACED.parent
            if parent.name == 'artifacts' and not any(parent.iterdir()):
                parent.rmdir()
    except OSError:
        pass


if __name__ == '__main__':
    migrate()
