"""Tiny deterministic tuning sweep.

Produces a small artifacts directory `artifacts/tuning_runs/<timestamp>/` with
`summary.csv` and per-run `<runid>_top.csv` files. Uses the scoring API in
`kryptos.k4.scoring` to score sample plaintexts under a small parameter grid.

Safe, fast, for local experimentation.
"""

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

ARTIFACTS = Path("artifacts") / "tuning_runs"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


SAMPLES = [
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION",
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD",
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER",
]


PARAM_GRID = [
    {"chi_weight": 1.0, "ngram_weight": 1.0, "crib_bonus": 0.0},
    {"chi_weight": 1.5, "ngram_weight": 0.8, "crib_bonus": 0.0},
    {"chi_weight": 0.8, "ngram_weight": 1.2, "crib_bonus": 0.5},
]


def run():
    # Prefer installed / editable package import; fall back to adding repo src/ to sys.path
    try:
        from kryptos.k4 import scoring  # type: ignore
    except ImportError:
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from kryptos.k4 import scoring  # type: ignore

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ARTIFACTS / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as sf:
        writer = csv.writer(sf)
        writer.writerow(["run_id", "chi_weight", "ngram_weight", "crib_bonus", "top_sample", "top_score"])

        for i, params in enumerate(PARAM_GRID, start=1):
            scores = []
            for s in SAMPLES:
                stats = scoring.baseline_stats(s)
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

    print(f"Wrote tuning artifacts to: {run_dir}")


if __name__ == "__main__":
    run()
