"""Clean duplicated matches and summarize match+delta info for latest artifact run.

Writes cleaned match files (overwrites) and creates artifact_summary.txt in the run folder.
"""

from __future__ import annotations

import csv
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


def load_sweep_csv(run_dir: Path):
    s = run_dir / 'crib_weight_sweep_from_artifact.csv'
    if not s.exists():
        return []
    rows = []
    with s.open('r', encoding='utf-8') as fh:
        r = csv.reader(fh)
        next(r, None)
        for row in r:
            if row:
                rows.append(row)
    return rows


def clean_matches_file(path: Path):
    if not path.exists():
        return []
    out = []
    with path.open('r', encoding='utf-8') as fh:
        r = csv.reader(fh)
        next(r, None)
        for row in r:
            sample = row[0]
            matched = row[1] if len(row) > 1 else ''
            if matched:
                parts = [p for p in matched.split('|') if p]
                uniq = sorted(set(parts))
                joined = '|'.join(uniq)
            else:
                joined = ''
            out.append((sample, joined))
    # overwrite
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['sample', 'matched_cribs'])
        for s, m in out:
            w.writerow([s, m])
    return out


def summarize(run_dir: Path, sweep_rows, cleaned_matches_per_weight):
    outp = run_dir / 'artifact_summary.txt'
    with outp.open('w', encoding='utf-8') as fh:
        fh.write(f'Artifact run: {run_dir.name}\n')
        fh.write('Summary of crib-weight deltas and matches\n\n')
        # map (weight, sample->matched)
        matches_map = {}
        for w, entries in cleaned_matches_per_weight.items():
            for sample, matched in entries:
                matches_map[(str(w), sample[:100])] = matched
        fh.write('Top deltas:\n')
        # sort sweep rows by absolute delta desc
        parsed = []
        for row in sweep_rows:
            try:
                w = row[0]
                sample = row[1]
                delta = float(row[4])
                parsed.append((abs(delta), delta, w, sample))
            except ValueError:
                continue
        parsed.sort(reverse=True)
        for _, delta, w, sample in parsed[:10]:
            matched = matches_map.get((w, sample[:100]), '')
            fh.write(f'weight={w} delta={delta:+.1f} matches={matched} sample="{sample[:120]}"\n')
    return outp


def main():
    run_dir = find_latest_run()
    if not run_dir:
        print('no runs found')
        sys.exit(1)
    sweep_rows = load_sweep_csv(run_dir)
    cleaned = {}
    # find match files
    for f in run_dir.glob('matches_weight_*.csv'):
        # extract weight
        w = f.stem.replace('matches_weight_', '')
        entries = clean_matches_file(f)
        cleaned[w] = entries
    summary = summarize(run_dir, sweep_rows, cleaned)
    print('Wrote summary:', summary)


if __name__ == '__main__':
    main()
