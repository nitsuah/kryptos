"""Tests for kryptos.benchmarks — attack-sweep benchmark harness."""

from __future__ import annotations

import csv
import json

import pytest

from kryptos.benchmarks import BENCHMARK_CASES, CSV_FIELDS, format_results_table, run_benchmarks


class TestRunBenchmarks:
    def test_single_fast_case(self, tmp_path):
        rows = run_benchmarks(names=["beaufort_sweep"], out_dir=tmp_path)
        assert len(rows) == 1
        row = rows[0]
        assert row["cipher"] == "K4"
        assert row["method"] == "beaufort_sweep"
        assert row["time_sec"] >= 0
        assert row["tested"] and row["tested"] > 0
        assert row["status"] == "null_result"

    def test_writes_json_and_csv(self, tmp_path):
        run_benchmarks(names=["beaufort_sweep"], out_dir=tmp_path)

        data = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
        assert data[0]["method"] == "beaufort_sweep"

        with open(tmp_path / "results.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == CSV_FIELDS
            csv_rows = list(reader)
        assert csv_rows[0]["method"] == "beaufort_sweep"

    def test_does_not_leave_null_artifacts(self, tmp_path):
        run_benchmarks(names=["beaufort_sweep"], out_dir=tmp_path)
        # Only the two results files should exist — sweep artifacts go to a temp dir
        assert {p.name for p in tmp_path.iterdir()} == {"results.json", "results.csv"}

    def test_unknown_case_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Unknown benchmark case"):
            run_benchmarks(names=["does_not_exist"], out_dir=tmp_path)

    def test_space_reduction_reported_for_clock_hill(self, tmp_path):
        rows = run_benchmarks(names=["clock_hill"], out_dir=tmp_path)
        # clock_hill filters by Hill invertibility, so a reduction fraction is reported
        assert rows[0]["space_reduction"] is not None
        assert 0.0 <= rows[0]["space_reduction"] <= 1.0


class TestFormatResultsTable:
    def test_renders_markdown(self):
        rows = [
            {
                "cipher": "K4",
                "method": "beaufort_sweep",
                "time_sec": 0.5,
                "tested": 20,
                "tested_per_sec": 40.0,
                "space_reduction": None,
                "status": "null_result",
                "timestamp": "2026-06-12T00:00:00Z",
            }
        ]
        table = format_results_table(rows)
        assert "| cipher | method |" in table
        assert "beaufort_sweep" in table
        assert "—" in table  # None space_reduction renders as em dash

    def test_space_reduction_percent(self):
        rows = [
            {
                "cipher": "K4",
                "method": "clock_hill_attack",
                "time_sec": 1.0,
                "tested": 100,
                "tested_per_sec": 100.0,
                "space_reduction": 0.85,
                "status": "null_result",
                "timestamp": "2026-06-12T00:00:00Z",
            }
        ]
        assert "85.00%" in format_results_table(rows)


def test_all_cases_have_unique_methods():
    methods = [c.method for c in BENCHMARK_CASES.values()]
    assert len(methods) == len(set(methods))
