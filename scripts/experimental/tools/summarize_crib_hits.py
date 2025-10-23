"""Summarize crib hit counts from the latest artifact run's match files.

Writes `crib_hit_counts.json` and appends a human-readable crib counts section to `artifact_summary.txt`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART_ROOT = ROOT / 'artifacts' / 'tuning_runs'


def find_latest_run():
    runs = [p for p in ART_ROOT.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return None
    runs.sort()
    return runs[-1]


def load_matches(run_dir: Path):
    matches = {}
    for f in run_dir.glob('matches_weight_*.csv'):
        with f.open('r', encoding='utf-8') as fh:
            # skip header
            next(fh, None)
            for line in fh:
                parts = line.rstrip('\n').split(',', 1)
                if len(parts) < 2:
                    continue
                matched = parts[1].strip()
                if not matched:
                    continue
                for crib in matched.split('|'):
                    crib = crib.strip()
                    if not crib:
                        continue
                    matches.setdefault(crib, 0)
                    matches[crib] += 1
    return matches


def append_summary(run_dir: Path, counts: dict[str, int]):
    summary = run_dir / 'artifact_summary.txt'
    with summary.open('a', encoding='utf-8') as fh:
        fh.write('\nCrib hit counts:\n')
        for crib, cnt in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
            fh.write(f'{crib}: {cnt}\n')
    return summary


def main():
    run_dir = find_latest_run()
    if not run_dir:
        print('No runs found')
        sys.exit(1)
    counts = load_matches(run_dir)
    out_json = run_dir / 'crib_hit_counts.json'
    out_json.write_text(json.dumps(counts, indent=2), encoding='utf-8')
    summary = append_summary(run_dir, counts)
    print('Wrote', out_json, 'and updated', summary)


if __name__ == '__main__':
    main()
