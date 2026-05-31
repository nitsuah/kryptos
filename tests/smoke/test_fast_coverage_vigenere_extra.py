from __future__ import annotations

from kryptos.k4 import vigenere_key_recovery as vkr


def test_get_spy_agent_singleton(monkeypatch) -> None:
    class _FakeSpy:
        pass

    vkr._spy_agent = None
    monkeypatch.setattr("kryptos.agents.spy.SpyAgent", _FakeSpy)

    a = vkr._get_spy_agent()
    b = vkr._get_spy_agent()
    assert isinstance(a, _FakeSpy)
    assert a is b


def test_recover_key_frequency_spy_scoring_and_tracker(monkeypatch) -> None:
    class _FakeSpy:
        def analyze_candidate(self, _plaintext: str) -> dict:
            return {"pattern_score": 2.0}

    class _FakeTracker:
        def __init__(self) -> None:
            self.recorded = []

        def already_tried(self, _cipher: str, key: str) -> bool:
            return key == "DROP"

        def record_exploration(self, **kwargs) -> None:
            self.recorded.append(kwargs)

    monkeypatch.setattr(vkr, "_generate_key_combinations", lambda _kc, max_keys=10: ["KEEP", "ERR", "DROP"])
    monkeypatch.setattr(vkr, "_rank_by_word_likelihood", lambda cands: cands)
    monkeypatch.setattr(vkr, "_get_spy_agent", lambda: _FakeSpy())

    def _fake_decrypt(_ct: str, key: str) -> str:
        if key == "ERR":
            raise ValueError("bad")
        return "PLAINTEXT"

    monkeypatch.setattr("kryptos.ciphers.vigenere_decrypt", _fake_decrypt)

    tracker = _FakeTracker()
    out = vkr.recover_key_by_frequency(
        ciphertext="ABABABAB",
        key_length=2,
        top_n=3,
        alphabet="AB",
        use_spy_scoring=True,
        skip_tried=True,
        tracker=tracker,
    )
    assert out == ["KEEP"]
    assert tracker.recorded and tracker.recorded[0]["cipher_type"] == "vigenere"


def test_recover_key_frequency_valueerror_in_column() -> None:
    out = vkr.recover_key_by_frequency(
        ciphertext="AZAZAZAZ",
        key_length=2,
        top_n=2,
        alphabet="ABC",
        use_spy_scoring=False,
    )
    assert isinstance(out, list)


def test_rank_empty_and_generate_indexerror_path() -> None:
    assert vkr._rank_by_word_likelihood([]) == []
    assert vkr._generate_key_combinations([[]], max_keys=2) == []


def test_recover_key_with_crib_invalid_and_partial(monkeypatch) -> None:
    monkeypatch.setattr(vkr, "KEYED_ALPHABET", "ABC")

    bad = vkr.recover_key_with_crib(ciphertext="DDDD", crib="AAA", key_length=2, position=0)
    assert bad == []

    monkeypatch.setattr(vkr, "_complete_partial_key", lambda _ct, _pk, _up: ["ABCA"])
    partial = vkr.recover_key_with_crib(ciphertext="ABCABC", crib="AAA", key_length=4, position=0)
    assert partial and partial[0][0] == "ABCA"


def test_complete_partial_key_branches(monkeypatch) -> None:
    assert vkr._complete_partial_key("ABC", ["A", "B"], []) == ["AB"]

    monkeypatch.setattr(vkr, "_brute_force_complete", lambda _ct, _pk, _up: ["ZZ"])
    assert vkr._complete_partial_key("ABC", ["", "", ""], [0, 1, 2]) == ["ZZ"]

    monkeypatch.setattr(vkr, "KEYED_ALPHABET", "AB")
    # Contains X in one column to trigger ValueError path during score generation.
    out = vkr._complete_partial_key("ABXABXABXABXABX", ["", "", "", "", ""], [0, 1, 2, 3])
    assert out and isinstance(out[0], str)


def test_bruteforce_complete_long_cipher_and_exceptions(monkeypatch) -> None:
    class _FakeSpy:
        def analyze_candidate(self, plaintext: str) -> dict:
            return {"pattern_score": float(len(plaintext))}

    monkeypatch.setattr(vkr, "KEYED_ALPHABET", "AB")
    monkeypatch.setattr("kryptos.agents.spy.SpyAgent", _FakeSpy)

    def _fake_decrypt(_ct: str, key: str) -> str:
        if key.endswith("B"):
            raise ValueError("bad")
        return "A" * 120

    monkeypatch.setattr("kryptos.ciphers.vigenere_decrypt", _fake_decrypt)

    out = vkr._brute_force_complete("A" * 120, ["A", "", ""], [1, 2])
    assert out


def test_vigenere_demo_exception_path(monkeypatch, capsys) -> None:
    monkeypatch.setattr(vkr, "recover_key_by_frequency", lambda _ct, _kl, top_n=5: ["BAD"])

    def _raise(_ct: str, _k: str) -> str:
        raise ValueError("boom")

    monkeypatch.setattr("kryptos.ciphers.vigenere_decrypt", _raise)

    vkr.test_key_recovery()
    out = capsys.readouterr().out
    assert "Failed -" in out
