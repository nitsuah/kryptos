"""Centralized filesystem path helpers for kryptos artifacts.

All writable outputs should route through these helpers so directory layout
can evolve without invasive refactors.
"""

from __future__ import annotations

from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent


def _find_project_root(start: Path) -> Path:
    candidates = {'pyproject.toml', '.git'}
    cur = start
    # Allow up to 6 levels climb to avoid runaway
    for _ in range(6):
        if any((cur / c).exists() for c in candidates):
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback: assume package parent parent (kryptos/src/.. -> repo root)
    return start.parent.parent


_PROJECT_ROOT = _find_project_root(_PKG_DIR)

# Base artifacts directory (under project root, not inside src tree)
ARTIFACTS_DIR = (_PROJECT_ROOT / 'artifacts').resolve()

# Reports subdirectory inside artifacts (JSON/CSV attempt & candidate logs).
REPORTS_DIR = ARTIFACTS_DIR / 'reports'


def ensure_reports_dir() -> Path:
    """Ensure the reports directory exists and return its Path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


__all__ = [
    'ARTIFACTS_DIR',
    'REPORTS_DIR',
    'ensure_reports_dir',
]
