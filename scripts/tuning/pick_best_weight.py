"""Simple analyzer for crib_weight_sweep artifacts.

Reads crib_weight_sweep.csv and picks the weight with the largest mean delta across samples.
Writes a short recommendation to stdout.
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path
from statistics import mean

from kryptos.logging import setup_logging


def _normalize_fieldnames(fieldnames: list[str] | None) -> dict[str, str]:
    if not fieldnames:
        return {}
    # ensure concrete list copy
    return {str(fn).strip().lower(): str(fn) for fn in list(fieldnames)}


def pick_best(run_path: Path) -> tuple[float, dict[float, float]]:
    path = run_path / 'crib_weight_sweep.csv'
    if not path.exists():
        raise FileNotFoundError(path)
    by_weight: dict[str, list[float]] = {}
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        rows_list = list(reader)
        norm = _normalize_fieldnames(list(reader.fieldnames) if reader.fieldnames else [])
    for _idx, row in enumerate(rows_list, start=1):
        try:
            weight_str = row.get(norm.get('weight', 'weight')) or row.get('weight')
            if not weight_str:
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
            by_weight.setdefault(weight_str, []).append(delta_val)
        except (ValueError, TypeError):
            # skip bad rows but continue
            continue
    weight_stats = {float(ws): mean(deltas) for ws, deltas in by_weight.items() if deltas}
    if not weight_stats:
        raise RuntimeError('no usable data in crib_weight_sweep.csv')
    # pick max mean delta
    best_w = max(weight_stats.items(), key=lambda kv: kv[1])[0]
    return best_w, weight_stats


def find_latest_run(repo_root: Path) -> Path:
    runs_dir = repo_root / 'artifacts' / 'tuning_runs'
    runs = sorted(runs_dir.glob('run_*'), reverse=True)
    if not runs:
        raise FileNotFoundError('No tuning_runs found')
    return runs[0]


if __name__ == '__main__':
    setup_logging(level=logging.INFO, logger_name="kryptos.tuning")
    log = logging.getLogger("kryptos.tuning")
    repo_root = Path(__file__).resolve().parents[2]
    run_arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    try:
        run_dir = run_arg_path if run_arg_path else find_latest_run(repo_root)
    except (FileNotFoundError, RuntimeError) as exc:
        log.error('Error locating run: %s', exc)
        raise SystemExit(2) from exc
    try:
        best, stats_map = pick_best(run_dir)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        log.error('Error computing best weight: %s', exc)
        raise SystemExit(2) from exc
    log.info('Run: %s', run_dir)
    for weight_val, mean_delta in sorted(stats_map.items()):
        log.info('weight=%.3f mean_delta=%.6f', weight_val, mean_delta)
    log.info('Best weight: %.3f', best)
    log.info('Recommended SPY min_conf (fallback): 0.25')
