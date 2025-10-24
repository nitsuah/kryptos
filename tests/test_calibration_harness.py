"""Tests for calibration harness sweeps."""

import os
import tempfile

from kryptos.k4.calibration import calibrate_positional_weight, calibrate_rarity_weight, write_calibration_artifact
from kryptos.k4.scoring import CRIBS

SAMPLE = [
    "BERLIN CLOCK EAST NORTHEAST",
    "CLOCK BERLIN EAST",
    "NORTHEAST EAST BERLIN",
    "RANDOM TEXT",
]


def test_rarity_weight_sweep_structure():
    rows = calibrate_rarity_weight(SAMPLE, CRIBS or ["BERLIN", "CLOCK", "EAST", "NORTHEAST"], k_values=[1.0, 2.0])
    assert len(rows) == 2
    assert all(hasattr(r, "spearman_vs_baseline") for r in rows)
    assert all(-1.0 <= r.spearman_vs_baseline <= 1.0 for r in rows)


def test_positional_weight_sweep_structure():
    rows = calibrate_positional_weight(SAMPLE, weights=[10.0, 30.0])
    assert len(rows) == 2
    assert all(-1.0 <= r.spearman_vs_baseline <= 1.0 for r in rows)


def test_write_calibration_artifact_creates_file():
    rarity_rows = calibrate_rarity_weight(SAMPLE, CRIBS or ["BERLIN", "CLOCK"], k_values=[1.0])
    positional_rows = calibrate_positional_weight(SAMPLE, weights=[10.0])
    tmp = tempfile.TemporaryDirectory()
    path = write_calibration_artifact(rarity_rows, positional_rows, output_dir=tmp.name)
    assert os.path.exists(path)
    tmp.cleanup()
