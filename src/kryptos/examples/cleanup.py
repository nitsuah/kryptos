"""Helpers to manage / purge demo artifact directories.

We keep demo outputs under ``artifacts/demo/``. These can accumulate quickly in
CI or local iteration. ``purge_demo_artifacts`` removes demo subdirectories
older than an age threshold (in hours) or exceeding a max count.

Both constraints can be combined: we first filter by age, then if the remaining
count still exceeds ``max_keep`` we delete the oldest until within the limit.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass(slots=True)
class PurgeResult:
    removed: list[Path]
    kept: list[Path]


def _iter_demo_dirs(root: Path) -> Iterable[Path]:
    demo_root = root / "demo"
    if not demo_root.exists():  # pragma: no cover - absent in fresh checkout
        return []
    for p in demo_root.iterdir():
        if p.is_dir():
            yield p


def purge_demo_artifacts(max_age_hours: int | None = 24, max_keep: int | None = 10) -> PurgeResult:
    """Purge demo artifact subdirectories based on age and count.

    Parameters
    ----------
    max_age_hours:
        Remove any demo directory whose newest mtime is older than this many hours.
        If ``None`` age filtering is skipped.
    max_keep:
        After age filtering, ensure only this many *newest* demo directories remain.
        If ``None`` count limiting is skipped.

    Returns
    -------
    PurgeResult
        Lists of removed and kept directories.
    """
    # Import dynamically so tests can monkeypatch kryptos.paths.get_artifacts_root
    from kryptos import paths as _paths  # local import to avoid binding early

    root = _paths.get_artifacts_root()
    now = datetime.utcnow()
    demo_dirs = list(_iter_demo_dirs(root))
    # Annotate with newest mtime (files or dir itself)
    annotated: list[tuple[Path, float]] = []
    for d in demo_dirs:
        newest = d.stat().st_mtime
        for sub in d.rglob('*'):
            try:
                mt = sub.stat().st_mtime
            except OSError:  # pragma: no cover - transient deletion race
                continue
            if mt > newest:
                newest = mt
        annotated.append((d, newest))
    # Age filter
    to_consider: list[tuple[Path, float]] = []
    removed: list[Path] = []
    if max_age_hours is not None:
        cutoff = now - timedelta(hours=max_age_hours)
        cutoff_ts = cutoff.timestamp()
        for d, mt in annotated:
            if mt < cutoff_ts:
                removed.append(d)
            else:
                to_consider.append((d, mt))
    else:
        to_consider = annotated
    # Count limiting
    if max_keep is not None and len(to_consider) > max_keep:
        # Sort newest first
        to_consider.sort(key=lambda x: x[1], reverse=True)
        keep = to_consider[:max_keep]
        spill = to_consider[max_keep:]
        removed.extend([p for p, _ in spill])
        kept_dirs = [p for p, _ in keep]
    else:
        kept_dirs = [p for p, _ in to_consider]
    # Perform deletions
    for d in removed:
        try:
            for sub in sorted(d.rglob('*'), reverse=True):
                if sub.is_file() or sub.is_symlink():
                    sub.unlink(missing_ok=True)  # type: ignore[arg-type]
                elif sub.is_dir():
                    sub.rmdir()
            d.rmdir()
        except OSError:
            # Best effort; ignore failures (permissions, races)
            continue
    return PurgeResult(removed=removed, kept=kept_dirs)


__all__ = ["purge_demo_artifacts", "PurgeResult"]
