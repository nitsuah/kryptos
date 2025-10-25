"""Tiny deterministic crib weight sweep example.

Runs a very small weight sweep using `kryptos.k4.tuning.run_crib_weight_sweep` and
writes artifacts under `artifacts/demo/tiny_weight_sweep_<timestamp>/`.

This replaces the legacy script `scripts/experimental/examples/run_ops_tiny_sweep.py`.
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path

from kryptos.k4.tuning import run_crib_weight_sweep
from kryptos.k4.tuning.crib_sweep import WeightSweepRow
from kryptos.log_setup import setup_logging
from kryptos.paths import get_artifacts_root

_DEFAULT_WEIGHTS = (0.1, 0.5)  # trimmed for speed


def run_tiny_weight_sweep(
    samples: Sequence[str] | None = None,
    cribs: Iterable[str] | None = None,
    weights: Sequence[float] | None = None,
) -> Path:
    """Execute a tiny weight sweep and persist summary + per-weight detail CSVs.

    Returns the output directory path.
    """
    setup_logging(level=logging.INFO, logger_name="kryptos.demo.tuning")
    log = logging.getLogger("kryptos.demo.tuning")
    rows: list[WeightSweepRow] = run_crib_weight_sweep(
        samples=samples,
        cribs=cribs,
        weights=weights or _DEFAULT_WEIGHTS,
    )
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = get_artifacts_root() / "demo" / f"tiny_weight_sweep_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = out_dir / "crib_weight_sweep.csv"
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
    # group and write detail per-weight
    by_weight: dict[float, list[WeightSweepRow]] = {}
    for r in rows:
        by_weight.setdefault(r.weight, []).append(r)
    for w, group in by_weight.items():
        detail = out_dir / f"weight_{str(w).replace('.', '_')}_details.csv"
        with detail.open("w", newline="", encoding="utf-8") as df:
            writer = csv.writer(df)
            writer.writerow(["sample", "baseline", "with_cribs", "delta"])
            for g in group:
                writer.writerow(
                    [
                        g.sample[:100],
                        f"{g.baseline:.6f}",
                        f"{g.with_cribs:.6f}",
                        f"{g.delta:.6f}",
                    ],
                )
    log.info("Tiny weight sweep complete. Artifacts: %s", out_dir)
    return out_dir


def _main() -> None:  # pragma: no cover
    import argparse

    p = argparse.ArgumentParser(description="Run tiny crib weight sweep example")
    p.add_argument("--weights", type=str, default=None, help="Comma-separated weight list")
    args = p.parse_args()
    weights: Sequence[float] | None
    if args.weights:
        try:
            weights = [float(x.strip()) for x in args.weights.split(',') if x.strip()]
        except ValueError:
            logging.getLogger("kryptos.demo.tuning").warning("Invalid --weights; using defaults")
            weights = None
    else:
        weights = None
    run_tiny_weight_sweep(weights=weights)


if __name__ == "__main__":  # pragma: no cover
    _main()
