from __future__ import annotations

from dataclasses import dataclass

import pytest

from kryptos.agents.k123_analyzer import K123Analyzer
from kryptos.k4 import hypotheses as hyp
from kryptos.k4 import transposition_analysis as ta
from kryptos.k4 import vigenere_key_recovery as vkr


def test_k123_analyzer_patterns_and_report() -> None:
    analyzer = K123Analyzer()
    patterns = analyzer.analyze_all()
    assert patterns
    cats = {p.category for p in patterns}
    assert {"spelling", "theme", "structure", "artistic", "cipher"}.issubset(cats)

    report = analyzer.generate_report()
    assert "K1-K3 PATTERN ANALYSIS REPORT" in report
    assert "STRATEGIC RECOMMENDATIONS FOR K4" in report


def test_transposition_period_and_scoring_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    assert ta.calculate_ioc("") == 0.0
    assert ta.score_bigrams("A") == 0.0
    assert ta.score_trigrams("AB") == 0.0

    period_scores = ta.detect_transposition_period("A" * 25, max_period=6)
    assert period_scores

    repeated = ta.detect_period_by_repeated_sequences("ABCDABCDABCDABCD", min_length=3)
    assert isinstance(repeated, dict)

    monkeypatch.setattr(ta, "detect_transposition_period", lambda _ct, _mp=30: [(4, 0.8), (6, 0.6)])
    monkeypatch.setattr(ta, "detect_period_by_repeated_sequences", lambda _ct: {6: 20, 4: 10})
    combined = ta.detect_period_combined("SAMPLETEXT", max_period=10)
    assert combined[0][0] == 4
    assert {row[2] for row in combined} <= {"ioc", "kasiski"}


def test_columnar_encrypt_reverse_rotation_and_bruteforce(monkeypatch: pytest.MonkeyPatch) -> None:
    plaintext = "THEQUICKBROWN"
    period = 4
    perm = [2, 0, 3, 1]
    ct = ta.apply_columnar_permutation_encrypt(plaintext, period, perm)
    restored = ta.apply_columnar_permutation_reverse(ct, period, perm)
    assert restored == plaintext

    assert ta.apply_rotation("", 4, "identity") == ""
    assert ta.apply_rotation("ABCDEFG", 3, "90cw")
    assert ta.apply_rotation("ABCDEFG", 3, "90ccw")
    assert ta.apply_rotation("ABCDEFG", 3, "180")
    assert ta.apply_rotation("ABCDEFG", 3, "flip_h")
    assert ta.apply_rotation("ABCDEFG", 3, "flip_v")

    rots = ta.test_all_rotations("THECLOCKISBERLIN", 4, top_n=3)
    assert len(rots) == 3

    target_plain = "ABCDEFGH"
    target_perm = [1, 0, 3, 2]
    target_ct = ta.apply_columnar_permutation_encrypt(target_plain, 4, target_perm)

    def _score(text: str) -> float:
        return 100.0 if text == target_plain else 0.0

    monkeypatch.setattr(ta, "score_combined", _score)
    best_perm, best_score = ta.solve_columnar_permutation_exhaustive(target_ct, 4)
    assert best_perm == target_perm
    assert best_score == 100.0

    with pytest.raises(ValueError):
        ta.solve_columnar_permutation_exhaustive("ABCDEFG", 9)


def test_transposition_search_variants(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ta.random, "shuffle", lambda arr: None)
    monkeypatch.setattr(ta.random, "sample", lambda seq, _n: [0, 1])
    monkeypatch.setattr(ta, "score_bigrams", lambda _text: 1.0)

    perm, score = ta.solve_columnar_permutation("ABCDEFGH", period=4, max_iterations=5)
    assert sorted(perm) == [0, 1, 2, 3]
    assert isinstance(score, float)

    monkeypatch.setattr(
        ta,
        "solve_columnar_permutation_simulated_annealing",
        lambda _ct, _p, _mi, _it, _cr: ([0, 1, 2], 0.5),
    )
    mp_perm, mp_score = ta.solve_columnar_permutation_simulated_annealing_multi_start(
        "ABCDEFGH", period=3, num_restarts=3
    )  # noqa: E501
    assert mp_perm == [0, 1, 2]
    assert mp_score == 0.5

    monkeypatch.setattr(
        ta,
        "solve_columnar_permutation_multi_start",
        lambda _ct, p, num_restarts=5, max_iterations=2000: (list(range(p)), float(p)),
    )
    monkeypatch.setattr(ta, "apply_columnar_permutation_reverse", lambda _ct, p, _perm: f"TEXT{p}")
    brute = ta.detect_period_by_brute_force("ABCDEFGHIJKLMN", min_period=2, max_period=6, top_n=3)
    assert len(brute) == 3


def test_simulated_annealing_and_demo_helpers(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:  # noqa: E501
    monkeypatch.setattr(ta.random, "shuffle", lambda arr: None)
    monkeypatch.setattr(ta.random, "sample", lambda seq, _n: [0, 1])
    monkeypatch.setattr(ta.random, "random", lambda: 0.0)
    monkeypatch.setattr(ta, "score_combined", lambda _text: 0.1)

    perm, score = ta.solve_columnar_permutation_simulated_annealing(
        "ABCDEFGHIJKL",
        period=4,
        max_iterations=3,
        initial_temp=1.0,
        cooling_rate=0.5,
    )
    assert sorted(perm) == [0, 1, 2, 3]
    assert isinstance(score, float)

    monkeypatch.setattr(ta, "detect_transposition_period", lambda _ct, max_period=30: [(24, 0.9), (12, 0.6)])
    monkeypatch.setattr(ta, "detect_period_by_repeated_sequences", lambda _ct: {24: 5, 12: 3})
    monkeypatch.setattr(ta, "detect_period_combined", lambda _ct, max_period=30: [(24, 0.95, "ioc")])
    ta.test_period_detection()

    monkeypatch.setattr(
        ta, "solve_columnar_permutation", lambda _ct, _p, max_iterations=5000: ([3, 1, 4, 0, 6, 2, 5], 1.23)
    )  # noqa: E501
    monkeypatch.setattr(
        ta, "apply_columnar_permutation_reverse", lambda _ct, _p, _perm: "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    )  # noqa: E501
    ta.test_permutation_solver()

    out = capsys.readouterr().out
    assert "TRANSPOSITION PERIOD DETECTION TEST" in out
    assert "TRANSPOSITION PERMUTATION SOLVER TEST" in out


def test_vigenere_internal_helpers() -> None:
    assert vkr._score_english_frequency("") == 0.0
    assert isinstance(vkr._score_english_frequency("ABCDEF"), float)
    assert isinstance(vkr._score_english_frequency("ABCDEFGHIJKL"), float)

    combos = vkr._generate_key_combinations([["A", "B"], ["C", "D"]], max_keys=3)
    assert combos
    assert vkr._generate_key_combinations([], max_keys=3) == []

    ranked = vkr._rank_by_word_likelihood(["KRYPTOS", "ZZZZ", "CLOCK"])
    assert ranked[0] in {"KRYPTOS", "CLOCK"}


def test_recover_key_frequency_and_crib_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    assert vkr.recover_key_by_frequency("ABC", key_length=10) == []

    merged = vkr.recover_key_by_frequency(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ",
        key_length=3,
        top_n=3,
        try_all_alphabets=True,
    )
    assert isinstance(merged, list)
    assert len(merged) <= 3
    assert len(merged) == len(set(merged))


def test_recover_key_with_crib_and_completion(monkeypatch: pytest.MonkeyPatch) -> None:
    assert vkr.recover_key_with_crib("ABCDEF", "AB", key_length=3) == []

    original_complete = vkr._complete_partial_key
    monkeypatch.setattr(vkr, "_complete_partial_key", lambda _ct, _pk, _up: ["KRY"])
    cands = vkr.recover_key_with_crib("KRYPTOSKRYPTOS", "KRYP", key_length=3, position=0)
    assert cands

    monkeypatch.setattr(vkr, "_brute_force_complete", lambda _ct, _pk, _up: ["ABC"])
    assert original_complete("ABCDEF", ["", "", ""], [0, 1, 2]) == ["ABC"]


def test_bruteforce_complete_with_fake_spy(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeSpy:
        def analyze_candidate(self, _plaintext: str) -> dict:
            return {"pattern_score": 1.0}

    monkeypatch.setattr("kryptos.agents.spy.SpyAgent", _FakeSpy)
    monkeypatch.setattr("kryptos.ciphers.vigenere_decrypt", lambda _ct, key: key + "TEXT")

    out = vkr._brute_force_complete("ABCDEF", ["A", "", ""], [1, 2])
    assert out


def test_vigenere_key_recovery_demo_function(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vkr, "recover_key_by_frequency", lambda _ct, _kl, top_n=5: ["SECRET", "CLOCK"])
    monkeypatch.setattr("kryptos.ciphers.vigenere_decrypt", lambda _ct, _k: "PLAINTEXT")
    vkr.test_key_recovery()


@dataclass
class _FakeCand:
    id: str
    plaintext: str
    key_info: dict
    score: float


class _FakeStage:
    def __init__(self, cands: list[_FakeCand]) -> None:
        self._cands = cands

    def generate_candidates(self, _ciphertext: str, limit: int = 10):
        return self._cands[:limit]


def test_hypotheses_composite_and_stage_models(monkeypatch: pytest.MonkeyPatch) -> None:
    c1 = [_FakeCand("s1", "PLAINTEXT1", {"k": 1}, 2.0)]
    c2 = [_FakeCand("s2", "PLAINTEXT2", {"k": 2}, 3.0)]
    comp = hyp.CompositeHypothesis(_FakeStage(c1), _FakeStage(c2), stage1_candidates=5)
    out = comp.generate_candidates("ABC", limit=3)
    assert out and out[0].id.startswith("composite_")

    monkeypatch.setattr(hyp, "invertible_2x2_keys", lambda: [[[1, 0], [0, 1]]])
    monkeypatch.setattr(
        hyp, "score_decryptions", lambda _ct, _keys, limit=1: [{"key": [[1, 0], [0, 1]], "text": "HELLO", "score": 9.0}]
    )  # noqa: E501
    hill = hyp.HillCipher2x2Hypothesis().generate_candidates("ABC", limit=1)
    assert hill and hill[0].id.startswith("hill_2x2_")

    monkeypatch.setattr(
        hyp, "genetic_algorithm_hill3x3", lambda *_args, **_kwargs: [([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1.0, "TEXT")]
    )  # noqa: E501
    hill3 = hyp.HillCipher3x3GeneticHypothesis(population_size=2, generations=1).generate_candidates("ABC", limit=1)
    assert hill3 and hill3[0].key_info["method"] == "genetic_algorithm"


def test_hypotheses_cipher_families(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.combined_plaintext_score", lambda text: float(len(text)))

    monkeypatch.setattr(
        hyp,
        "search_columnar",
        lambda *_args, **_kwargs: [
            {"text": "AAA", "score": 1.0, "cols": 5, "perm": [0, 1]},
            {"text": "AAA", "score": 0.5, "cols": 5, "perm": [1, 0]},
            {"text": "BBB", "score": 2.0, "cols": 6, "perm": [0, 1]},
        ],
    )
    trans = hyp.BerlinClockTranspositionHypothesis(widths=[5, 6], max_perms=10).generate_candidates("ABC", limit=2)
    assert len(trans) == 2
    assert trans[0].plaintext == "BBB"

    vig = hyp.VigenereHypothesis(min_key_length=1, max_key_length=2, keys_per_length=2, explicit_keywords=["BERLIN"])
    vig_cands = vig.generate_candidates("LIPPSASVPH", limit=3)
    assert vig_cands

    auto = hyp.AutokeyHypothesis(primers=["KRYPTOS"])
    assert auto.generate_candidates("LIPPSASVPH", limit=1)

    playfair = hyp.PlayfairHypothesis(keywords=["KRYPTOS"])
    assert playfair.generate_candidates("GATLMZCLRQTX", limit=1)

    four = hyp.FourSquareHypothesis(keywords=["KRYPTOS", "BERLIN"])
    assert four.generate_candidates("GATLMZCLRQTX", limit=1)

    bifid = hyp.BifidHypothesis(keyword="KRYPTOS", periods=[5])
    assert bifid.generate_candidates("GATLMZCLRQTX", limit=1)

    monkeypatch.setattr("kryptos.k4.berlin_clock.full_berlin_clock_shifts", lambda _t: [1, 2, 3])
    bcv = hyp.BerlinClockVigenereHypothesis(hours=[0, 1])
    assert bcv.generate_candidates("ABCDEF", limit=2)
