"""Structural checks: each has a planted-solution positive control, then the K4 result."""

from __future__ import annotations

import numpy as np

from kryptos.k4 import crib_constraints as cc
from kryptos.k4 import structural_checks as sc
from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

S = cc.STANDARD
PLAIN_97 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGWHILEASMALLBIRDWATCHESFROMTHEOLDOAKTREENEARTHERIVERBANKTODAYXX"


def _plain_at(pt: str) -> dict[int, str]:
    return {i: pt[i] for i in cc.crib_letters()}


def _vig(pt: str, key: list[int]) -> str:
    return "".join(S[(S.index(c) + k) % 26] for c, k in zip(pt, key, strict=True))


def test_output_alphabet():
    res = sc.output_alphabet_eliminations()
    assert res["distinct_letters"] == 26
    assert {"playfair", "four_square", "adfgvx", "bifid_5x5"} <= set(res["eliminated"])
    assert sc.output_alphabet_eliminations("ABCDE" * 10)["eliminated"] == []


def test_null_gap_positive_control_and_k4():
    period, g = 7, 5
    key = [4, 15, 9, 22, 1, 18, 11]
    blocks = [i for i in range(97)]
    # key phase: positions after the first crib group (>= 63) are shifted by g nulls
    ks = [key[(i - g if i >= 63 else i) % period] for i in blocks]
    res = sc.null_gap_periodic(max_period=8, ciphertext=_vig(PLAIN_97, ks), plain=_plain_at(PLAIN_97))
    assert {"nulls": g, "period": period} in res["vigenere"]
    for hits in sc.null_gap_periodic().values():
        assert all(h["period"] >= 24 for h in hits)


def test_hill_positive_control_and_k4():
    kmat = np.array([[3, 3], [2, 5]])
    ct = []
    for b in range(0, 96, 2):
        v = np.array([S.index(PLAIN_97[b]), S.index(PLAIN_97[b + 1])])
        ct += [S[x] for x in (kmat @ v) % 26]
    ct = "".join(ct) + "X"
    res = sc.hill_consistency(sizes=[2], ciphertext=ct, plain=_plain_at(PLAIN_97))
    assert {"offset": 0, "direction": "encrypt", "blocks": 11} in res[2] or any(
        h["offset"] == 0 and h["direction"] == "encrypt" for h in res[2]
    )
    k4 = sc.hill_consistency(sizes=[2, 3])
    assert k4[2] == [] and k4[3] == []


def test_rotation_matches_repo_convention():
    from kryptos.k4.transposition_analysis import apply_rotation

    text = "ABCDEFGHIJKLMNOPQRSTUVWX"
    for rot in sc.ROTATIONS:
        toks = sc._rotate(list(range(24)), 6, rot)
        assert "".join(text[t] for t in toks) == apply_rotation(text, 6, rot)


def test_double_rotation_positive_control_and_k4():
    maps, labels = sc.double_rotation_mappings(97, max_pad=3)
    idx = next(
        i
        for i, lab in enumerate(labels)
        if lab == {"pad": 3, "nulls_at": "end", "width_a": 4, "rot_a": "90cw", "width_b": 25, "rot_b": "flip_h"}
    )
    pos = maps[idx]
    key = [6, 19, 2, 13, 24]
    sub = _vig(PLAIN_97, [key[i % 5] for i in range(97)])
    ct = [""] * 97
    for j, c in enumerate(sub):
        ct[pos[j]] = c
    res = sc.double_rotation_period_scan(
        periods=[5], max_pad=3, ciphertext="".join(ct), plain=_plain_at(PLAIN_97), max_examples=500
    )
    assert res["sub_then_trans"]["vigenere"][5]["survivors"] >= 1
    k4 = sc.double_rotation_period_scan(periods=range(1, 16), max_pad=3)
    for model in ("sub_then_trans", "trans_then_sub"):
        for fam in k4[model].values():
            assert all(v["survivors"] == 0 for v in fam.values())


def test_transposition_autokey_positive_control_and_k4():
    w, perm, lag, b = 5, [2, 0, 4, 1, 3], 9, 7
    s = []
    for j, p in enumerate(PLAIN_97):
        k = (S.index(s[j - lag]) + b) % 26 if j >= lag else 3
        s.append(S[(S.index(p) + k) % 26])
    ct = apply_columnar_permutation_encrypt("".join(s), w, perm)
    res = sc.transposition_autokey_scan(widths=[w], ciphertext=ct, plain=_plain_at(PLAIN_97), max_examples=100)
    assert {"perm": perm, "lag": lag, "offset": b} in res[w]["vigenere"]["examples"]
    k4 = sc.transposition_autokey_scan(widths=range(2, 6))
    assert all(v["survivors"] == 0 for r in k4.values() for f, v in r.items() if f != "permutations")


def test_chaocipher_round_trip_and_positive_control():
    left, right = cc.keyed_alphabet("HXUCZVAMDSLKPEFJRIGTWOBNYQ"), cc.keyed_alphabet("PTLNBQDEOYSFAVZKGJRIHWXUMC")
    assert sc._chaocipher_decrypt(sc._chaocipher_encrypt(PLAIN_97, left, right), left, right) == PLAIN_97
    ct = sc._chaocipher_encrypt(PLAIN_97, cc.keyed_alphabet("ZEBRA"), cc.keyed_alphabet("KRYPTOS"))
    res = sc.chaocipher_scan(["ZEBRA", "KRYPTOS"], ciphertext=ct, plain=_plain_at(PLAIN_97))
    assert {"left": "ZEBRA", "right": "KRYPTOS"} in res["exact"]
    assert sc.chaocipher_scan(["KRYPTOS", "PALIMPSEST", "ABSCISSA"])["exact"] == []


def test_chaocipher_published_example():
    # Byrne's worked example (Rubin 2010): WELLDONEISBETTERTHANWELLSAID -> OAHQHCNYNXTSZJRRHJBYHQKSOUJY
    left, right = "HXUCZVAMDSLKPEFJRIGTWOBNYQ", "PTLNBQDEOYSFAVZKGJRIHWXUMC"
    assert sc._chaocipher_encrypt("WELLDONEISBETTERTHANWELLSAID", left, right) == "OAHQHCNYNXTSZJRRHJBYHQKSOUJY"


def test_transposition_running_key_positive_control_and_k4():
    w, perm = 4, [3, 1, 0, 2]
    source = "ZZ" + PLAIN_97[::-1] + "QQQ"
    key = [S.index(c) for c in source[2 : 2 + 97]]
    ct = apply_columnar_permutation_encrypt(_vig(PLAIN_97, key), w, perm)
    res = sc.transposition_running_key_scan({"src": source}, widths=[w], ciphertext=ct, plain=_plain_at(PLAIN_97))
    assert res[w]["vigenere"]["best"]["sub_then_trans"] == 24
    from kryptos.k4.crib_constraints import sculpture_corpus

    k4 = sc.transposition_running_key_scan(sculpture_corpus(), widths=[2, 3])
    assert all(v["best"][m] < 16 for r in k4.values() for f, v in r.items() if f != "permutations" for m in v["best"])
