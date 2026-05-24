from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from kryptos.agents.ops import JobResult, OpsAgent, OpsConfig, ops_report
from kryptos.pipeline.attack_generator import AttackSpec
from kryptos.provenance.attack_log import AttackParameters, AttackResult


def _spec(cipher_type: str, params: dict, priority: float = 0.7, rationale: str = "r") -> AttackSpec:
    return AttackSpec(
        parameters=AttackParameters(cipher_type=cipher_type, key_or_params=params),
        priority=priority,
        source="test",
        rationale=rationale,
        tags=["t"],
    )


def test_ops_init_and_generation_guards(tmp_path: Path) -> None:
    agent_off = OpsAgent(config=OpsConfig(enable_attack_generation=False))
    assert agent_off.attack_logger is None
    assert agent_off.attack_generator is None

    with pytest.raises(RuntimeError, match="Attack generation not enabled"):
        agent_off.generate_attack_queue_from_q_hints("ABC")
    with pytest.raises(RuntimeError, match="Attack generation not enabled"):
        agent_off.generate_attack_queue_comprehensive("ABC")

    agent_on = OpsAgent(config=OpsConfig(enable_attack_generation=True, attack_log_dir=tmp_path / "logs"))
    assert agent_on.attack_logger is not None
    assert agent_on.attack_generator is not None


def test_execute_attack_queue_and_best_attack(tmp_path: Path) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=True, attack_log_dir=tmp_path / "logs"))

    specs = [
        _spec("vigenere", {"key": "AAAA"}, priority=0.1, rationale="low"),
        _spec("vigenere", {"key": "BBBB"}, priority=0.9, rationale="high"),
        _spec("vigenere", {"key": "CCCC"}, priority=0.3, rationale="mid"),
    ]

    scores = iter([0.1, 0.8, 0.5])

    def _fake_exec(_spec, _cipher):
        score = next(scores)
        return AttackResult(success=score >= 0.3, confidence_scores={"spy": score}, plaintext_candidate="TXT")

    agent._execute_single_attack = _fake_exec  # type: ignore[method-assign]
    summary = agent.execute_attack_queue(specs, "OBKRUOX", batch_size=2)

    assert summary["total_attacks"] == 3
    assert summary["executed"] == 3
    assert summary["successful"] == 2
    assert summary["best_score"] == 0.8
    assert summary["best_attack_rationale"] == "high"

    agent.attack_logger = None
    with pytest.raises(RuntimeError, match="Attack logging not enabled"):
        agent.execute_attack_queue(specs, "OBKRUOX")


def test_execute_single_attack_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=False))

    # Unknown cipher branch
    unknown = agent._execute_single_attack(_spec("unknown", {}), "ABC")
    assert unknown.success is False
    assert "Unknown cipher type" in (unknown.error_message or "")

    # Decryption returns None branch
    monkeypatch.setattr(agent, "_execute_vigenere", lambda *_args, **_kwargs: None)
    none_res = agent._execute_single_attack(_spec("vigenere", {"key": "X"}), "ABC")
    assert none_res.success is False
    assert "returned None" in (none_res.error_message or "")

    # Success branch via fake SpyAgent
    monkeypatch.setattr(agent, "_execute_vigenere", lambda *_args, **_kwargs: "PLAINTEXT")

    class _Spy:
        def analyze_candidate(self, _txt):
            return {"summary": {"overall_confidence": 0.9}, "insights": [1, 2]}

    monkeypatch.setattr("kryptos.agents.ops.SpyAgent", _Spy)
    good = agent._execute_single_attack(_spec("vigenere", {"key": "X"}), "ABC")
    assert good.success is True
    assert good.confidence_scores["spy"] == 0.9
    assert good.metadata["spy_insights_count"] == 2

    # Exception branch
    def _boom(*_args, **_kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(agent, "_execute_vigenere", _boom)
    bad = agent._execute_single_attack(_spec("vigenere", {"key": "X"}), "ABC")
    assert bad.success is False
    assert bad.metadata["error_type"] == "ValueError"


def test_cipher_specific_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=False))

    monkeypatch.setattr("kryptos.agents.ops.vigenere_decrypt", lambda _c, _k: "DEC")
    assert agent._execute_vigenere("ABC", {"key": "KEY"}) == "DEC"

    def _bad_vig(*_args, **_kwargs):
        raise RuntimeError("x")

    monkeypatch.setattr("kryptos.agents.ops.vigenere_decrypt", _bad_vig)
    assert agent._execute_vigenere("ABC", {"key": "KEY"}) is None

    monkeypatch.setattr("kryptos.agents.ops.recover_key_by_frequency", lambda *_args, **_kwargs: ["K"])
    monkeypatch.setattr("kryptos.agents.ops.vigenere_decrypt", lambda _c, _k: "REC")
    assert agent._execute_vigenere("ABC", {"key_length": 4}) == "REC"

    monkeypatch.setattr("kryptos.agents.ops.recover_key_by_frequency", lambda *_args, **_kwargs: [])
    assert agent._execute_vigenere("ABC", {"key_length": 4}) is None

    assert agent._execute_hill("ABC", {}) is None
    monkeypatch.setattr("kryptos.agents.ops.hill_decrypt", lambda _c, _m: "HILL")
    assert agent._execute_hill("ABC", {"key_matrix": [[1, 0], [0, 1]]}) == "HILL"
    monkeypatch.setattr("kryptos.agents.ops.hill_decrypt", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad")))
    assert agent._execute_hill("ABC", {"key_matrix": [[1]]}) is None

    monkeypatch.setattr("kryptos.agents.ops.apply_columnar_permutation", lambda _c, _n, _p: "TR")
    assert agent._execute_transposition("ABC", {"period": 3, "permutation": [0, 1, 2]}) == "TR"
    monkeypatch.setattr(
        "kryptos.agents.ops.apply_columnar_permutation",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad")),
    )
    assert agent._execute_transposition("ABC", {"period": 3, "permutation": [0, 1, 2]}) is None
    assert agent._execute_transposition("ABC", {"period": 3}) is None


def test_run_parallel_timeout_exception_and_success(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=False, job_timeout_seconds=1, max_workers=2))

    class _Future:
        def __init__(self, behavior):
            self.behavior = behavior

        def result(self, timeout=None):
            _ = timeout
            if self.behavior == "ok":
                return JobResult("ok", True, 0.1, candidates_count=1, best_score=1.0)
            if self.behavior == "timeout":
                from concurrent.futures import TimeoutError

                raise TimeoutError()
            raise RuntimeError("exec")

    class _Executor:
        def __init__(self, max_workers=None):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            _ = exc_type
            _ = exc
            _ = tb
            return False

        def submit(self, fn, name, cls, ciphertext, **params):
            _ = fn
            _ = cls
            _ = ciphertext
            _ = params
            return _Future(name)

    monkeypatch.setattr("kryptos.agents.ops.ProcessPoolExecutor", _Executor)
    monkeypatch.setattr("kryptos.agents.ops.as_completed", lambda futures, timeout=None: list(futures))

    jobs = [
        {"name": "ok", "class": object, "params": {}},
        {"name": "timeout", "class": object, "params": {}},
        {"name": "boom", "class": object, "params": {}},
    ]

    results = agent.run_parallel(jobs, ciphertext="ABC")
    assert len(results) == 3
    assert any(r.success for r in results)
    assert any((r.error or "").startswith("Job timeout") for r in results)
    assert any("Executor exception" in (r.error or "") for r in results)


def test_ops_report_includes_sections() -> None:
    report = ops_report(
        [
            JobResult("good", True, 1.2, candidates_count=3, best_score=0.5),
            JobResult("bad", False, 0.1, error="nope"),
        ],
    )
    assert "Successful Hypotheses" in report
    assert "Failed Hypotheses" in report
    assert "good" in report and "bad" in report


def test_generation_passthrough_and_additional_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=False))

    class _Gen:
        def generate_from_q_hints(self, ciphertext, max_attacks=50):
            _ = ciphertext
            _ = max_attacks
            return ["q"]

        def generate_comprehensive_queue(self, ciphertext, cipher_types=None, max_total=200):
            _ = ciphertext
            _ = cipher_types
            _ = max_total
            return ["c"]

    agent.attack_generator = _Gen()
    assert agent.generate_attack_queue_from_q_hints("ABC", max_attacks=3) == ["q"]
    assert agent.generate_attack_queue_comprehensive("ABC", cipher_types=["vigenere"], max_attacks=5) == ["c"]

    # Cover hill/transposition dispatch branches in _execute_single_attack.
    monkeypatch.setattr(agent, "_execute_hill", lambda *_args, **_kwargs: "HILLTXT")
    monkeypatch.setattr(agent, "_execute_transposition", lambda *_args, **_kwargs: "TRTXT")

    class _Spy:
        def analyze_candidate(self, _txt):
            return {"summary": {"overall_confidence": 0.4}, "insights": []}

    monkeypatch.setattr("kryptos.agents.ops.SpyAgent", _Spy)
    assert agent._execute_single_attack(_spec("hill", {"key_matrix": [[1]]}), "ABC").success is True
    assert agent._execute_single_attack(_spec("transposition", {"period": 3, "permutation": [0, 1, 2]}), "ABC").success is True


def test_vigenere_keylength_recovery_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    agent = OpsAgent(config=OpsConfig(enable_attack_generation=False))

    def _boom(*_args, **_kwargs):
        raise RuntimeError("bad recover")

    monkeypatch.setattr("kryptos.agents.ops.recover_key_by_frequency", _boom)
    assert agent._execute_vigenere("ABC", {"key_length": 5}) is None
