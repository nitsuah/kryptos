"""Tests adaptive fusion weighting in composite pipeline (replacing executor dynamic gating)."""

from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import Stage, StageResult


def _make_stage(name: str, texts_and_scores):
    def _run(_: str) -> StageResult:
        cands = [{"text": txt, "score": sc, "source": name} for txt, sc in texts_and_scores]
        best = max(cands, key=lambda c: c["score"]) if cands else {"text": "EMPTY", "score": -999}
        return StageResult(name=name, output=best["text"], metadata={"candidates": cands}, score=best["score"])

    return Stage(name=name, func=_run)


def test_adaptive_fusion_adds_diagnostics():
    stages = [_make_stage("stageA", [("AAA", 10.0), ("BBBB", 20.0), ("CCC", 30.0)])]
    out = run_composite_pipeline("DUMMY", stages, report=False, adaptive=True)
    profile = out.get("profile", {})
    diag = profile.get("adaptive_diagnostics")
    assert diag and "stageA" in diag
    assert "median_wordlist_hit_rate" in diag["stageA"]
