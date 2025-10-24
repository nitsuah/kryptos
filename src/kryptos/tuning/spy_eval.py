"""Package-level SPY evaluation harness.

This is a near-copy of `scripts/tuning/spy_eval.py` moved into the package so tests and
imports are robust when the project is installed or run inside venvs.
"""

from __future__ import annotations

import csv
from collections.abc import Callable
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


def select_best_threshold(
    labels_p: Path,
    runs_root_p: Path,
    thresholds: list[float] | None = None,
    extractor: Callable[[Path, float], set[str]] | None = None,
) -> float:
    eval_map = evaluate(labels_p, runs_root_p, thresholds=thresholds, extractor=extractor)
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
    """Default extraction using package spy extract API.

    Returns uppercase tokens with confidence >= min_conf. Empty set on failure.
    """
    try:
        from kryptos.spy import extract as spy_extract
    except ImportError:
        return set()
    try:
        matches = spy_extract(min_conf=min_conf, run_dir=run_dir)
    except (RuntimeError, OSError, ValueError):  # narrow expected failure types
        return set()
    tokens: set[str] = set()
    for m in matches:
        for t in m.tokens:
            tokens.add(t.upper())
    return tokens


def evaluate(
    labels_p: Path,
    runs_root_p: Path,
    thresholds: list[float] | None = None,
    extractor: Callable[[Path, float], set[str]] | None = None,
) -> dict[float, tuple[float, float, float]]:
    def safe_div(n: float, d: float, default: float = 0.0) -> float:
        if d == 0:
            return default
        # No broad try/except: allow unforeseen errors to surface during tests
        return n / d

    labels = load_labels(labels_p)
    if thresholds is None:
        thresholds = [0.0, 0.25, 0.5, 0.75]
    use_extractor = extractor or run_extractor_on_run
    out: dict[float, tuple[float, float, float]] = {}
    for threshold in thresholds:
        tp = fp = fn = 0
        for run_dir in runs_root_p.iterdir():
            if not run_dir.is_dir() or not run_dir.name.startswith('run_'):
                continue
            run_name = run_dir.name
            true = labels.get(run_name, set())
            preds = use_extractor(run_dir, threshold)
            tp += len(preds & true)
            fp += len(preds - true)
            fn += len(true - preds)
        precision = safe_div(tp, (tp + fp))
        recall = safe_div(tp, (tp + fn))
        f1_score = safe_div(2 * precision * recall, (precision + recall))
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
