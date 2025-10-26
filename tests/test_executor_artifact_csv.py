"""Tests that executor writes stage_top_candidates.csv with expected rows and header.

DEPRECATED: Testing deprecated PipelineExecutor class.
These tests are skipped pending migration to new Pipeline class or removal.
See: src/kryptos/k4/executor.py deprecation notice.
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from kryptos.k4.executor import PipelineConfig, PipelineExecutor  # noqa: E402
from kryptos.k4.pipeline import Stage, StageResult  # noqa: E402


def _make_stage(name: str, scores: list[float]) -> Stage:
    candidates = [{"text": f"{name}_cand_{i}", "score": sc, "source": name} for i, sc in enumerate(scores)]

    def _run(_: str) -> StageResult:
        best = max(candidates, key=lambda c: c["score"])
        return StageResult(name=name, output=best["text"], metadata={"candidates": candidates}, score=best["score"])

    return Stage(name=name, func=_run)


@unittest.skip("Testing deprecated PipelineExecutor - pending migration or removal")
class TestExecutorArtifactCSV(unittest.TestCase):
    def test_csv_export_rows(self):
        tmp = tempfile.TemporaryDirectory()
        artifact_root = os.path.join(tmp.name, "artifacts_test")
        ordering = [
            _make_stage("stage1", [100.0, 90.0, 80.0]),
            _make_stage("stage2", [75.0, 60.0, 50.0]),
        ]
        cfg = PipelineConfig(
            ordering=ordering,
            pruning_top_n=2,
            candidate_cap_per_stage=5,
            crib_bonus_threshold=9999.0,  # effectively ignore extras
            artifact_root=artifact_root,
            enable_attempt_log=False,
        )
        ex = PipelineExecutor(cfg)
        summary = ex.run("DUMMY")
        csv_name_obj = summary.get("artifact_csv")
        self.assertIsInstance(csv_name_obj, str)
        csv_name: str = csv_name_obj  # type: ignore[assignment]
        # Find single run_* directory under artifact root/executor_runs
        executor_runs_dir = os.path.join(artifact_root, "executor_runs")
        self.assertTrue(os.path.exists(executor_runs_dir), "executor_runs subdirectory not created")
        run_dirs = [d for d in os.listdir(executor_runs_dir) if d.startswith("run_")]
        self.assertTrue(run_dirs, "No run_* artifact directory created")
        run_dir0 = str(run_dirs[0])
        full_csv_path = os.path.join(executor_runs_dir, run_dir0, csv_name)
        self.assertTrue(os.path.exists(full_csv_path), f"CSV artifact missing at {full_csv_path}")
        with open(full_csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            rows = list(reader)
        header = rows[0]
        self.assertEqual(header, ["stage", "rank", "score", "crib_bonus", "text_prefix"])
        # Expect 2 pruned candidates per stage => 4 data rows + header
        self.assertEqual(len(rows) - 1, 4)
        tmp.cleanup()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
