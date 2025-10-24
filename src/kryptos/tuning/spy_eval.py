"""Package-level SPY evaluation harness.

This is a near-copy of `scripts/tuning/spy_eval.py` moved into the package so tests and
imports are robust when the project is installed or run inside venvs.
"""

from __future__ import annotations

import csv
from pathlib import Path


def load_labels(path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    if not path.exists():
        return out
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue
            run, tok = row[0].strip(), row[1].strip().upper()
            out.setdefault(run, set()).add(tok)
    return out


def select_best_threshold(labels_p: Path, runs_root_p: Path, thresholds: list[float] | None = None) -> float:
    eval_map = evaluate(labels_p, runs_root_p, thresholds=thresholds)
    if not eval_map:
        return 0.0
    chosen_th = 0.0
    best_precision = -1.0
    best_f1_local = -1.0
    for th_val, triple in eval_map.items():
        precision_val, _rec_val, f1_val = triple
        if precision_val > best_precision or (precision_val == best_precision and f1_val > best_f1_local):
            best_precision = precision_val
            best_f1_local = f1_val
            chosen_th = th_val
    return float(chosen_th)


def run_extractor_on_run(run_dir: Path, min_conf: float = 0.0) -> set[str]:
    try:
        from kryptos.scripts.dev import spy_extractor as spy_mod
    except ImportError:
        return set()

    cribs = spy_mod.load_cribs(spy_mod.CRIBS)
    scan_res = spy_mod.scan_run(run_dir, cribs)
    max_delta = max((d for _, _, d in scan_res), default=0.0)
    tokens = set()
    for _, matches, delta in scan_res:
        conf = 0.0 if max_delta <= 0 else float(delta) / float(max_delta)
        if conf >= min_conf:
            for t in matches.split(','):
                tokens.add(t)
    return tokens


def evaluate(
    labels_p: Path,
    runs_root_p: Path,
    thresholds: list[float] | None = None,
) -> dict[float, tuple[float, float, float]]:
    labels = load_labels(labels_p)
    if thresholds is None:
        thresholds = [0.0, 0.25, 0.5, 0.75]
    out: dict[float, tuple[float, float, float]] = {}
    for threshold in thresholds:
        tp = 0
        fp = 0
        fn = 0
        for run_dir in runs_root_p.iterdir():
            if not run_dir.is_dir() or not run_dir.name.startswith('run_'):
                continue
            run_name = run_dir.name
            true = labels.get(run_name, set())
            preds = run_extractor_on_run(run_dir, min_conf=threshold)
            tp += len(preds & true)
            fp += len(preds - true)
            fn += len(true - preds)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        out[threshold] = (precision, recall, f1_score)
    return out


if __name__ == '__main__':
    import argparse

    from kryptos.logging import setup_logging

    p = argparse.ArgumentParser(description='Evaluate SPY extractor across thresholds')
    p.add_argument('--labels', type=str, default='data/spy_eval_labels.csv', help='CSV of run_dir,token')
    p.add_argument('--runs', type=str, default='artifacts/tuning_runs', help='Root tuning runs folder')
    args = p.parse_args()
    labels_path = Path(args.labels)
    runs_root = Path(args.runs)
    eval_res = evaluate(labels_path, runs_root)
    logger = setup_logging(logger_name="kryptos.spy")
    for th, (prec_v, rec_v, f1_v) in eval_res.items():
        logger.info("th=%.2f prec=%.3f rec=%.3f f1=%.3f", th, prec_v, rec_v, f1_v)
