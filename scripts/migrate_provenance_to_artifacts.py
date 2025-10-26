"""Migrate provenance data from data/ to artifacts/.

This script moves runtime state files from data/ to artifacts/ to fix the
directory structure. Runtime state should be in artifacts/ (git-ignored),
while source data stays in data/ (committed).

Run with --dry-run first to see what would be moved.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

# Directories to migrate
MIGRATIONS = [
    ("data/search_space", "artifacts/search_space"),
    ("data/attack_logs", "artifacts/attack_logs"),
    ("data/ops_strategy", "artifacts/ops_strategy"),
    ("data/intel_cache", "artifacts/intel_cache"),
]


def migrate_directory(src: Path, dst: Path, dry_run: bool = False) -> tuple[int, int]:
    """Move directory from src to dst.

    Returns:
        (files_moved, bytes_moved)
    """
    if not src.exists():
        print(f"⏭️  Skip: {src} (doesn't exist)")
        return 0, 0

    if dst.exists():
        print(f"⚠️  Warning: {dst} already exists")
        response = input("Merge contents? [y/N]: ")
        if response.lower() != 'y':
            print(f"⏭️  Skipping {src}")
            return 0, 0

    files_moved = 0
    bytes_moved = 0

    # Create destination parent
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)

    # Count files and bytes
    if src.is_file():
        files_moved = 1
        bytes_moved = src.stat().st_size
        print(f"📄 {'Would move' if dry_run else 'Moving'}: {src} -> {dst} ({bytes_moved:,} bytes)")
        if not dry_run:
            shutil.move(str(src), str(dst))
    else:
        for item in src.rglob("*"):
            if item.is_file():
                files_moved += 1
                size = item.stat().st_size
                bytes_moved += size

                rel_path = item.relative_to(src)
                dst_file = dst / rel_path

                print(f"📄 {'Would move' if dry_run else 'Moving'}: {item} -> {dst_file}")

                if not dry_run:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dst_file))

        # Remove empty source directory
        if not dry_run and src.exists():
            try:
                src.rmdir()
                print(f"🗑️  Removed empty directory: {src}")
            except OSError:
                print(f"⚠️  Warning: Could not remove {src} (not empty)")

    return files_moved, bytes_moved


def main():
    parser = argparse.ArgumentParser(description="Migrate provenance data to artifacts/")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without moving")
    args = parser.parse_args()

    print("=" * 80)
    print("Kryptos Provenance Migration")
    print("=" * 80)
    print()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    if args.dry_run:
        print("⚠️  DRY RUN MODE - No files will be moved")
        print()
    else:
        print("⚠️  LIVE MODE - Files will be moved!")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
        print()

    total_files = 0
    total_bytes = 0

    for src_rel, dst_rel in MIGRATIONS:
        src = PROJECT_ROOT / src_rel
        dst = PROJECT_ROOT / dst_rel

        print(f"\n📦 Migration: {src_rel} → {dst_rel}")
        print("-" * 80)

        files, bytes_moved = migrate_directory(src, dst, dry_run=args.dry_run)
        total_files += files
        total_bytes += bytes_moved

        print(f"✅ Migrated {files:,} files ({bytes_moved:,} bytes)")

    print()
    print("=" * 80)
    print(f"Total: {total_files:,} files, {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
    print("=" * 80)

    if args.dry_run:
        print()
        print("This was a DRY RUN. Run without --dry-run to actually move files.")
    else:
        print()
        print("✅ Migration complete!")
        print()
        print("Next steps:")
        print("1. Update module imports to use get_artifacts_root()")
        print("2. Run tests to verify everything still works")
        print("3. Commit the updated code (not the artifacts)")

    return 0


if __name__ == "__main__":
    exit(main())
