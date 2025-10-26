"""Tests for dynamic adaptive gating adjustments in PipelineExecutor.

DEPRECATED: Testing deprecated PipelineExecutor class.
These tests are skipped pending migration to new Pipeline class or removal.
See: src/kryptos/k4/executor.py deprecation notice.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from kryptos.k4.executor import PipelineConfig, PipelineExecutor  # noqa: E402
from kryptos.k4.pipeline import Stage, StageResult  # noqa: E402


def _make_stage(name: str, scores: list[float]) -> Stage:
    candidates = [{"text": f"{name}_{i}", "score": sc} for i, sc in enumerate(scores)]

    def _run(_: str) -> StageResult:
        best = max(candidates, key=lambda c: c["score"]) if candidates else {"text": "EMPTY", "score": -999}
        return StageResult(name=name, output=best["text"], metadata={"candidates": candidates}, score=best["score"])

    return Stage(name=name, func=_run)


@unittest.skip("Testing deprecated PipelineExecutor - pending migration or removal")
class TestExecutorDynamicGating(unittest.TestCase):
    def test_dynamic_adjust_increases_threshold(self):
        ordering = [_make_stage("stageA", [10.0, 20.0, 30.0])]
        cfg = PipelineConfig(ordering=ordering, adaptive_thresholds={"stageA": 5.0})
        ex = PipelineExecutor(cfg)
        summary = ex.run("DUMMY")
        stage_info = summary["stages"][0]
        self.assertTrue(stage_info["adaptive_gate_pass"])  # score >= threshold
        # Dynamic adjustment should be positive (mean above base threshold)
        self.assertGreater(stage_info["dynamic_threshold_adjust"], 0.0)
        final_dyn = summary["dynamic_thresholds_final"].get("stageA")
        self.assertGreater(final_dyn, 0.0)

    def test_dynamic_adjust_decreases_on_empty(self):
        ordering = [_make_stage("stageB", [])]
        cfg = PipelineConfig(ordering=ordering, adaptive_thresholds={"stageB": 50.0})
        ex = PipelineExecutor(cfg)
        summary = ex.run("DUMMY")
        stage_info = summary["stages"][0]
        # No candidates => gate pass depends on score but dynamic adjust should be negative
        self.assertLess(stage_info["dynamic_threshold_adjust"], 0.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
