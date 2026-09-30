"""Frontier checks: each has a positive control (a planted solution it must find), then runs on K4."""

from __future__ import annotations

import random

import numpy as np
import pytest

from kryptos.k4 import frontier_checks as fc
from kryptos.k4.crib_constraints import STANDARD as S
from kryptos.k4.crib_constraints import crib_letters
from kryptos.k4.crib_constraints import keyed_alphabet as cc_keyed
from kryptos.k4.english_model import english_z, reference_english
from kryptos.k4.physical_grid import K4

# 97 letters of English with EAST/NORTHEAST/BERLIN/CLOCK at K4's crib positions.
PLAIN = fc.reconstruction_plain()
PLAIN_TEXT = "".join(PLAIN[i] for i in range(97))


def _cribs_of(text: str) -> dict[int, str]:
    return {i: text[i] for i in crib_letters()}


def _vig(pt: str, key: list[int]) -> str:
    return "".join(S[(S.index(c) + k) % 26] for c, k in zip(pt, key, strict=True))


class TestEnglishModel:
    def test_separates_english_from_random(self):
        rng = random.Random(1)
        noise = "".join(rng.choice(S) for _ in range(60))
        assert english_z("THEREWASNOTHINGSOVERYREMARKABLEINTHATNORDIDALICETHINKITSOVERY") > 0.6
        assert english_z(noise) < 0.3


class TestRunningKeyEnglish:
    def test_planted_english_running_key_is_plausible(self):
        eng = reference_english()
        key = [S.index(c) for c in eng[500:597]]
        ct = _vig(PLAIN_TEXT, key)
        res = fc.running_key_english(ciphertext=ct, plain=_cribs_of(PLAIN_TEXT), samples=500)
        assert res["families"]["vigenere"]["p_english"] > 0.05

    def test_k4_key_fragments_are_not_english(self):
        res = fc.running_key_english(samples=500)
        assert all(v["p_english"] < 0.01 for v in res["families"].values())


class TestTranspositionRunningKeyEnglish:
    def test_planted_columnar_plus_english_key_beats_controls(self):
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

        eng = reference_english()
        key = [S.index(c) for c in eng[700:797]]
        ct = apply_columnar_permutation_encrypt(_vig(PLAIN_TEXT, key), 5, [3, 0, 4, 1, 2])
        res = fc.transposition_running_key_english(widths=[5], ciphertext=ct, plain=_cribs_of(PLAIN_TEXT), controls=3)
        row = res[5]["sub_then_trans"]["vigenere"]
        assert row["k4_best"] > max(row["control_best"]) + 0.3


class TestRecurrenceKey:
    def test_planted_recurrence_key_is_found(self):
        coeffs, d, key = [3, 7, 11], 5, [4, 19, 8]
        while len(key) < 97:
            key.append((sum(c * key[-1 - j] for j, c in enumerate(coeffs)) + d) % 26)
        ct = _vig(PLAIN_TEXT, key)
        res = fc.recurrence_key(max_order=5, ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert any(h["order"] == 3 for h in res["vigenere"])

    def test_k4_has_no_recurrence_key_up_to_order_7(self):
        assert fc.recurrence_testable_orders() == [1, 2, 3, 4, 5, 6, 7]
        assert all(v == [] for v in fc.recurrence_key(7).values())


class TestGeneralAlphabet:
    def test_planted_mixed_alphabet_is_found(self):
        rng = random.Random(3)
        sigma = rng.sample(range(26), 26)
        key = [rng.randrange(26) for _ in range(7)]
        ct = "".join(S[(sigma[S.index(c)] + key[i % 7]) % 26] for i, c in enumerate(PLAIN_TEXT))
        res = fc.general_alphabet_periodic(max_period=10, ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert 7 in res["mixed_plain_alphabet"]

    def test_planted_mixed_cipher_alphabet_is_found(self):
        rng = random.Random(4)
        tau = rng.sample(range(26), 26)
        key = [rng.randrange(26) for _ in range(6)]
        ct = "".join(S[tau[(S.index(c) + key[i % 6]) % 26]] for i, c in enumerate(PLAIN_TEXT))
        res = fc.general_alphabet_periodic(max_period=10, ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert 6 in res["mixed_cipher_alphabet_add"]

    def test_k4_eliminated_where_the_check_has_teeth(self):
        res = fc.general_alphabet_periodic(max_period=15)
        assert [p for p in res["mixed_plain_alphabet"] if p <= 12] == []
        assert res["mixed_cipher_alphabet_add"] == [] and res["mixed_cipher_alphabet_sub"] == []
        assert fc.general_alphabet_control_rate(12, trials=40) == 0.0


class TestDialKey:
    def test_planted_compass_dial_key_is_found(self):
        n, start, step, b = 360, 17, 41, 9
        key = [(((start + step * i) % n) * 26 // n + b) % 26 for i in range(97)]
        ct = _vig(PLAIN_TEXT, key)
        res = fc.dial_key_scan({"compass degrees": 360}, ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        hits = res["vigenere"]["compass degrees"]
        assert any(h["start"] == start and h["step"] == step and h["rule"] == "scaled" for h in hits)

    def test_k4_has_no_dial_key(self):
        res = fc.dial_key_scan({"12-hour face": 12, "24-hour ring": 24, "minutes": 60})
        assert all(not hits for fam in res.values() for hits in fam.values())


class TestBearingRoute:
    def test_routes_are_permutations_and_axis_bearings_read_rows(self):
        for bearing in (0, 45, 90, 137, 270):
            route = fc.bearing_route(97, 8, bearing)
            assert sorted(route) == list(range(97))
        # Bearing 90 (east) reads row by row, left to right.
        assert fc.bearing_route(20, 5, 90)[:5] == [0, 1, 2, 3, 4]

    def test_planted_bearing_route_with_periodic_key_is_found(self):
        route = fc.bearing_route(97, 9, 60)
        key = [2, 14, 7, 21, 9]
        sub = _vig(PLAIN_TEXT, [key[i % 5] for i in range(97)])
        ct = "".join(sub[i] for i in route)  # ciphertext read off the grid along the bearing
        res = fc.bearing_route_scan(widths=[9], periods=[5], ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert res["sub_then_trans"]["vigenere"][5]["survivors"] >= 1
        assert any(e["bearing"] == 60 for e in res["sub_then_trans"]["vigenere"][5]["examples"])


class TestVocabularyPhraseKeys:
    def test_planted_phrase_key_positive_control(self):
        phrase = "PALIMPSESTABSCISSAKRYPTOS"
        ka = cc_keyed("KRYPTOS")
        key = [ka.index(phrase[(i + 4) % len(phrase)]) for i in range(97)]
        ct = "".join(ka[(ka.index(c) + k) % 26] for c, k in zip(PLAIN_TEXT, key, strict=True))
        res = fc.vocabulary_phrase_keys(
            words=["PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLIN"],
            min_len=20,
            ciphertext=ct,
            plain=_cribs_of(PLAIN_TEXT),
        )
        assert {"phrase": phrase, "family": "quagmire3_kryptos", "offset": 4} in res["hits"]

    def test_k4_no_vocabulary_phrase_key(self):
        res = fc.vocabulary_phrase_keys(max_words=3)
        assert res["phrases_tested"] > 20_000 and res["hits"] == []


class TestWideColumnar:
    def test_matches_brute_force_where_both_run(self):
        from kryptos.k4.crib_constraints import columnar_period_scan

        wide = fc.wide_columnar_scan(widths=[7], periods=[5, 13, 22])[7]
        brute = columnar_period_scan(widths=[7], periods=[5, 13, 22])[7]
        for model in ("sub_then_trans", "trans_then_sub"):
            for fam, per in wide[model].items():
                for p, entry in per.items():
                    assert entry["survivors"] == brute[model][fam][p]["survivors"]

    def test_planted_width_11_positive_control_is_found_and_decrypts(self):
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

        order = [4, 9, 0, 7, 2, 10, 5, 1, 8, 3, 6]
        key = [11, 3, 20, 7, 15, 0, 22]
        ct = apply_columnar_permutation_encrypt(_vig(PLAIN_TEXT, [key[i % 7] for i in range(97)]), 11, order)
        res = fc.wide_columnar_scan(widths=[11], periods=[7], ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        entry = res[11]["sub_then_trans"]["vigenere"][7]
        assert order in entry["examples"] and entry["best_english_z"] > 0.8

    def test_planted_trans_then_sub_is_found(self):
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

        order = [2, 7, 0, 9, 4, 1, 8, 5, 3, 6]
        key = [5, 18, 2, 9, 24]
        moved = apply_columnar_permutation_encrypt(PLAIN_TEXT, 10, order)
        ct = _vig(moved, [key[i % 5] for i in range(97)])
        res = fc.wide_columnar_scan(widths=[10], periods=[5], ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert order in res[10]["trans_then_sub"]["vigenere"][5]["examples"]
        assert res[10]["trans_then_sub"]["vigenere"][5]["best_english_z"] > 0.8

    def test_k4_width_10_has_no_survivors_to_period_22(self):
        res = fc.wide_columnar_scan(widths=[10])
        assert all(e["survivors"] == 0 for m in res[10].values() for fam in m.values() for e in fam.values())


class TestHill:
    def _encrypt(self, key: np.ndarray, pt: str, offset: int = 0) -> str:
        n = len(key)
        out = list(pt)
        for b in range(offset, len(pt) - n + 1, n):
            v = (key @ np.array([S.index(c) for c in pt[b : b + n]])) % 26
            out[b : b + n] = [S[x] for x in v]
        return "".join(out)

    def test_planted_hill4_is_found_and_reads_as_english(self):
        m = np.array([[5, 5, 9, 10], [6, 17, 21, 20], [6, 5, 22, 6], [12, 9, 0, 11]])  # det 15, coprime to 26
        assert fc._invertible_mod26(m)
        ct = self._encrypt(m, PLAIN_TEXT, offset=1)
        res = fc.hill_exhaustive(sizes=(4,), ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        hit = next(r for r in res[4] if r["offset"] == 1)
        assert hit["status"] == "decrypted" and hit["best_english_z"] > 0.6

    def test_k4_has_no_invertible_hill4(self):
        res = fc.hill_exhaustive(sizes=(4,))
        assert all(r.get("invertible_matrices", 0) == 0 for r in res[4])


class TestHill5:
    @pytest.mark.slow
    def test_planted_hill5_positive_control_scores_as_english(self):
        rng = random.Random(7)
        while True:
            m = np.array([[rng.randrange(26) for _ in range(5)] for _ in range(5)])
            if fc._invertible_mod26(m):
                break
        ct = TestHill()._encrypt(m, PLAIN_TEXT, offset=4)
        res = fc.hill_rowspace_search(5, ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert res[4]["status"] == "searched" and res[4]["best_english_z"] > 0.8

    @pytest.mark.slow
    def test_k4_hill5_stays_near_noise(self):
        res = fc.hill_rowspace_search(5)
        assert res[3]["status"] == "no consistent matrix"
        assert res[4]["best_english_z"] < 0.6


class TestHillBeam:
    @pytest.mark.slow
    def test_planted_hill5_positive_control_found_by_beam(self):
        rng = random.Random(7)
        while True:
            m = np.array([[rng.randrange(26) for _ in range(5)] for _ in range(5)])
            if fc._invertible_mod26(m):
                break
        ct = TestHill()._encrypt(m, PLAIN_TEXT, offset=1)
        res = fc.hill_beam_search(5, [1], ciphertext=ct, plain=_cribs_of(PLAIN_TEXT))
        assert res[0]["best_english_z"] > 0.8

    def test_beam_refuses_underconstrained_alignments(self):
        res = fc.hill_beam_search(5, [0], plain={})
        assert res[0]["status"] == "too many row choices for the beam"

    def test_k4_hill5_alignment_2_has_no_matrix(self):
        res = fc.hill_beam_search(5, [2])
        assert res[0]["status"] == "no consistent matrix"


class TestReconstruction:
    def test_reconstruction_has_the_cribs(self):
        assert len(PLAIN) == 97
        assert all(PLAIN[i] == c for i, c in crib_letters().items())
        assert K4[63:69] == "NYPVTT"

    @pytest.mark.slow
    def test_reconstruction_suite_runs(self):
        res = fc.reconstruction_suite(columnar_widths=range(2, 6))

        def empty_lists(d):
            return all(v == [] for v in d.values())

        for key in (
            "periodic_1_48",
            "ciphertext_autokey",
            "plaintext_autokey",
            "linear_key",
            "progressive_key_1_48",
            "double_periodic_p_le_45",
            "recurrence_key_1_40",
            "general_alphabet_periodic_1_48",
        ):
            assert empty_lists(res[key]), key
        assert all(v == [] for v in res["hill_2_9"].values())
        assert all(n == 0 for fam in res["dial_keys"].values() for n in fam.values())
        assert all(v["english_z"] < 0.3 for v in res["running_key_keystreams"].values())
        assert all(n == 0 for n in res["columnar_period_1_48"].values())
        assert res["geometry_period_1_48"] == 0
        assert res["double_rotation_period_1_48"] == 0
        assert res["bearing_route_period_1_48"] == 0

    @pytest.mark.slow
    def test_reconstruction_dictionary_quagmires_have_no_fit(self):
        res = fc.reconstruction_suite(columnar_widths=[2], include_dictionary=True)
        assert all(n == 0 for n in res["keyword_alphabets_1_48"].values())
        assert res["quagmire4_dictionary_1_48"] == 0


def test_english_z_rejects_unsupported_lengths():
    with pytest.raises(ValueError):
        english_z("ABC")
    with pytest.raises(ValueError):
        english_z("A" * 5000)


def test_columnar_decrypt_score_skips_unscorable_lengths():
    from kryptos.k4.crib_constraints import families

    alpha, fn = families()["vigenere"]
    text = PLAIN_TEXT[:12]
    plain = {i: text[i] for i in range(10)}  # only 2 non-crib letters
    assert fc._best_columnar_decrypt_z([0, 1, 2], 3, 2, "sub_then_trans", alpha, fn, text, plain) is None
