"""Run a focused sweep over external crib weight to measure impact.

Writes `crib_weight_sweep.csv` and per-weight `<w>_details.csv` into a
timestamped artifacts folder under `artifacts/tuning_runs/`.
"""

import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


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
    parser = argparse.ArgumentParser(description='Run crib weight sweep')
    parser.add_argument('--weights', type=str, default=None, help='Comma-separated weights, e.g. 0.1,0.5,1.0')
    parser.add_argument('--dry-run', action='store_true', help='Dry run flag (no external side-effects)')
    args = parser.parse_args()

    from k4 import scoring

    cribs_path = ROOT / "docs" / "sources" / "sanborn_crib_candidates.txt"
    cribs = load_cribs(cribs_path)

    if args.weights:
        try:
            weights = [float(x.strip()) for x in args.weights.split(',') if x.strip()]
        except Exception:
            print("Invalid --weights value, falling back to defaults")
            weights = [0.1, 0.5, 1.0]
    else:
        weights = [0.1, 0.5, 1.0]

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "artifacts" / "tuning_runs" / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary = run_dir / "crib_weight_sweep.csv"
    with summary.open("w", newline="", encoding="utf-8") as sf:
        writer = csv.writer(sf)
        writer.writerow(["weight", "sample", "baseline", "with_cribs", "delta"])

        for w in weights:
            details = []
            for s in SAMPLES:
                base = scoring.combined_plaintext_score(s)
                withc = scoring.combined_plaintext_score_with_external_cribs(s, cribs, crib_weight=w)
                delta = withc - base
                details.append((s, base, withc, delta))
                writer.writerow([f"{w}", s[:80], f"{base:.6f}", f"{withc:.6f}", f"{delta:.6f}"])

            # write per-weight detail file
            per = run_dir / f"weight_{str(w).replace('.','_')}_details.csv"
            with per.open("w", newline="", encoding="utf-8") as pf:
                pw = csv.writer(pf)
                pw.writerow(["sample", "baseline", "with_cribs", "delta"])
                for s, base, withc, delta in details:
                    pw.writerow([s[:100], f"{base:.6f}", f"{withc:.6f}", f"{delta:.6f}"])

    print(f"Wrote crib weight sweep artifacts to: {run_dir}")


if __name__ == "__main__":
    run()
