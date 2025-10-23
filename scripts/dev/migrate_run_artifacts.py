"""One-off helper to migrate pre-existing run_* directories into artifacts/k4_runs/.

Usage:
    python scripts/dev/migrate_run_artifacts.py --dry-run  # show planned moves
    python scripts/dev/migrate_run_artifacts.py            # perform moves

Moves only directories directly under artifacts/ matching run_YYYYMMDDT* and having summary.json.
Skips if target already exists. Safe to re-run.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def find_runs(root: Path) -> list[Path]:
    out: list[Path] = []
    for child in root.iterdir():
        if child.is_dir() and child.name.startswith('run_') and (child / 'summary.json').exists():
            out.append(child)
    return sorted(out)


def migrate(root: Path, dry_run: bool = True) -> list[tuple[Path, Path]]:
    k4_dir = root / 'k4_runs'
    k4_dir.mkdir(parents=True, exist_ok=True)
    moves: list[tuple[Path, Path]] = []
    for run_dir in find_runs(root):
        target = k4_dir / run_dir.name
        if target.exists():
            continue
        moves.append((run_dir, target))
        if not dry_run:
            shutil.move(str(run_dir), str(target))
    return moves


def main() -> int:
    p = argparse.ArgumentParser(description='Migrate legacy artifacts/run_* to artifacts/k4_runs/')
    p.add_argument('--artifacts-root', type=str, default='artifacts', help='Root artifacts directory')
    p.add_argument('--dry-run', action='store_true', help='Preview moves only')
    args = p.parse_args()
    root = Path(args.artifacts_root)
    if not root.exists():
        print(f'Artifacts root not found: {root}')
        return 2
    moves = migrate(root, dry_run=args.dry_run)
    if args.dry_run:
        if not moves:
            print('No legacy run_ directories to migrate.')
        else:
            print('Planned moves:')
            for src, dst in moves:
                print(f'  {src} -> {dst}')
    else:
        print(f'Migrated {len(moves)} directories.')
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
