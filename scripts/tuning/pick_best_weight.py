"""Simple analyzer for crib_weight_sweep artifacts.

Reads crib_weight_sweep.csv and picks the weight with the largest mean delta across samples.
Writes a short recommendation to stdout.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from statistics import mean


def _normalize_fieldnames(fieldnames: list[str] | None):
    if not fieldnames:
        return {}
    return {fn.strip().lower(): fn for fn in fieldnames}


def pick_best(run_dir: Path) -> tuple[float, dict]:
    path = run_dir / 'crib_weight_sweep.csv'
    if not path.exists():
        raise FileNotFoundError(path)
    by_weight: dict[str, list[float]] = {}
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        norm = _normalize_fieldnames(reader.fieldnames)
    for _i, row in enumerate(rows, start=1):
        try:
            w = row.get(norm.get('weight', 'weight'))
            if w is None:
                # try fallback direct key
                w = row.get('weight')
            if not w:
                # skip rows without weight
                continue
            # try delta column first; otherwise compute from with_cribs - baseline
            delta_val = None
            if 'delta' in norm:
                raw = row.get(norm['delta'])
                if raw is not None and raw != '':
                    delta_val = float(raw)
            if delta_val is None:
                # attempt compute
                b = row.get(norm.get('baseline', 'baseline')) or row.get('baseline')
                wc = row.get(norm.get('with_cribs', 'with_cribs')) or row.get('with_cribs')
                if b is None or wc is None or b == '' or wc == '':
                    # can't compute delta for this row
                    continue
                delta_val = float(wc) - float(b)
            by_weight.setdefault(w, []).append(delta_val)
        except Exception:
            # skip bad rows but continue
            continue
    stats = {float(w): mean(deltas) for w, deltas in by_weight.items() if deltas}
    if not stats:
        raise RuntimeError('no usable data in crib_weight_sweep.csv')
    # pick max mean delta
    best_w = max(stats.items(), key=lambda kv: kv[1])[0]
    return best_w, stats


def find_latest_run(root: Path) -> Path:
    runs_dir = root / 'artifacts' / 'tuning_runs'
    runs = sorted(runs_dir.glob('run_*'), reverse=True)
    if not runs:
        raise FileNotFoundError('No tuning_runs found')
    return runs[0]


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    # optional first CLI arg: run dir
    run_arg = None
    if len(sys.argv) > 1:
        run_arg = Path(sys.argv[1])
    try:
        run = Path(run_arg) if run_arg else find_latest_run(root)
    except Exception as exc:
        print('Error locating run:', exc)
        sys.exit(2)

    try:
        best, stats = pick_best(run)
    except Exception as exc:
        print('Error:', exc)
        sys.exit(2)
    print('Run:', run)
    print('Mean deltas per weight:')
    for w, v in sorted(stats.items()):
        print(f'  {w}: {v:.6f}')
    print(f'Best weight: {best:.3f}')
    # recommend conservative SPY min_conf default placeholder
    print('Recommended SPY min_conf (fallback): 0.25')
