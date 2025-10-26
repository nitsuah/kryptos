"""SPY extraction & aggregation utilities.

Public API:
- load_cribs(path: Path) -> set[str]
- find_latest_run() -> Path | None
- scan_run(run_dir: Path, cribs: set[str]) -> list[SpyMatch]
- extract(min_conf: float = 0.0) -> list[SpyMatch]  (appends to artifacts/spy_extractions/LEARNED.md)
- aggregate_phrases(input_path: Path, output_path: Path) -> int

These functions consolidate prior dev/experimental scripts:
- scripts/dev/spy_extractor.py
- scripts/experimental/tools/aggregate_spy_phrases.py

They are pure (aside from extract() writing LEARNED.md) and testable.
"""

from .aggregate import aggregate_phrases
from .extractor import SpyMatch, extract, find_latest_run, load_cribs, scan_run

__all__ = [
    'load_cribs',
    'find_latest_run',
    'scan_run',
    'extract',
    'SpyMatch',
    'aggregate_phrases',
]
