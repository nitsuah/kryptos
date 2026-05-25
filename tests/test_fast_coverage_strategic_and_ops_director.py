from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from kryptos.agents.ops_director import (
    AgentInsight,
    AttackProgress,
    OpsStrategicDirector,
    StrategicDecision,
    StrategyAction,
    demo_ops_director,
)
from kryptos.analysis.strategic_coverage import (
    CoverageTrend,
    StrategicCoverageAnalyzer,
    SaturationAnalysis,
    demo_strategic_coverage,
)
from kryptos.provenance.search_space import SearchSpaceTracker


def test_strategic_dataclasses_and_trend_paths(tmp_path: Path) -> None:
    trend = CoverageTrend(
        timestamp=datetime.now(),
        cipher_type="vigenere",
        region_key="length_5",
        coverage_percent=12.5,
        explored_count=100,
        successful_count=3,
    )
    sat = SaturationAnalysis(
        cipher_type="vigenere",
        region_key="length_5",
        is_saturated=False,
        coverage_percent=12.5,
        exploration_rate=0.0,
        estimated_completion_hours=None,
        recommendation="EXPLORE",
    )
    assert trend.to_dict()["cipher_type"] == "vigenere"
    assert sat.to_dict()["region_key"] == "length_5"

    tracker = SearchSpaceTracker(cache_dir=tmp_path / "tracker")
    analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path / "history")
    assert analyzer.analyze_saturation("unknown") == []


def test_strategic_analyzer_branches_and_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    tracker = SearchSpaceTracker(cache_dir=tmp_path / "tracker")
    analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path / "history")

    tracker.register_region("vigenere", "saturated", {}, 1000)
    tracker.record_exploration("vigenere", "saturated", count=950, successful=120)

    tracker.register_region("vigenere", "fast", {}, 1000)
    tracker.record_exploration("vigenere", "fast", count=700, successful=20)

    tracker.register_region("vigenere", "promising", {}, 1000)
    tracker.record_exploration("vigenere", "promising", count=300, successful=120)

    tracker.register_region("vigenere", "unexplored", {}, 1000)
    tracker.record_exploration("vigenere", "unexplored", count=5, successful=0)

    now = datetime.now()
    analyzer.coverage_history = [
        CoverageTrend(now - timedelta(hours=4), "vigenere", "fast", 50.0, 500, 8),
        CoverageTrend(now - timedelta(hours=2), "vigenere", "fast", 65.0, 650, 15),
        CoverageTrend(now, "vigenere", "fast", 70.0, 700, 20),
        CoverageTrend(now - timedelta(hours=1), "vigenere", "promising", 30.0, 300, 120),
    ]

    sats = analyzer.analyze_saturation("vigenere", saturation_threshold=80.0, min_samples=3)
    by_key = {s.region_key: s for s in sats}
    assert by_key["saturated"].is_saturated is True
    assert "PIVOT" in by_key["saturated"].recommendation
    assert by_key["fast"].estimated_completion_hours is not None
    assert "CONTINUE" in by_key["fast"].recommendation
    assert "INTENSIFY" in by_key["promising"].recommendation

    # Non-standard output format falls back to json payload.
    fallback = analyzer.generate_heatmap_visualization("vigenere", output_format="xml")
    assert isinstance(fallback, dict)

    html = analyzer.generate_heatmap_visualization("vigenere", output_format="html")
    assert "<html>" in html.lower()

    recs = analyzer.get_ops_recommendations(top_n=10, min_coverage=80.0)
    actions = {r["action"] for r in recs}
    assert "PIVOT_AWAY" in actions
    assert "INTENSIFY" in actions
    assert "EXPLORE" in actions

    trends_empty = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path / "h2")._analyze_trends()
    assert trends_empty == {"status": "insufficient_data"}

    report = analyzer.generate_coverage_report_for_ops()
    assert "vigenere" in report["overall_status"]

    # Cover load-history error branches.
    bad_history = tmp_path / "bad_history"
    bad_history.mkdir(parents=True, exist_ok=True)
    (bad_history / "coverage_history.json").write_text("not-json", encoding="utf-8")
    analyzer_bad = StrategicCoverageAnalyzer(tracker=tracker, history_dir=bad_history)
    assert analyzer_bad.coverage_history == []

    # Exercise demo path and its print rendering.
    demo_strategic_coverage()
    out = capsys.readouterr().out
    assert "STRATEGIC COVERAGE ANALYSIS DEMO" in out


class _DummyOpenAIClient:
    class ChatCompletion:
        @staticmethod
        def create(**_kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])


class _DummyAnthropicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.messages = self

    def create(self, **_kwargs):
        return SimpleNamespace(content=[SimpleNamespace(text="ok")])



def test_ops_director_branches_and_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    director = OpsStrategicDirector(llm_provider="local", model="rule-based", cache_dir=tmp_path / "ops")

    # Hit update branches including confidence history trimming.
    director.update_attack_progress("attack_a", attempts=10, best_score=0.2)
    director.active_attacks["attack_a"].confidence_trend = [0.1] * 110
    director.update_attack_progress("attack_a", attempts=12, best_score=0.3)
    assert len(director.active_attacks["attack_a"].confidence_trend) == 100

    # Insight trimming branch.
    director.recent_insights = [
        AgentInsight("A", datetime.now(), "pattern", "x", 0.5, False) for _ in range(1000)
    ]
    director.register_agent_insight(AgentInsight("SPY", datetime.now(), "pattern", "new", 0.8, True))
    assert len(director.recent_insights) == 1000

    synthesis = director.synthesize_agent_insights(
        [
            AgentInsight("SPY", datetime.now(), "linguistic", "ling1", 0.9, True),
            AgentInsight("LINGUIST", datetime.now(), "linguistic", "ling2", 0.7, True),
            AgentInsight("SPY_WEB", datetime.now(), "external_intel", "intel", 0.8, True, metadata={"cribs": ["BERLIN"]}),
        ],
    )
    assert synthesis["confidence"] > 0
    assert synthesis["key_findings"]

    director.decision_history.append(
        StrategicDecision(
            timestamp=datetime.now(),
            action=StrategyAction.CONTINUE,
            reasoning="steady",
            affected_attacks=["attack_a"],
            resource_changes={},
            success_criteria="keep improving",
            review_in_hours=2.0,
            confidence=0.7,
        ),
    )
    report = director.generate_daily_report()
    assert "STRATEGIC REPORT" in report
    assert "Active attacks" in report

    situation = director._gather_situation_report()
    assert director._needs_decision(situation) is False

    # actionable-insights trigger branch
    director.recent_insights = [
        AgentInsight("SPY", datetime.now(), "pattern", "i1", 0.8, True),
        AgentInsight("Q", datetime.now(), "pattern", "i2", 0.8, True),
        AgentInsight("LINGUIST", datetime.now(), "pattern", "i3", 0.8, True),
    ]
    assert director._needs_decision(director._gather_situation_report()) is True

    # _load_strategy_kb existing-file branch
    kb_path = director.cache_dir / "strategy_kb.json"
    kb_path.write_text(json.dumps({"successful_strategies": ["a"], "failed_strategies": [], "lessons_learned": []}), encoding="utf-8")
    assert director._load_strategy_kb()["successful_strategies"] == ["a"]

    # _call_llm branches for openai/anthropic and exception fallback.
    director.llm_provider = "openai"
    director.llm_client = _DummyOpenAIClient()
    assert director._call_llm("prompt") == "ok"

    director.llm_provider = "anthropic"
    director.llm_client = _DummyAnthropicClient("k")
    assert director._call_llm("prompt") == "ok"

    class _BadClient:
        class ChatCompletion:
            @staticmethod
            def create(**_kwargs):
                raise RuntimeError("boom")

    director.llm_provider = "openai"
    director.llm_client = _BadClient()
    assert director._call_llm("prompt") is None

    # Analyze with stale attack to force pivot rule and persistence save.
    director.llm_client = None
    director.active_attacks = {
        "stale": AttackProgress(
            attack_type="stale",
            attempts=100,
            best_score=0.1,
            time_elapsed_hours=9.0,
            cpu_allocation=0.5,
            improvement_rate=0.0,
            last_improvement=datetime.now() - timedelta(hours=9),
            confidence_trend=[0.1],
        ),
    }
    decision = director.analyze_situation(force_decision=True)
    assert decision is not None
    assert decision.action == StrategyAction.PIVOT
    assert (director.cache_dir / "decisions.jsonl").exists()

    # Cover demo function.
    demo_ops_director()
    out = capsys.readouterr().out
    assert "OPS v2.0 STRATEGIC DIRECTOR DEMO" in out
