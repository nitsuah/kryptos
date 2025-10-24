#!/usr/bin/env python3
"""Unified tuning CLI - parameter calibration for K4 cryptanalysis.

Usage:
    python scripts/tuning.py sweep --weights 0.1,0.5,1.0
    python scripts/tuning.py analyze [run_dir]
    python scripts/tuning.py calibrate --k-values 1.0,3.0,5.0
    python scripts/tuning.py quick

All tuning logic lives in kryptos.k4.tuning package.
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from pathlib import Path
from statistics import mean

from kryptos.k4.scoring import baseline_stats
from kryptos.k4.tuning import run_crib_weight_sweep
from kryptos.logging import setup_logging

ROOT = Path(__file__).resolve().parents[1]

# Sample plaintexts for testing
SAMPLES = [
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION",
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD",
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER",
]


# ============================================================================
# SWEEP: Crib weight sweep
# ============================================================================


def load_cribs(path: Path) -> list[str]:
    """Load cribs from sanborn_crib_candidates.txt."""
    cribs: list[str] = []
    if not path.exists():
        return cribs
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            tok = parts[0].strip().upper() if parts else ''
            if tok.isalpha() and len(tok) >= 3:
                cribs.append(tok)
    return cribs


def cmd_sweep(args, log: logging.Logger) -> int:
    """Run crib weight sweep."""
    cribs_path = ROOT / "docs" / "sources" / "sanborn_crib_candidates.txt"
    cribs = load_cribs(cribs_path)

    if args.weights:
        try:
            weights = [float(x.strip()) for x in args.weights.split(',') if x.strip()]
        except ValueError:
            log.warning("Invalid --weights value, using defaults")
            weights = [0.1, 0.5, 1.0]
    else:
        weights = [0.1, 0.5, 1.0]

    rows = run_crib_weight_sweep(samples=SAMPLES, cribs=cribs, weights=weights)

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "artifacts" / "tuning_runs" / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write summary CSV
    summary = run_dir / "crib_weight_sweep.csv"
    with summary.open("w", newline="", encoding="utf-8") as sf:
        writer = csv.writer(sf)
        writer.writerow(["weight", "sample", "baseline", "with_cribs", "delta"])
        for r in rows:
            writer.writerow(
                [
                    f"{r.weight}",
                    r.sample[:80],
                    f"{r.baseline:.6f}",
                    f"{r.with_cribs:.6f}",
                    f"{r.delta:.6f}",
                ],
            )

    # Write per-weight detail CSVs
    by_weight: dict[float, list] = {}
    for r in rows:
        by_weight.setdefault(r.weight, []).append(r)

    for w, group in by_weight.items():
        per = run_dir / f"weight_{str(w).replace('.', '_')}_details.csv"
        with per.open("w", newline="", encoding="utf-8") as pf:
            pw = csv.writer(pf)
            pw.writerow(["sample", "baseline", "with_cribs", "delta"])
            for g in group:
                pw.writerow(
                    [
                        g.sample[:100],
                        f"{g.baseline:.6f}",
                        f"{g.with_cribs:.6f}",
                        f"{g.delta:.6f}",
                    ],
                )

    log.info("Sweep artifacts: %s", run_dir)
    return 0


# ============================================================================
# ANALYZE: Pick best weight from sweep
# ============================================================================


def find_latest_run() -> Path:
    """Find most recent tuning run directory."""
    runs_dir = ROOT / 'artifacts' / 'tuning_runs'
    runs = sorted(runs_dir.glob('run_*'), reverse=True)
    if not runs:
        raise FileNotFoundError('No tuning_runs found')
    return runs[0]


def pick_best_weight(run_path: Path) -> tuple[float, dict[float, float]]:
    """Analyze sweep results and recommend best weight."""
    path = run_path / 'crib_weight_sweep.csv'
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")

    by_weight: dict[str, list[float]] = {}
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            weight_str = row.get('weight')
            delta_str = row.get('delta')
            if weight_str and delta_str:
                try:
                    by_weight.setdefault(weight_str, []).append(float(delta_str))
                except ValueError:
                    continue

    weight_stats = {float(ws): mean(deltas) for ws, deltas in by_weight.items() if deltas}
    if not weight_stats:
        raise RuntimeError('No usable data in sweep results')

    best_w = max(weight_stats.items(), key=lambda kv: kv[1])[0]
    return best_w, weight_stats


def cmd_analyze(args, log: logging.Logger) -> int:
    """Analyze sweep results and recommend best weight."""
    try:
        run_dir = Path(args.run_dir) if args.run_dir else find_latest_run()
    except FileNotFoundError as exc:
        log.error('Error locating run: %s', exc)
        return 2

    try:
        best, stats_map = pick_best_weight(run_dir)
    except (FileNotFoundError, RuntimeError) as exc:
        log.error('Error analyzing results: %s', exc)
        return 2

    log.info('Run: %s', run_dir)
    for weight_val, mean_delta in sorted(stats_map.items()):
        log.info('weight=%.3f mean_delta=%.6f', weight_val, mean_delta)
    log.info('Best weight: %.3f', best)
    return 0


# ============================================================================
# CALIBRATE: Rarity and positional deviation sweep
# ============================================================================


def cmd_calibrate(args, log: logging.Logger) -> int:
    """Run rarity calibration sweep."""
    try:
        from kryptos.k4.calibration import run_rarity_calibration
    except ImportError:
        log.error("Calibration module not implemented yet")
        return 1

    k_values = [1.0, 2.0, 5.0, 10.0]
    if args.k_values:
        try:
            k_values = [float(x.strip()) for x in args.k_values.split(',') if x.strip()]
        except ValueError:
            log.warning("Invalid --k-values, using defaults")

    pos_weights = [10.0, 20.0, 30.0, 40.0]
    if args.pos_weights:
        try:
            pos_weights = [float(x.strip()) for x in args.pos_weights.split(',') if x.strip()]
        except ValueError:
            log.warning("Invalid --pos-weights, using defaults")

    results = run_rarity_calibration(k_values=k_values, pos_weights=pos_weights)
    log.info("Calibration complete: %s", results)
    return 0


# ============================================================================
# QUICK: Fast deterministic parameter test
# ============================================================================


def cmd_quick(args, log: logging.Logger) -> int:
    """Quick deterministic parameter sweep for local experimentation."""
    param_grid = [
        {"chi_weight": 1.0, "ngram_weight": 1.0, "crib_bonus": 0.0},
        {"chi_weight": 1.5, "ngram_weight": 0.8, "crib_bonus": 0.0},
        {"chi_weight": 0.8, "ngram_weight": 1.2, "crib_bonus": 0.5},
    ]

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "artifacts" / "tuning_runs" / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as sf:
        writer = csv.writer(sf)
        writer.writerow(["run_id", "chi_weight", "ngram_weight", "crib_bonus", "top_sample", "top_score"])

        for i, params in enumerate(param_grid, start=1):
            scores = []
            for s in SAMPLES:
                stats = baseline_stats(s)
                ngram_sum = stats["bigram_score"] + stats["trigram_score"] + stats["quadgram_score"]
                score = (
                    params["ngram_weight"] * ngram_sum
                    - params["chi_weight"] * (0.05 * stats["chi_square"])
                    + params["crib_bonus"] * stats["crib_bonus"]
                )
                scores.append((s, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            top_sample, top_score = scores[0]

            run_id = f"r{i:03d}"
            writer.writerow(
                [
                    run_id,
                    params["chi_weight"],
                    params["ngram_weight"],
                    params["crib_bonus"],
                    top_sample[:60].replace(',', ' '),
                    f"{top_score:.4f}",
                ],
            )

            per_path = run_dir / f"{run_id}_top.csv"
            with per_path.open("w", newline="", encoding="utf-8") as pf:
                pw = csv.writer(pf)
                pw.writerow(["rank", "sample", "score"])
                for r, (samp, sc) in enumerate(scores, start=1):
                    pw.writerow([r, samp, f"{sc:.6f}"])

    log.info("Quick sweep artifacts: %s", run_dir)
    return 0


# ============================================================================
# CLI
# ============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Tuning CLI for K4 parameter calibration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', help='Tuning commands')

    # SWEEP
    sweep_parser = subparsers.add_parser('sweep', help='Run crib weight sweep')
    sweep_parser.add_argument('--weights', type=str, help='Comma-separated weights (e.g., 0.1,0.5,1.0)')

    # ANALYZE
    analyze_parser = subparsers.add_parser('analyze', help='Analyze sweep results')
    analyze_parser.add_argument('run_dir', nargs='?', help='Run directory (default: latest)')

    # CALIBRATE
    calibrate_parser = subparsers.add_parser('calibrate', help='Run rarity calibration')
    calibrate_parser.add_argument('--k-values', type=str, help='Comma-separated k values')
    calibrate_parser.add_argument('--pos-weights', type=str, help='Comma-separated positional weights')

    # QUICK
    subparsers.add_parser('quick', help='Quick deterministic parameter test')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(level=logging.INFO, logger_name="kryptos.tuning")
    log = logging.getLogger("kryptos.tuning")

    try:
        if args.command == 'sweep':
            return cmd_sweep(args, log)
        if args.command == 'analyze':
            return cmd_analyze(args, log)
        if args.command == 'calibrate':
            return cmd_calibrate(args, log)
        if args.command == 'quick':
            return cmd_quick(args, log)
    except Exception as e:
        log.error("Error: %s", e)
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
