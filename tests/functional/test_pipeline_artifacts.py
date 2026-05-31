"""Tests for composite pipeline artifact generation (JSON & CSV) replacing executor artifact CSV test."""

import os
import tempfile

from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import Stage, StageResult


def _make_stage(name: str, scores: list[float]) -> Stage:
    candidates = [{"text": f"{name}_cand_{i}", "score": sc, "source": name} for i, sc in enumerate(scores)]

    def _run(_: str) -> StageResult:
        best = max(candidates, key=lambda c: c["score"])
        return StageResult(name=name, output=best["text"], metadata={"candidates": candidates}, score=best["score"])

    return Stage(name=name, func=_run)


def test_composite_artifact_files():
    tmp = tempfile.TemporaryDirectory()
    ordering = [
        _make_stage("stage1", [100.0, 90.0, 80.0]),
        _make_stage("stage2", [75.0, 60.0, 50.0]),
    ]
    out = run_composite_pipeline("DUMMY", ordering, report=True, report_dir=tmp.name, limit=10)
    paths = out.get("artifacts")
    assert isinstance(paths, dict)
    json_path = paths.get("json")
    csv_path = paths.get("csv")
    assert json_path and os.path.exists(json_path)
    assert csv_path and os.path.exists(csv_path)
    tmp.cleanup()
