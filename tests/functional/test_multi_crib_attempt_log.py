"""Test attempt log persistence for multi-crib transposition stage."""

import os

from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import make_transposition_multi_crib_stage

CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
POS = {"BERLIN": [64], "CLOCK": [69]}  # use list to match expected dict[str, Sequence[int]]


def test_multi_crib_attempt_log_created(tmp_path):
    stage = make_transposition_multi_crib_stage(positional_cribs=POS, min_cols=5, max_cols=6, limit=5)
    out = run_composite_pipeline(CIPHERTEXT, [stage], report=True, report_dir=str(tmp_path), limit=5)
    attempt_log = out.get("attempt_log")
    assert attempt_log and os.path.exists(attempt_log)
    # file should not be empty
    assert os.path.getsize(attempt_log) > 0
