from __future__ import annotations

import pytest

from kryptos.k4 import transposition_analysis as ta


def test_score_words_matching_paths(monkeypatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.WORDLIST", {"THE", "QUICK", "BROWN", "FOX"})
    assert ta.score_words("") == 0.0
    val = ta.score_words("THEQUICKBROWNFOX")
    assert 0.0 <= val <= 1.0
    assert val > 0.0


def test_multi_start_no_improvement_break(monkeypatch) -> None:
    monkeypatch.setattr(ta.random, "shuffle", lambda _x: None)
    monkeypatch.setattr(ta.random, "sample", lambda _rng, _k: [0, 1])
    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _t, _p, _perm: "ABCDEF")

    calls = {"n": 0}

    def _score(_text: str) -> float:
        calls["n"] += 1
        # First call seeds current_score high, then force non-improving steps.
        return 1.0 if calls["n"] == 1 else 0.0

    monkeypatch.setattr(ta, "score_combined", _score)

    perm, score = ta.solve_columnar_permutation_multi_start(
        ciphertext="ABCDEFGH",
        period=2,
        num_restarts=1,
        max_iterations=1001,
    )
    assert perm == [0, 1]
    assert isinstance(score, float)


def test_simulated_annealing_accept_and_temperature_break(monkeypatch) -> None:
    monkeypatch.setattr(ta.random, "shuffle", lambda _x: None)
    monkeypatch.setattr(ta.random, "sample", lambda _rng, _k: [0, 1])
    monkeypatch.setattr(ta.random, "random", lambda: 0.0)
    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _t, _p, perm: "".join(str(x) for x in perm))
    monkeypatch.setattr(ta, "score_combined", lambda text: {"01": 0.0, "10": 1.0}.get(text, 0.0))

    perm, score = ta.solve_columnar_permutation_simulated_annealing(
        ciphertext="ABCDEFGH",
        period=2,
        max_iterations=2,
        initial_temp=1.0,
        cooling_rate=1.0,
    )
    assert isinstance(perm, list)
    assert isinstance(score, float)

    # Trigger early break on low temperature branch.
    _perm2, _score2 = ta.solve_columnar_permutation_simulated_annealing(
        ciphertext="ABCDEFGH",
        period=2,
        max_iterations=50,
        initial_temp=0.02,
        cooling_rate=0.1,
    )


def test_exhaustive_break_and_period_limit(monkeypatch) -> None:
    with pytest.raises(ValueError):
        ta.solve_columnar_permutation_exhaustive("ABCDEFG", period=9)

    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _t, _p, _perm: "TXT")
    monkeypatch.setattr(ta, "score_combined", lambda _text: 100.0)
    perm, score = ta.solve_columnar_permutation_exhaustive("ABCDEFG", period=3, target_score=50.0)
    assert perm
    assert score >= 50.0


def test_hill_climb_reset_and_debug_branch(monkeypatch) -> None:
    monkeypatch.setattr(ta.random, "shuffle", lambda _x: None)
    monkeypatch.setattr(ta.random, "sample", lambda _rng, _k: [0, 1])
    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _t, _p, _perm: "ABCD")
    monkeypatch.setattr(ta, "score_bigrams", lambda _text: 0.0)

    seen = {"debug": 0}
    monkeypatch.setattr(ta.logger, "debug", lambda *_a, **_k: seen.__setitem__("debug", seen["debug"] + 1))

    perm, score = ta.solve_columnar_permutation("ABCDEFGH", period=2, max_iterations=1001)
    assert perm
    assert isinstance(score, float)
    assert seen["debug"] >= 1


def test_transposition_demo_else_and_partial_paths(monkeypatch, capsys) -> None:
    monkeypatch.setattr(ta, "detect_transposition_period", lambda _ct, max_period=30: [(12, 0.9)])
    monkeypatch.setattr(ta, "detect_period_by_repeated_sequences", lambda _ct: {12: 4})
    monkeypatch.setattr(ta, "detect_period_combined", lambda _ct, max_period=30: [(12, 0.8, "ioc")])

    ta.test_period_detection()
    out1 = capsys.readouterr().out
    assert "Period 24 detected" in out1

    monkeypatch.setattr(ta, "solve_columnar_permutation", lambda _ct, _period, max_iterations=5000: ([0, 1], 0.0))
    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _ct, _period, _perm: "NOTTHESAME")
    ta.test_permutation_solver()
    out2 = capsys.readouterr().out
    assert "PARTIAL" in out2
