"""Generate a condensed CSV summarizing top deltas per weight from a tuning run.

Usage: run from repo root. Writes `artifacts/tuning_runs/<run>/condensed_report.csv`.
"""

import csv
from collections import defaultdict
from pathlib import Path

RUN_DIR = Path('artifacts/tuning_runs').expanduser().resolve()
# find latest run
runs = sorted([p for p in RUN_DIR.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
if not runs:
    raise SystemExit('No tuning runs found')
run = runs[0]

summary = run / 'crib_weight_sweep.csv'
if not summary.exists():
    raise SystemExit(f'No summary file found at {summary}')

rows = []
with summary.open('r', encoding='utf-8') as fh:
    header = fh.readline()
    for ln in fh:
        parts = ln.strip().split(',')
        if len(parts) >= 5:
            weight = parts[0]
            sample = parts[1]
            delta = float(parts[4])
            rows.append((weight, delta, sample))

# find top delta per weight
best = defaultdict(lambda: (0.0, ''))
for weight, delta, sample in rows:
    if delta > best[weight][0]:
        best[weight] = (delta, sample)

out = run / 'condensed_report.csv'
with out.open('w', newline='', encoding='utf-8') as of:
    w = csv.writer(of)
    w.writerow(['weight', 'top_delta', 'sample_snippet'])
    for weight, (delta, sample) in sorted(best.items()):
        w.writerow([weight, f"{delta:.6f}", sample[:120]])

print('Wrote condensed report to', out)
