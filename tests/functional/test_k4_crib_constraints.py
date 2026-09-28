"""Crib-constraint engine: every test has a positive control, so "no survivors" on K4 means something."""

from __future__ import annotations

import random

import numpy as np
import pytest

from kryptos.k4 import crib_constraints as cc
from kryptos.k4.physical_grid import K4
from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

S = cc.STANDARD
PLAIN_97 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGWHILEASMALLBIRDWATCHESFROMTHEOLDOAKTREENEARTHERIVERBANKTODAYXX"
assert len(PLAIN_97) == 97


def _vig(pt: str, key: list[int]) -> str:
    return "".join(S[(S.index(c) + k) % 26] for c, k in zip(pt, key, strict=True))


def _plain_at(pt: str) -> dict[int, str]:
    return {i: pt[i] for i in cc.crib_letters()}


class TestKeyedAlphabet:
    def test_kryptos(self):
        assert cc.keyed_alphabet("KRYPTOS") == "KRYPTOSABCDEFGHIJLMNQUVWXZ"


class TestAutokey:
    def test_ciphertext_autokey_positive_control(self):
        lag, b = 5, 3
        ct: list[str] = []
        for i, p in enumerate(PLAIN_97):
            k = (S.index(ct[i - lag]) + b) % 26 if i >= lag else 7
            ct.append(S[(S.index(p) + k) % 26])
        res = cc.ciphertext_autokey("".join(ct), _plain_at(PLAIN_97))
        assert {"lag": lag, "offset": b, "constraints": 24} in res["vigenere"]["survivors"]

    def test_k4_ciphertext_autokey_short_lags_eliminated(self):
        res = cc.ciphertext_autokey()
        for fam in res.values():
            assert all(s["lag"] >= 72 for s in fam["survivors"])

    def test_plaintext_autokey_positive_control(self):
        lag, b = 42, 11
        key = [(S.index(PLAIN_97[i - lag]) + b) % 26 if i >= lag else 0 for i in range(97)]
        res = cc.plaintext_autokey(_vig(PLAIN_97, key), _plain_at(PLAIN_97))
        assert any(s["lag"] == lag and s["offset"] == b for s in res["vigenere"]["survivors"])

    def test_k4_plaintext_autokey_no_constrained_survivor(self):
        for fam in cc.plaintext_autokey().values():
            assert fam["survivors"] == []


class TestArithmeticKeys:
    def test_linear_positive_control(self):
        key = [(7 * i + 4) % 26 for i in range(97)]
        assert {"a": 7, "b": 4} in cc.linear_key(_vig(PLAIN_97, key), _plain_at(PLAIN_97))["vigenere"]

    def test_k4_linear_eliminated(self):
        assert all(v == [] for v in cc.linear_key().values())

    def test_digit_positive_control(self):
        key = [random.Random(i).randrange(10) for i in range(97)]
        res = cc.digit_key(["KRYPTOS"], _vig(PLAIN_97, key), _plain_at(PLAIN_97))
        assert res["KRYPTOS:c_minus_p"]["viable"] is False  # standard-alphabet key, keyed-alphabet check
        res_std = cc.digit_key(["A"], _vig(PLAIN_97, key), _plain_at(PLAIN_97))  # "A" keyed == standard
        assert res_std["A:c_minus_p"]["viable"] is True

    def test_k4_digit_keys_eliminated(self):
        assert not any(v["viable"] for v in cc.digit_key(cc.DIGIT_KEYWORDS).values())


class TestRunningKey:
    def test_positive_control(self):
        source = "ZZZZZ" + PLAIN_97[::-1] + "ZZZZZ"
        key = [S.index(c) for c in source[5 : 5 + 97]]
        res = cc.running_key_scan({"src": source}, _vig(PLAIN_97, key), _plain_at(PLAIN_97))
        assert res["vigenere"]["src"]["exact"] and res["vigenere"]["src"]["start"] == 5

    def test_k4_sculpture_corpus_no_exact(self):
        res = cc.running_key_scan(cc.sculpture_corpus())
        assert not any(src["exact"] for fam in res.values() for src in fam.values())


class TestColumnarScan:
    def test_mapping_matches_repo_columnar(self):
        rng = random.Random(1)
        for w in (3, 5, 7, 8):
            perm = list(range(w))
            rng.shuffle(perm)
            ct = apply_columnar_permutation_encrypt(PLAIN_97, w, perm)
            start = cc._columnar_pt_to_ct(w, np.array([perm], dtype=np.int16), 97)[0]
            assert all(ct[start[j % w] + j // w] == PLAIN_97[j] for j in range(97))

    @pytest.mark.parametrize("model", ["sub_then_trans", "trans_then_sub"])
    def test_positive_control(self, model):
        w, perm, period = 6, [4, 1, 5, 0, 3, 2], 7
        key = [3, 17, 8, 22, 0, 11, 5]
        if model == "sub_then_trans":
            ct = apply_columnar_permutation_encrypt(_vig(PLAIN_97, [key[i % period] for i in range(97)]), w, perm)
        else:
            ct = _vig(apply_columnar_permutation_encrypt(PLAIN_97, w, perm), [key[i % period] for i in range(97)])
        res = cc.columnar_period_scan(widths=[w], periods=[period], ciphertext=ct, plain=_plain_at(PLAIN_97))
        hit = res[w][model]["vigenere"][period]
        assert hit["survivors"] >= 1 and perm in hit["examples"]

    def test_k4_small_widths_no_survivors_at_strong_periods(self):
        res = cc.columnar_period_scan(widths=range(2, 7), periods=range(1, 16))
        for w in res:
            for model in ("sub_then_trans", "trans_then_sub"):
                for fam in res[w][model].values():
                    assert all(v["survivors"] == 0 for v in fam.values())


class TestGeometryScan:
    def test_k4_geometry_no_survivors_at_strong_periods(self):
        res = cc.geometry_period_scan(periods=range(1, 16))
        assert res["mappings"] > 1000
        for model in ("sub_then_trans", "trans_then_sub"):
            for fam in res[model].values():
                assert all(v["survivors"] == 0 for v in fam.values())


def test_suite_writes_artifact(tmp_path):
    out = tmp_path / "a.json"
    summary = cc.run_crib_constraint_suite(widths=[2, 3], artifact_path=out)
    assert out.exists() and summary["status"] == "complete"
    assert set(summary) >= {"ciphertext_autokey", "running_key", "columnar_period", "geometry_period"}


def test_k4_constant():
    assert len(K4) == 97


class TestKeywordAlphabets:
    def test_positive_control_quagmire3(self):
        ka = cc.keyed_alphabet("ZEBRA")
        key = [5, 19, 2, 11, 23, 8, 14]
        ct = "".join(ka[(ka.index(c) + key[i % 7]) % 26] for i, c in enumerate(PLAIN_97))
        res = cc.keyword_alphabet_scan(
            ["ZEBRA", "KRYPTOS", "PALIMPSEST"], periods=[7], ciphertext=ct, plain=_plain_at(PLAIN_97)
        )
        assert res["quagmire3"][7]["examples"] == ["ZEBRA"]

    def test_k4_hand_picked_keywords_eliminated(self):
        res = cc.keyword_alphabet_scan(cc.DIGIT_KEYWORDS, periods=range(1, 23))
        for name in ("quagmire1", "quagmire2", "quagmire3"):
            assert all(v["survivors"] == 0 for v in res[name].values())

    def test_dictionary_words_nonempty(self):
        assert len(cc.dictionary_words()) >= 10


class TestProgressiveKey:
    def test_positive_control(self):
        base, p, d = [4, 9, 20, 1, 13], 5, 3
        key = [(base[i % p] + d * (i // p)) % 26 for i in range(97)]
        res = cc.progressive_key(_vig(PLAIN_97, key), _plain_at(PLAIN_97))
        assert {"period": p, "step": d} in res["vigenere"]

    def test_k4_short_periods_eliminated(self):
        for hits in cc.progressive_key(periods=range(1, 23)).values():
            assert hits == []


class TestMonoalphabetic:
    def test_positive_control_fixed_substitution_has_no_conflicts(self):
        ka = cc.keyed_alphabet("ZEBRA")
        ct = "".join(ka[S.index(c)] for c in PLAIN_97)
        assert cc.monoalphabetic_conflicts(ct, _plain_at(PLAIN_97)) == {}

    def test_k4_eight_conflicting_letters(self):
        assert len(cc.monoalphabetic_conflicts()) == 8


class TestGeometryPositiveControl:
    def test_planted_geometry_mapping_is_found(self):
        from kryptos.k4.geometry_combined_sweep import DEFAULT_ORDER_NAMES, composed_flat_indices

        order = DEFAULT_ORDER_NAMES[3]
        flat = composed_flat_indices(order, "flip_h", 5, "trailing")
        key = [2, 19, 7, 11, 24, 3, 16]
        pre = _vig(PLAIN_97, [key[i % 7] for i in range(97)])  # substitution first
        ct = "".join(pre[flat[i]] for i in range(97))  # apply_inverse(ct, flat) == pre
        res = cc.geometry_period_scan(periods=[7], ciphertext=ct, plain=_plain_at(PLAIN_97), max_examples=50)
        hit = res["sub_then_trans"]["vigenere"][7]
        assert {"order": order, "reflection": "flip_h", "offset": 5, "remainder": "trailing"} in hit["examples"]


def test_suite_records_dictionary_provenance(tmp_path):
    summary = cc.run_crib_constraint_suite(widths=[2], artifact_path=tmp_path / "a.json")
    assert summary["run_params"]["dictionary_source"]
    assert summary["run_params"]["dictionary_words"] > 0
