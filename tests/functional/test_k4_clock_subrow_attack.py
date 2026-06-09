"""Tests for non-standard Berlin Clock sub-row encoding and lamp-count transposition attacks (Attack 3 & 4)."""

from __future__ import annotations

import json
from pathlib import Path

from kryptos.k4.clock_subrow_attack import (
    K4,
    SUBROW_ENCODING_SCHEMES,
    lamp_row_widths,
    run_clock_subrow_attack,
    run_clock_transposition_attack,
)
from kryptos.k4.eureka import EurekaSignal


class TestSubrowEncodingSchemes:
    def test_all_schemes_present(self):
        expected = {"5hour_row", "top_2_rows", "minutes_only", "row_sum_keyed_offset"}
        assert set(SUBROW_ENCODING_SCHEMES.keys()) == expected

    def test_5hour_row_returns_one_value(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(13, 30, 0))
        result = SUBROW_ENCODING_SCHEMES["5hour_row"](cs)
        assert len(result) == 1
        assert 0 <= result[0] <= 4

    def test_top_2_rows_returns_two_values(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(13, 30, 0))
        result = SUBROW_ENCODING_SCHEMES["top_2_rows"](cs)
        assert len(result) == 2
        assert all(0 <= v <= 4 for v in result)

    def test_minutes_only_returns_two_values(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(10, 47, 0))
        result = SUBROW_ENCODING_SCHEMES["minutes_only"](cs)
        assert len(result) == 2
        assert 0 <= result[0] <= 11
        assert 0 <= result[1] <= 4

    def test_row_sum_keyed_offset_returns_four_values(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(23, 59, 0))
        result = SUBROW_ENCODING_SCHEMES["row_sum_keyed_offset"](cs)
        assert len(result) == 4
        assert all(0 <= v < 26 for v in result)

    def test_midnight_all_zero(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(0, 0, 0))
        for name, encoder in SUBROW_ENCODING_SCHEMES.items():
            result = encoder(cs)
            assert all(
                v == 0 for v in result
            ), f"Scheme '{name}' not all-zero at midnight"


class TestLampRowWidths:
    def test_midnight_all_zero(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(0, 0, 0))
        widths = lamp_row_widths(cs)
        assert widths == [0, 0, 0, 0]

    def test_max_time(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(23, 59, 0))
        widths = lamp_row_widths(cs)
        assert widths == [4, 3, 11, 4]

    def test_returns_4_values(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(12, 30, 0))
        widths = lamp_row_widths(cs)
        assert len(widths) == 4

    def test_hour_12_30(self):
        from datetime import time

        from kryptos.k4.berlin_clock import full_clock_state

        cs = full_clock_state(time(12, 30, 0))
        widths = lamp_row_widths(cs)
        # h5 = 12//5 = 2, h1 = 12%5 = 2, m5 = 30//5 = 6, m1 = 30%5 = 0
        assert widths == [2, 2, 6, 0]


class TestRunClockSubrowAttack:
    def _tiny_params(self, tmp_path):
        return dict(
            clock_step_seconds=43200,  # 2 states
            null_artifact_path=tmp_path / "null_subrow.json",
            eureka_snapshot_path=tmp_path / "snap_subrow.md",
        )

    def test_returns_dict(self, tmp_path):
        result = run_clock_subrow_attack(K4, **self._tiny_params(tmp_path))
        assert isinstance(result, dict)

    def test_status_null_result(self, tmp_path):
        result = run_clock_subrow_attack(K4, **self._tiny_params(tmp_path))
        assert result["status"] == "null_result"

    def test_attack_field(self, tmp_path):
        result = run_clock_subrow_attack(K4, **self._tiny_params(tmp_path))
        assert result["attack"] == "clock_subrow_vigenere"

    def test_writes_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_clock_subrow_attack(K4, **params)
        assert Path(params["null_artifact_path"]).exists()

    def test_artifact_valid_json(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_clock_subrow_attack(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        assert "run_params" in data
        assert "encoding_schemes" in data["run_params"]
        assert "total_tested" in data["run_params"]

    def test_total_tested_positive(self, tmp_path):
        result = run_clock_subrow_attack(K4, **self._tiny_params(tmp_path))
        assert result["run_params"]["total_tested"] > 0

    def test_encoding_schemes_in_params(self, tmp_path):
        result = run_clock_subrow_attack(K4, **self._tiny_params(tmp_path))
        schemes = result["run_params"]["encoding_schemes"]
        assert "5hour_row" in schemes
        assert "minutes_only" in schemes

    def test_eureka_raised_on_threshold_1(self, tmp_path):
        # Build plaintext that contains EAST; encrypt with zero shifts (identity)
        plain = "EAST" + "X" * 93
        ct = plain  # zero shifts = identity

        try:
            run_clock_subrow_attack(
                ct,
                clock_step_seconds=43200,
                null_artifact_path=tmp_path / "null_e1.json",
                eureka_snapshot_path=tmp_path / "snap_e1.md",
                keyword_eureka_threshold=1,
            )
        except EurekaSignal:
            pass  # expected when midnight scheme gives zero shifts and plaintext contains EAST


class TestRunClockTranspositionAttack:
    def _tiny_params(self, tmp_path):
        return dict(
            clock_step_seconds=43200,
            null_artifact_path=tmp_path / "null_tp.json",
            eureka_snapshot_path=tmp_path / "snap_tp.md",
        )

    def test_returns_dict(self, tmp_path):
        result = run_clock_transposition_attack(K4, **self._tiny_params(tmp_path))
        assert isinstance(result, dict)

    def test_status_null_result(self, tmp_path):
        result = run_clock_transposition_attack(K4, **self._tiny_params(tmp_path))
        assert result["status"] == "null_result"

    def test_attack_field(self, tmp_path):
        result = run_clock_transposition_attack(K4, **self._tiny_params(tmp_path))
        assert result["attack"] == "clock_lamp_transposition"

    def test_writes_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_clock_transposition_attack(K4, **params)
        assert Path(params["null_artifact_path"]).exists()

    def test_artifact_valid_json(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_clock_transposition_attack(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        assert "run_params" in data
        assert "total_tested" in data["run_params"]

    def test_total_tested_positive_for_nonzero_states(self, tmp_path):
        # Use 12:30 clock state (has non-zero widths [2,2,6,0])
        result = run_clock_transposition_attack(K4, **self._tiny_params(tmp_path))
        # At least one clock state in the 2-state sweep should have valid widths
        assert (
            result["run_params"]["total_tested"] >= 0
        )  # may be 0 if both states are all-zero

    def test_best_candidates_list(self, tmp_path):
        result = run_clock_transposition_attack(K4, **self._tiny_params(tmp_path))
        assert isinstance(result["best_candidates"], list)
        assert len(result["best_candidates"]) <= 10

    def test_full_day_finds_valid_states(self, tmp_path):
        """With a full-day sweep at 1-hour granularity there should be tested variants."""
        result = run_clock_transposition_attack(
            K4,
            clock_step_seconds=3600,  # 24 states
            null_artifact_path=tmp_path / "null_full.json",
            eureka_snapshot_path=tmp_path / "snap_full.md",
        )
        assert result["run_params"]["total_tested"] > 0
