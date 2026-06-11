from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from kryptos.agents.ops_director import AttackProgress, StrategicDecision, StrategyAction
from kryptos.autonomous_coordinator import AutonomousCoordinator, main


def _mk_coord(tmp_path):
    return AutonomousCoordinator(state_path=tmp_path / "state.json", ops_cycle_minutes=15, web_intel_check_hours=1)


def test_web_intelligence_success_and_failure_paths(tmp_path, monkeypatch):
    c = _mk_coord(tmp_path)

    monkeypatch.setattr(
        c.web_intel,
        "gather_intelligence",
        lambda: {"new_cribs": ["i1", "i2"], "updates": [], "timestamp": "2026-01-01T00:00:00"},
    )
    monkeypatch.setattr(c.web_intel, "get_top_cribs", lambda: ["BERLIN", "CLOCK"])
    c._check_web_intelligence()
    assert any(i.agent_name == "WEB_INTEL" for i in c.state.agent_insights)

    monkeypatch.setattr(c.web_intel, "gather_intelligence", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    c.state.web_intel_last_check = None
    c._check_web_intelligence()
    assert c.state.web_intel_last_check is not None


def test_ops_analysis_throttle_and_action_variants(tmp_path, monkeypatch):
    c = _mk_coord(tmp_path)

    # Throttle branch.
    c.state.last_ops_decision = datetime.now()
    called = {"n": 0}
    monkeypatch.setattr(c.ops_director, "analyze_situation", lambda: called.__setitem__("n", called["n"] + 1))
    c._run_ops_strategic_analysis()
    assert called["n"] == 0

    c.state.last_ops_decision = datetime.now() - timedelta(minutes=20)

    decision = StrategicDecision(
        timestamp=datetime.now(),
        action=StrategyAction.BOOST,
        reasoning="boost",
        affected_attacks=["a"],
        resource_changes={"a": 0.7},
        success_criteria="x",
        review_in_hours=1.0,
        confidence=0.8,
    )
    monkeypatch.setattr(c.ops_director, "update_attack_progress", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(c.ops_director, "analyze_situation", lambda: decision)
    c._run_ops_strategic_analysis()
    assert c.state.strategic_decisions

    # Remaining action branches in _execute_strategic_decision
    c._execute_strategic_decision(StrategyAction.STOP, {"reasoning": "s"})
    c._execute_strategic_decision(StrategyAction.START_NEW, {"reasoning": "s"})
    c._execute_strategic_decision(StrategyAction.EMERGENCY_STOP, {"reasoning": "s"})


def test_coordination_cycle_checkpoint_and_exchange_error(tmp_path, monkeypatch):
    c = _mk_coord(tmp_path)
    c.state.k123_patterns_loaded = True
    c.state.coordination_cycles = 9
    c.state.active_attacks = {
        "x": AttackProgress("x", 1, 0.1, 0.1, 0.5, 0.0, datetime.now(), []),
    }

    monkeypatch.setattr(c, "_check_web_intelligence", lambda: None)
    monkeypatch.setattr(c, "_run_ops_strategic_analysis", lambda: None)
    monkeypatch.setattr(
        "kryptos.autonomous_coordinator.run_exchange",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    calls = []
    monkeypatch.setattr(c, "create_checkpoint", lambda **kwargs: calls.append(kwargs))

    c._coordination_cycle()
    assert c.state.coordination_cycles == 10
    assert calls and calls[0]["attack_type"] == "x"


def test_run_loop_branches_and_main(tmp_path, monkeypatch):
    c = _mk_coord(tmp_path)

    # max_cycles break path
    c.state.coordination_cycles = 1
    monkeypatch.setattr(c, "_coordination_cycle", lambda: None)
    monkeypatch.setattr(c, "_generate_progress_report", lambda: "r")
    monkeypatch.setattr("kryptos.autonomous_coordinator.time.sleep", lambda *_args, **_kwargs: None)
    c.run_autonomous_loop(max_cycles=1, cycle_interval_minutes=0)

    # KeyboardInterrupt path
    c2 = _mk_coord(tmp_path)
    monkeypatch.setattr(c2, "_coordination_cycle", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
    c2.run_autonomous_loop(max_cycles=2, cycle_interval_minutes=0)

    # Generic exception path
    c3 = _mk_coord(tmp_path)
    monkeypatch.setattr(c3, "_coordination_cycle", lambda: (_ for _ in ()).throw(RuntimeError("fatal")))
    c3.run_autonomous_loop(max_cycles=2, cycle_interval_minutes=0)

    # main() path
    called = {"args": None, "loop": None}

    class _FakeCoordinator:
        def __init__(self, **kwargs):
            called["args"] = kwargs

        def run_autonomous_loop(self, **kwargs):
            called["loop"] = kwargs

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _FakeCoordinator)
    main()
    assert called["args"]["ops_cycle_minutes"] == 15
    assert called["loop"]["max_hours"] == 1.0


def test_state_key_error_paths_and_loop_reporting(tmp_path, monkeypatch):
    c = _mk_coord(tmp_path)

    # _save_state error path
    original_write_text = Path.write_text

    def _write_text(self, *args, **kwargs):
        if self == c.state_path:
            raise OSError("x")
        return original_write_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", _write_text)
    c._save_state()

    # _save_tested_keys + load_tested_keys paths
    c._save_tested_keys("v", ["A", "B"])
    assert c.load_tested_keys("v")
    assert c.load_tested_keys("missing") == set()

    bad_file = c.state_path.parent / "tested_keys" / "bad_tested_keys.json"
    bad_file.parent.mkdir(parents=True, exist_ok=True)
    bad_file.write_text("{bad", encoding="utf-8")
    assert c.load_tested_keys("bad") == set()

    # _load_k123_patterns early return branch
    c.state.k123_patterns_loaded = True
    c._load_k123_patterns()

    # run_autonomous_loop max_hours branch
    c.run_autonomous_loop(max_hours=0.0, cycle_interval_minutes=0)

    # report + sleep branch in loop
    c2 = _mk_coord(tmp_path)

    def _cycle_once():
        c2.state.coordination_cycles += 1

    monkeypatch.setattr(c2, "_coordination_cycle", _cycle_once)
    monkeypatch.setattr(c2, "_generate_progress_report", lambda: "report")
    monkeypatch.setattr("kryptos.autonomous_coordinator.get_logs_dir", lambda: tmp_path)
    monkeypatch.setattr("kryptos.autonomous_coordinator.time.sleep", lambda *_args, **_kwargs: None)
    c2.run_autonomous_loop(max_cycles=1, cycle_interval_minutes=0)
