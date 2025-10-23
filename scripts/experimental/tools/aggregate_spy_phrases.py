"""Aggregate the SPY crib token TSV into deduplicated quoted phrases.

Reads `agents/output/spy_cribs.tsv` and writes `agents/output/spy_crib_phrases.tsv` containing
unique excerpt -> source -> confidence (highest seen).
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IN_PATH = ROOT / 'agents' / 'output' / 'spy_cribs.tsv'
OUT_PATH = ROOT / 'agents' / 'output' / 'spy_crib_phrases.tsv'


def run():
    if not IN_PATH.exists():
        print('No input found:', IN_PATH)
        return
    phrases: dict[str, dict] = {}
    with open(IN_PATH, encoding='utf-8') as fh:
        for line in fh:
            parts = line.rstrip('\n').split('\t')
            if len(parts) != 4:
                continue
            token, src, excerpt, conf = parts
            # Use excerpt as key (full phrase); prefer highest confidence order: high>med>low
            prev = phrases.get(excerpt)
            rank = {'low': 0, 'med': 1, 'high': 2}
            if prev is None or rank.get(conf, 0) > rank.get(prev['conf'], 0):
                phrases[excerpt] = {'src': src, 'conf': conf}
    # write out
    with open(OUT_PATH, 'w', encoding='utf-8', newline='') as out:
        w = csv.writer(out, delimiter='\t')
        w.writerow(['EXCERPT', 'SOURCE', 'CONFIDENCE'])
        for excerpt, meta in phrases.items():
            w.writerow([excerpt, meta['src'], meta['conf']])
    print('Wrote', OUT_PATH)


if __name__ == '__main__':
    run()
