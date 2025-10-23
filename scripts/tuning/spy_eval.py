"""SPY evaluation harness

Scans tuning runs and computes precision/recall/F1 for SPY extractor matches
against a labeled CSV of expected crib tokens per run.

Labels CSV format: run_dir,token
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


def select_best_threshold(labels_path: Path, runs_root: Path, thresholds: list[float] | None = None) -> float:
    """Select the threshold preferring precision (more conservative extraction).

    The selection now prefers the threshold with the highest precision. If
    multiple thresholds share the same precision, pick the one with the
    highest F1 as a tie-breaker. Returns 0.0 if no data is available.
    """
    res = evaluate(labels_path, runs_root, thresholds=thresholds)
    if not res:
        return 0.0
    # pick threshold with max precision; tie-breaker picks the higher F1
    best_th = 0.0
    best_prec = -1.0
    best_f1 = -1.0
    for th, (prec_v, _rec_v, f1_v) in res.items():
        if prec_v > best_prec or (prec_v == best_prec and f1_v > best_f1):
            best_prec = prec_v
            best_f1 = f1_v
            best_th = th
    return float(best_th)


def run_extractor_on_run(run_dir: Path, min_conf: float = 0.0) -> set[str]:
    # import the installed package's spy_extractor and call scan_run directly
    try:
        from kryptos.scripts.dev import spy_extractor as spy_mod
    except Exception:
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
    labels_path: Path,
    runs_root: Path,
    thresholds: list[float] | None = None,
) -> dict[float, tuple[float, float, float]]:
    labels = load_labels(labels_path)
    if thresholds is None:
        thresholds = [0.0, 0.25, 0.5, 0.75]
    out: dict[float, tuple[float, float, float]] = {}
    for threshold in thresholds:
        tp = 0
        fp = 0
        fn = 0
        for run_dir in runs_root.iterdir():
            if not run_dir.is_dir() or not run_dir.name.startswith('run_'):
                continue
            run_name = run_dir.name
            true = labels.get(run_name, set())
            preds = run_extractor_on_run(run_dir, min_conf=threshold)
            tp += len(preds & true)
            fp += len(preds - true)
            fn += len(true - preds)
        prec_v = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec_v = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_v = (2 * prec_v * rec_v / (prec_v + rec_v)) if (prec_v + rec_v) > 0 else 0.0
        out[threshold] = (prec_v, rec_v, f1_v)
    return out


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Evaluate SPY extractor across thresholds')
    p.add_argument('--labels', type=str, default='data/spy_eval_labels.csv', help='CSV of run_dir,token')
    p.add_argument('--runs', type=str, default='artifacts/tuning_runs', help='Root tuning runs folder')
    args = p.parse_args()
    labels_path = Path(args.labels)
    runs_root = Path(args.runs)
    eval_res = evaluate(labels_path, runs_root)
    for th, (prec_v, rec_v, f1_v) in eval_res.items():
        print(f'th={th:.2f} prec={prec_v:.3f} rec={rec_v:.3f} f1={f1_v:.3f}')
