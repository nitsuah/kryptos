"""Generate a top-3 candidates markdown report from the latest condensed_report.csv.

Writes: artifacts/reports/top_candidates_<ts>.md
"""

import csv
from datetime import datetime
from pathlib import Path

_here = Path(__file__).resolve()
ROOT = _here
for p in _here.parents:
    if (p / 'pyproject.toml').exists():
        ROOT = p
        break
print(f'[generate_top_candidates] repo root resolved to {ROOT}')
RUNS = ROOT / 'artifacts' / 'tuning_runs'
OUT_DIR = ROOT / 'artifacts' / 'reports'
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not RUNS.exists():
    raise SystemExit(f'No tuning runs root found at {RUNS}')
all_runs = sorted(
    [p for p in RUNS.iterdir() if p.is_dir() and p.name.startswith('run_')],
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)
if not all_runs:
    raise SystemExit('No tuning runs directories found')

# pick the most recent run that contains condensed_report.csv
latest = None
for r in all_runs:
    if (r / 'condensed_report.csv').exists():
        latest = r
        break
if latest is None:
    raise SystemExit('No tuning runs with condensed_report.csv found')
condensed = latest / 'condensed_report.csv'

rows = []
with condensed.open('r', encoding='utf-8') as fh:
    r = csv.DictReader(fh)
    for row in r:
        raw_delta = row.get('top_delta', '0')
        try:
            delta = float(raw_delta)
        except (TypeError, ValueError):
            delta = 0.0
        rows.append({'weight': row.get('weight', ''), 'delta': delta, 'sample': row.get('sample_snippet', '')})
if not rows:
    print('Condensed report has header only; no candidate rows. Nothing to report.')
    raise SystemExit(0)

rows_sorted = sorted(rows, key=lambda x: x['delta'], reverse=True)
top3 = rows_sorted[:3]

# find SPY matches referencing files in this run
learned = ROOT / 'agents' / 'LEARNED.md'
learned_lines = []
if learned.exists():
    with learned.open('r', encoding='utf-8') as fh:
        learned_lines = [ln.strip() for ln in fh if ln.strip()]

# Map file names to learned lines
file_to_learned = {}
for ln in learned_lines:
    for f in latest.iterdir():
        if f.is_file() and f.name in ln:
            file_to_learned.setdefault(f.name, []).append(ln)

# write markdown report
ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
out_file = OUT_DIR / f'top_candidates_{ts}.md'
with out_file.open('w', encoding='utf-8') as of:
    of.write('# Top K4 Candidates Report\n\n')
    of.write(f'Generated: {ts}\n\n')
    of.write(f'Latest tuning run: {latest}\n\n')

    for i, cand in enumerate(top3, start=1):
        of.write(f'## Candidate {i}\n')
        of.write(f'- weight: {cand["weight"]}\n')
        of.write(f'- top_delta: {cand["delta"]:.6f}\n')
        of.write(f'- sample_snippet: "{cand["sample"]}"\n')
        # attempt to find matching detail file for this weight
        fname_prefix = f'weight_{cand["weight"].replace(".", "_")}_details.csv'
        detail_path = latest / fname_prefix
        if detail_path.exists():
            of.write(f'- detail_file: {detail_path}\n')
            learns = file_to_learned.get(detail_path.name, [])
            if learns:
                of.write('- SPY matches:\n')
                for learn_line in learns:
                    of.write(f'  - {learn_line}\n')
        of.write('\n')

print('Wrote report to', out_file)
print(out_file)
