"""Tests for the strategy_kb write path: persistence helper + director recording."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from kryptos import persistence
from kryptos.agents.ops_director import OpsStrategicDirector, StrategicDecision, StrategyAction

# --- persistence.persist_strategy ---------------------------------------------


def test_persist_strategy_rejects_bad_category() -> None:
    with pytest.raises(ValueError, match="category must be one of"):
        persistence.persist_strategy("bogus", "desc")


def test_persist_strategy_noop_without_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert persistence.persist_strategy("failed", "no db here") is None


class _FakeCursor:
    def __init__(self, sink: list[tuple]) -> None:
        self._sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql: str, params: tuple) -> None:
        self._sink.append((sql, params))

    def fetchone(self):
        return (42,)


class _FakeConn:
    def __init__(self, sink: list[tuple]) -> None:
        self._sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self):
        return _FakeCursor(self._sink)


def test_persist_strategy_writes_to_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://fake")
    sink: list[tuple] = []
    import kryptos.db as db

    monkeypatch.setattr(db, "get_conn", lambda: _FakeConn(sink))

    sid = persistence.persist_strategy(
        "successful",
        "vigenere period 14 promising",
        attack_type="vigenere",
        confidence=0.8,
        metadata={"k": "v"},
    )
    assert sid == 42
    assert len(sink) == 1
    sql, params = sink[0]
    assert "INSERT INTO strategy_kb" in sql
    assert params[0] == "successful"
    assert params[1] == "vigenere period 14 promising"
    assert params[2] == "vigenere"
    assert params[3] == 0.8
    assert json.loads(params[4]) == {"k": "v"}


# --- OpsStrategicDirector.record_strategy -------------------------------------


def _director(tmp_path: Path) -> OpsStrategicDirector:
    return OpsStrategicDirector(llm_provider="local", model="rule-based", cache_dir=tmp_path / "ops")


def test_record_strategy_rejects_bad_category(tmp_path: Path) -> None:
    director = _director(tmp_path)
    with pytest.raises(ValueError):
        director.record_strategy("invalid", "x")


def test_record_strategy_updates_memory_and_jsonl_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    director = _director(tmp_path)

    director.record_strategy("failed", "hill 3x3 stagnant", attack_type="hill_3x3", confidence=0.6, metadata={"a": 1})

    # In-memory KB reflects the entry immediately under the right list.
    failed = director.strategy_kb["failed_strategies"]
    assert failed[-1]["description"] == "hill 3x3 stagnant"
    assert failed[-1]["attack_type"] == "hill_3x3"

    # With no DB, it falls back to a JSONL file rather than losing the learning.
    kb_file = director.cache_dir / "strategy_kb_writes.jsonl"
    assert kb_file.exists()
    row = json.loads(kb_file.read_text().splitlines()[-1])
    assert row["category"] == "failed"
    assert row["description"] == "hill 3x3 stagnant"


def test_record_strategy_uses_db_and_skips_jsonl(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    director = _director(tmp_path)
    # DB write "succeeds" (returns an id) -> no JSONL fallback should be written.
    monkeypatch.setattr(persistence, "persist_strategy", lambda *a, **k: 7)

    director.record_strategy("successful", "promising", attack_type="vigenere", confidence=0.9)

    assert director.strategy_kb["successful_strategies"][-1]["description"] == "promising"
    assert not (director.cache_dir / "strategy_kb_writes.jsonl").exists()


# --- _record_strategy_from_decision mapping -----------------------------------


def _decision(action: StrategyAction) -> StrategicDecision:
    return StrategicDecision(
        timestamp=datetime.now(),
        action=action,
        reasoning=f"{action.value} reasoning",
        affected_attacks=["attack_x"],
        resource_changes={},
        success_criteria="criteria",
        review_in_hours=2.0,
        confidence=0.75,
    )


@pytest.mark.parametrize(
    "action,expected_list",
    [
        (StrategyAction.BOOST, "successful_strategies"),
        (StrategyAction.START_NEW, "lessons_learned"),
        (StrategyAction.PIVOT, "failed_strategies"),
        (StrategyAction.STOP, "failed_strategies"),
        (StrategyAction.EMERGENCY_STOP, "failed_strategies"),
    ],
)
def test_decision_maps_to_kb_category(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: StrategyAction, expected_list: str
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    director = _director(tmp_path)
    before = len(director.strategy_kb[expected_list])

    director._record_strategy_from_decision(_decision(action))

    entries = director.strategy_kb[expected_list]
    assert len(entries) == before + 1
    assert entries[-1]["attack_type"] == "attack_x"
    assert entries[-1]["metadata"]["action"] == action.value


@pytest.mark.parametrize("action", [StrategyAction.CONTINUE, StrategyAction.REDUCE])
def test_steady_state_decisions_record_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: StrategyAction
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    director = _director(tmp_path)
    sizes = {k: len(v) for k, v in director.strategy_kb.items()}

    director._record_strategy_from_decision(_decision(action))

    assert {k: len(v) for k, v in director.strategy_kb.items()} == sizes
    assert not (director.cache_dir / "strategy_kb_writes.jsonl").exists()
