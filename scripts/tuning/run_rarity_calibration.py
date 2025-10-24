"""CLI script to run rarity and positional weight calibration sweeps and write JSON artifact."""

from __future__ import annotations

import argparse

from kryptos.k4.calibration import (
    calibrate_positional_weight,
    calibrate_rarity_weight,
    write_calibration_artifact,
)
from kryptos.k4.scoring import CRIBS

DEFAULT_CANDIDATES = [
    "BERLIN CLOCK EAST NORTHEAST",  # includes multiple cribs for alignment frequency
    "CLOCK BERLIN EAST",
    "NORTHEAST EAST BERLIN",
    "RANDOM PLAINTEXT STRING FOR TESTING",
    "NO CRIBS HERE JUST FILLER",
    "EASTWARD MOVEMENT BERLIN CLOCK",
    "CLOCKWISE TURN BERLIN",
    "SUBTLE SHADING ABSENCE OF LIGHT",
    "BETWEEN SUBTLE SHADING AND ABSENCE OF LIGHT LIES NUANCE OF ILLUSION",
    "TOTALLY INVISIBLE THEY USED EARTHS MAGNETIC FIELD",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run K4 calibration sweeps for rarity and positional weights")
    parser.add_argument("--output-dir", dest="output_dir", help="Directory for calibration JSON", default=None)
    parser.add_argument(
        "--k-values",
        nargs="*",
        type=float,
        default=[1.0, 2.0, 5.0, 10.0],
        help="Rarity k sweep values",
    )
    parser.add_argument(
        "--pos-weights",
        nargs="*",
        type=float,
        default=[10.0, 20.0, 30.0, 40.0],
        help="Positional deviation weight sweep",
    )
    args = parser.parse_args()
    cribs = CRIBS or ["BERLIN", "CLOCK", "EAST", "NORTHEAST"]
    rarity_rows = calibrate_rarity_weight(DEFAULT_CANDIDATES, cribs, k_values=args.k_values)
    positional_rows = calibrate_positional_weight(DEFAULT_CANDIDATES, weights=args.pos_weights)
    path = write_calibration_artifact(rarity_rows, positional_rows, output_dir=args.output_dir or None)
    print(f"Calibration results written to {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
