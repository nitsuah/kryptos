"""Phrase aggregation (migrated from scripts/experimental/tools/aggregate_spy_phrases.py).

Differences vs script:
- Pure function aggregate_phrases returning count of phrases written (int) or -1 if input missing.
- No print side-effects by default (optional verbose flag).
"""

from __future__ import annotations

import csv
from pathlib import Path

RANK = {'low': 0, 'med': 1, 'high': 2}


def aggregate_phrases(input_path: Path, output_path: Path, verbose: bool = False) -> int:
    if not input_path.exists():
        if verbose:
            print('No input found:', input_path)
        return -1
    phrases: dict[str, dict] = {}
    with input_path.open(encoding='utf-8') as fh:
        for line in fh:
            parts = line.rstrip('\n').split('\t')
            if len(parts) != 4:
                continue
            _token, src, excerpt, conf = parts
            prev = phrases.get(excerpt)
            if prev is None or RANK.get(conf, 0) > RANK.get(prev['conf'], 0):
                phrases[excerpt] = {'src': src, 'conf': conf}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8', newline='') as out:
        w = csv.writer(out, delimiter='\t')
        w.writerow(['EXCERPT', 'SOURCE', 'CONFIDENCE'])
        for excerpt, meta in phrases.items():
            w.writerow([excerpt, meta['src'], meta['conf']])
    if verbose:
        print('Wrote', output_path)
    return len(phrases)


__all__ = ['aggregate_phrases']
