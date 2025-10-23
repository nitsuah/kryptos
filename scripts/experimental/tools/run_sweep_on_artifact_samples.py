"""Run crib-weight sweep using samples from an artifact's crib_integration.csv.

This script will:
- load cribs from `docs/sources/sanborn_crib_candidates.txt` (existing file)
- load sample plaintexts from an artifact `crib_integration.csv` (first column 'sample')
- compute combined_plaintext_score + combined_plaintext_score_with_external_cribs
- write results to a new artifacts run folder.
"""

from __future__ import annotations

import csv
import importlib
import sys
import time
from pathlib import Path

_here = Path(__file__).resolve()
ROOT = _here
for p in _here.parents:
    if (p / 'pyproject.toml').exists():
        ROOT = p
        break
print(f'[run_sweep_on_artifact_samples] repo root resolved to {ROOT}')
SRC = ROOT / 'src'

# Prefer package import; fall back to adding src/ to sys.path
try:
    scoring = importlib.import_module('src.k4.scoring')
except ImportError:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    scoring = importlib.import_module('k4.scoring')


def load_cribs(path: Path) -> list[str]:
    cribs: list[str] = []
    if not path.exists():
        return cribs
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            tok = parts[0].strip().upper() if parts else ''
            if tok.isalpha() and len(tok) >= 3:
                cribs.append(tok)
    return cribs


def load_samples_from_artifact(artifact_dir: Path) -> list[str]:
    csvp = artifact_dir / 'crib_integration.csv'
    samples: list[str] = []
    if not csvp.exists():
        return samples
    with csvp.open('r', encoding='utf-8') as fh:
        r = csv.reader(fh)
        next(r, None)
        for row in r:
            if row:
                samples.append(row[0])
    return samples


def run(artifact_dir: Path):
    cribs_path = ROOT / 'docs' / 'sources' / 'sanborn_crib_candidates.txt'
    cribs = load_cribs(cribs_path)
    samples = load_samples_from_artifact(artifact_dir)
    if not samples:
        print('No samples found in', artifact_dir)
        return
    # Expanded weight grid to explore sensitivity
    # Focused weights per OPS request
    weights = [0.25, 0.5]
    ts = time.strftime('%Y%m%dT%H%M%S')
    run_dir = ROOT / 'artifacts' / 'tuning_runs' / f'run_{ts}'
    run_dir.mkdir(parents=True, exist_ok=True)
    summary = run_dir / 'crib_weight_sweep_from_artifact.csv'
    with summary.open('w', newline='', encoding='utf-8') as sf:
        writer = csv.writer(sf)
        writer.writerow(['weight', 'sample', 'baseline', 'with_cribs', 'delta'])
        for w in weights:
            # per-weight match details
            per_matches = run_dir / f'matches_weight_{str(w).replace(".", "_")}.csv'
            with per_matches.open('w', newline='', encoding='utf-8') as pmf:
                pmw = csv.writer(pmf)
                pmw.writerow(['sample', 'matched_cribs'])
                for s in samples:
                    base = scoring.combined_plaintext_score(s)
                    # find which cribs appear in the sample (conservative substring match)
                    matched = [c for c in cribs if c in s.upper()]
                    withc = scoring.combined_plaintext_score_with_external_cribs(s, cribs, crib_weight=w)
                    delta = withc - base
                    writer.writerow([f'{w}', s[:80], f'{base:.6f}', f'{withc:.6f}', f'{delta:.6f}'])
                    pmw.writerow([s[:100], '|'.join(matched)])
    print('Wrote', summary)


if __name__ == '__main__':
    # choose a recent artifact run with crib_integration.csv
    cand = ROOT / 'artifacts' / 'tuning_runs' / 'run_20251022T193245'
    run(cand)
