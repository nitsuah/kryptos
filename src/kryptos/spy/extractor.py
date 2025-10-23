"""Conservative SPY extractor (migrated from scripts/dev/spy_extractor.py).

Key differences vs original script:
- Refactored into pure functions with a SpyMatch dataclass.
- No direct argparse usage; CLI can wrap extract() later.
- append_learned() returns the line it wrote (facilitates testing).
- scan_run() returns structured SpyMatch objects instead of tuples.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # src/kryptos/spy -> kryptos -> src -> repo root
AGENTS_DIR = REPO / 'agents'
LEARNED = AGENTS_DIR / 'LEARNED.md'
CRIBS_DEFAULT = REPO / 'docs' / 'sources' / 'sanborn_crib_candidates.txt'


@dataclass(slots=True)
class SpyMatch:
    filename: str
    tokens: tuple[str, ...]
    delta: float
    confidence: float

    def to_note(self) -> str:
        toks = ','.join(self.tokens)
        return f"SPY_MATCH {self.filename}: {toks} (delta={self.delta:.6f}, conf={self.confidence:.2f})"


def load_cribs(path: Path = CRIBS_DEFAULT) -> set[str]:
    out: set[str] = set()
    if not path.exists():
        return out
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tok = line.split('\t')[0].strip().upper()
            if tok:
                out.add(tok)
    return out


def find_latest_run() -> Path | None:
    tr = REPO / 'artifacts' / 'tuning_runs'
    if not tr.exists():
        return None
    runs = [p for p in tr.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return None
    latest = max(runs, key=lambda p: p.stat().st_mtime)
    return latest


def scan_run(run_dir: Path, cribs: set[str]) -> list[SpyMatch]:
    results: list[SpyMatch] = []
    seen_tokens: set[str] = set()
    for csvf in run_dir.glob('weight_*_details.csv'):
        with csvf.open('r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                sample = row.get('sample', '')
                try:
                    delta = float(row.get('delta', '0'))
                except Exception:
                    delta = 0.0
                if delta <= 0:
                    continue
                text = sample.upper()
                # Extract all uppercase 3+ letter tokens (quoted handling simplified for robustness)
                tokens_to_check = re.findall(r'[A-Z]{3,}', text)
                matches = [t for t in tokens_to_check if t in cribs and t not in seen_tokens]
                if matches:
                    for t in matches:
                        seen_tokens.add(t)
                    # confidence computed later once we know max delta
                    results.append(SpyMatch(csvf.name, tuple(matches), delta, 0.0))
    # second pass to assign confidence relative to max delta
    max_delta = max((m.delta for m in results), default=0.0)
    for m in results:
        m.confidence = 0.0 if max_delta <= 0 else float(m.delta) / float(max_delta)
    return results


def append_learned(note: str) -> str:
    LEARNED.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().isoformat()
    line = f"- {ts} SPY: {note}\n"
    with LEARNED.open('a', encoding='utf-8') as fh:
        fh.write(line)
    return line


def extract(min_conf: float = 0.0, cribs_path: Path = CRIBS_DEFAULT, run_dir: Path | None = None) -> list[SpyMatch]:
    """Extract SPY matches for a given run directory (or latest if None)."""
    cribs = load_cribs(cribs_path)
    run = run_dir if run_dir is not None else find_latest_run()
    if run is None:
        return []
    matches = scan_run(run, cribs)
    kept: list[SpyMatch] = []
    for m in matches:
        if m.confidence < float(min_conf):
            continue
        append_learned(m.to_note())
        kept.append(m)
    return kept


__all__ = [
    'SpyMatch',
    'load_cribs',
    'find_latest_run',
    'scan_run',
    'extract',
]
