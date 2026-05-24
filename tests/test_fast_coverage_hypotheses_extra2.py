from __future__ import annotations

from kryptos.k4 import hypotheses as hyp


def test_simple_substitution_full_generation(monkeypatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.combined_plaintext_score", lambda text: float(len(text)))
    h = hyp.SimpleSubstitutionHypothesis()
    out = h.generate_candidates("Abc-DeF", limit=40)
    ids = {c.id for c in out}
    assert len(out) == 28
    assert "atbash" in ids
    assert "reverse" in ids
    assert "caesar_rot0" in ids


def test_vigenere_find_keys_and_generate(monkeypatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.combined_plaintext_score", lambda text: float(sum(ord(c) for c in text[:5])))
    h = hyp.VigenereHypothesis(min_key_length=2, max_key_length=2, keys_per_length=6, explicit_keywords=["berlin"])

    keys = h._find_best_keys_for_length("THISISALONGERTESTCIPHERTEXT", key_length=6)
    assert keys
    assert len(keys) <= 6

    cands = h.generate_candidates("THISISALONGERTESTCIPHERTEXT", limit=10)
    assert cands
    assert any(c.key_info.get("explicit") is True for c in cands)


def test_autokey_and_playfair_edge_branches(monkeypatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.combined_plaintext_score", lambda text: float(len(text)))

    a = hyp.AutokeyHypothesis(primers=[""])
    # Empty primer forces fallback key_char='A' path on first iteration.
    assert a._autokey_decrypt("ABC", "")
    assert a.generate_candidates("ABC", limit=1)

    p = hyp.PlayfairHypothesis(keywords=["KRYPTOS"])
    grid = p._build_playfair_grid("KRYPTOS")
    assert p._find_in_grid(grid, "J") == (0, 0)

    # Odd length branch appends X.
    dec = p._playfair_decrypt("A", "KRYPTOS")
    assert len(dec) == 2

    # Force same-row branch.
    monkeypatch.setattr(p, "_find_in_grid", lambda _grid, ch: (0, 1) if ch == "A" else (0, 2))
    assert p._playfair_decrypt("AB", "KRYPTOS")

    # Force same-column branch.
    monkeypatch.setattr(p, "_find_in_grid", lambda _grid, ch: (1, 0) if ch == "A" else (2, 0))
    assert p._playfair_decrypt("AB", "KRYPTOS")


def test_foursquare_and_bifid_find_fallbacks(monkeypatch) -> None:
    monkeypatch.setattr("kryptos.k4.scoring.combined_plaintext_score", lambda text: float(len(text)))

    fs = hyp.FourSquareHypothesis(keywords=["KRYPTOS", "BERLIN"])
    grid = fs._plain_grid()
    assert fs._find(grid, "J") == (0, 0)
    # Odd-length branch in FourSquare _decrypt.
    assert fs._decrypt("A", "KRYPTOS", "BERLIN")
    assert fs.generate_candidates("ABCD", limit=2)

    bf = hyp.BifidHypothesis(keyword="KRYPTOS", periods=[5])
    bgrid = bf._build_grid("KRYPTOS")
    assert bf._find(bgrid, "J") == (0, 0)
    assert bf.generate_candidates("ABCD", limit=1)


def test_composite_initializers_and_hill_limit_wrappers(monkeypatch) -> None:
    limits: list[int] = []

    def _fake_hill_generate(self, ciphertext: str, limit: int = 10):
        limits.append(limit)
        return []

    monkeypatch.setattr(hyp.HillCipher2x2Hypothesis, "generate_candidates", _fake_hill_generate)

    th = hyp.TranspositionThenHillHypothesis(hill_limit=123)
    th.stage2.generate_candidates("ABC", limit=1)

    vh = hyp.VigenereThenHillHypothesis(hill_limit=321)
    vh.stage2.generate_candidates("ABC", limit=1)

    assert 123 in limits
    assert 321 in limits

    vt = hyp.VigenereThenTranspositionHypothesis(vigenere_candidates=4, transposition_limit=7, vigenere_max_key_length=3)
    assert isinstance(vt.stage1, hyp.VigenereHypothesis)

    st = hyp.SubstitutionThenTranspositionHypothesis(transposition_limit=6)
    ht = hyp.HillThenTranspositionHypothesis(hill_candidates=5, transposition_limit=8)
    at = hyp.AutokeyThenTranspositionHypothesis(autokey_candidates=5, transposition_limit=8)
    pt = hyp.PlayfairThenTranspositionHypothesis(playfair_candidates=5, transposition_limit=8)
    dt = hyp.DoubleTranspositionHypothesis(stage1_candidates=4, stage2_limit=9)

    assert st.stage1_candidates == 28
    assert ht.stage1_candidates == 5
    assert at.stage1_candidates == 5
    assert pt.stage1_candidates == 5
    assert dt.stage1_candidates == 4
