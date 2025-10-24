"""Run a focused sweep over external crib weight to measure impact.

Writes `crib_weight_sweep.csv` and per-weight `<w>_details.csv` into a
timestamped artifacts folder under `artifacts/tuning_runs/`.
"""

import argparse
import csv
import logging
import sys
import time
from pathlib import Path

from kryptos.logging import setup_logging

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def load_cribs(path: Path) -> list[str]:
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


SAMPLES = [
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION",
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD",
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER",
]


def run():
    setup_logging(level=logging.INFO, logger_name="kryptos.tuning")
    log = logging.getLogger("kryptos.tuning")
    """Thin wrapper delegating to kryptos.k4.tuning.run_crib_weight_sweep.

    Retained temporarily while we migrate toward CLI subcommands.
    """
    parser = argparse.ArgumentParser(description='Run crib weight sweep (wrapper)')
    parser.add_argument('--weights', type=str, default=None, help='Comma-separated weights, e.g. 0.1,0.5,1.0')
    parser.add_argument('--dry-run', action='store_true', help='Accepted for backward compatibility; no effect')
    args = parser.parse_args()

    # import tuning API (fallback path mutation for editable install dev usage)
    try:
        from kryptos.k4 import scoring  # noqa: F401  (for crib loading util reuse, optional)
        from kryptos.k4.tuning import run_crib_weight_sweep  # type: ignore
    except ImportError:
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from kryptos.k4.tuning import run_crib_weight_sweep  # type: ignore

    cribs_path = ROOT / "docs" / "sources" / "sanborn_crib_candidates.txt"
    cribs = load_cribs(cribs_path)

    if args.weights:
        try:
            weights = [float(x.strip()) for x in args.weights.split(',') if x.strip()]
        except ValueError:
            log.warning("Invalid --weights value, falling back to defaults")
            weights = [0.1, 0.5, 1.0]
    else:
        weights = [0.1, 0.5, 1.0]

    rows = run_crib_weight_sweep(samples=SAMPLES, cribs=cribs, weights=weights)

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "artifacts" / "tuning_runs" / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)
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

    # per weight detail CSVs (reconstruct grouping)
    by_weight: dict[float, list] = {}
    for r in rows:
        by_weight.setdefault(r.weight, []).append(r)
    for w, group in by_weight.items():
        per = run_dir / f"weight_{str(w).replace('.','_')}_details.csv"
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

    log.info("Wrote crib weight sweep artifacts to: %s", run_dir)


if __name__ == "__main__":
    run()
