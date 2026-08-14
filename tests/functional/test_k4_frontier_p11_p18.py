"""Tests for K4 Phase 2 frontier attacks: P11 (alt keywords), P17 (bigram), P18 (key CSP)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# P11 — Alternative keyed-alphabet keywords
# ---------------------------------------------------------------------------
class TestAltKeywords:
    def test_p11_keywords_list_not_empty(self):
        from kryptos.k4.alt_keywords import P11_KEYWORDS
        assert len(P11_KEYWORDS) >= 10

    def test_alt_keyed_alphabets_all_26_unique(self):
        from kryptos.k4.alt_keywords import ALT_KEYED_ALPHABETS
        for name, alpha in ALT_KEYED_ALPHABETS.items():
            assert len(alpha) == 26, f"{name} alphabet wrong length"
            assert len(set(alpha)) == 26, f"{name} alphabet has duplicates"

    def test_sanborn_alphabet_starts_with_s(self):
        from kryptos.k4.alt_keywords import ALT_KEYED_ALPHABETS
        assert ALT_KEYED_ALPHABETS["SANBORN"][0] == "S"

    def test_scheidt_alphabet_starts_with_s(self):
        from kryptos.k4.alt_keywords import ALT_KEYED_ALPHABETS
        assert ALT_KEYED_ALPHABETS["SCHEIDT"][0] == "S"

    def test_northeast_alphabet_starts_with_n(self):
        from kryptos.k4.alt_keywords import ALT_KEYED_ALPHABETS
        assert ALT_KEYED_ALPHABETS["NORTHEAST"][0] == "N"

    def test_combined_alphabets_superset(self):
        from kryptos.k4.alt_keywords import COMBINED_ALPHABETS, ALT_KEYED_ALPHABETS
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS
        for key in KNOWN_KEYED_ALPHABETS:
            assert key in COMBINED_ALPHABETS
        for key in ALT_KEYED_ALPHABETS:
            assert key in COMBINED_ALPHABETS

    def test_no_keyword_overlap_with_known(self):
        from kryptos.k4.alt_keywords import P11_KEYWORDS
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS
        for kw in P11_KEYWORDS:
            assert kw not in KNOWN_KEYED_ALPHABETS, f"{kw} already in KNOWN_KEYED_ALPHABETS"

    def test_build_keyed_alphabet_round_trip(self):
        from kryptos.k4.vigenere_key_recovery import build_keyed_alphabet
        alpha = build_keyed_alphabet("LANGLEY")
        assert alpha.startswith("LANGEY"), f"LANGLEY alpha should start with L,A,N,G,E,Y got {alpha[:6]}"
        assert len(alpha) == 26
        assert len(set(alpha)) == 26

    def test_p11_module_importable(self):
        from kryptos.k4.alt_keywords import run_alt_keyword_sweep  # noqa: F401
        assert callable(run_alt_keyword_sweep)


# ---------------------------------------------------------------------------
# P17 — Bigram constraints
# ---------------------------------------------------------------------------
class TestBigramConstraint:
    def test_find_doubled_pairs_returns_expected(self):
        from kryptos.k4.bigram_constraint import find_doubled_pairs, K4
        pairs = find_doubled_pairs(K4)
        positions = [p["position"] for p in pairs]
        # QQ at 25, SS at 32, SS at 42, ZZ at 46 (approx — depends on exact K4 indexing)
        assert len(pairs) >= 4, f"Expected ≥4 doubled pairs, got {len(pairs)} at {positions}"

    def test_qq_is_rare_doublet(self):
        from kryptos.k4.bigram_constraint import find_doubled_pairs, K4, RARE_DOUBLETS
        pairs = find_doubled_pairs(K4)
        qq_pairs = [p for p in pairs if p["letter"] == "Q"]
        assert len(qq_pairs) >= 1, "Expected QQ pair in K4"
        for p in qq_pairs:
            assert p["is_rare_doublet"], f"Q should be flagged as rare doublet"

    def test_filter_candidates_passes_common_doublets(self):
        from kryptos.k4.bigram_constraint import filter_candidates_by_doublets, COMMON_ENGLISH_DOUBLETS
        # Build a candidate that has 'LL' at each doubled position
        cand = "A" * 50 + "L" * 2 + "A" * 50
        # positions=[25] with 'L' at 25 should pass
        results = filter_candidates_by_doublets([cand], doubled_positions=[25])
        assert results[0][1] is True

    def test_filter_candidates_blocks_rare_doublets(self):
        from kryptos.k4.bigram_constraint import filter_candidates_by_doublets
        # Build a candidate with Q at position 25 (rare doublet in English)
        cand = "A" * 25 + "QQ" + "A" * 70
        results = filter_candidates_by_doublets([cand], doubled_positions=[25], strict=True)
        assert results[0][1] is False

    def test_doubled_constraint_analysis_structure(self):
        from kryptos.k4.bigram_constraint import doubled_constraint_analysis
        report = doubled_constraint_analysis()
        assert "doubled_pairs" in report
        assert "total_pairs" in report
        assert report["total_pairs"] >= 4
        assert "summary" in report
        assert isinstance(report["summary"], str)

    def test_analysis_includes_key_length_implications(self):
        from kryptos.k4.bigram_constraint import doubled_constraint_analysis
        report = doubled_constraint_analysis()
        # Some key lengths should have implications (L where pos%L == (pos+1)%L — only L=1)
        assert "key_length_implications" in report

    def test_valid_english_doublets_set(self):
        from kryptos.k4.bigram_constraint import valid_english_doublets
        ds = valid_english_doublets()
        assert "L" in ds
        assert "S" in ds
        assert "E" in ds


# ---------------------------------------------------------------------------
# P18 — Repeating-key CSP
# ---------------------------------------------------------------------------
class TestKeyCsp:
    def test_crib_shifts_count(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        # 4 (EAST) + 9 (NORTHEAST) + 6 (BERLIN) + 5 (CLOCK) = 24
        assert len(CRIB_SHIFTS) == 24

    def test_crib_shifts_all_valid_range(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        for pos, shift in CRIB_SHIFTS:
            assert 0 <= pos < 97, f"Position {pos} out of K4 range"
            assert 0 <= shift < 26, f"Shift {shift} out of range for position {pos}"

    def test_east_shifts_correct(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        # EAST @ 22-25: shifts [7, 17, 3, 23]
        east = {pos: shift for pos, shift in CRIB_SHIFTS if 22 <= pos <= 25}
        assert east == {22: 7, 23: 17, 24: 3, 25: 23}

    def test_northeast_shifts_correct(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        # NORTHEAST @ 26-34: shifts [3, 1, 0, 20, 25, 6, 18, 0, 21]
        ne = {pos: shift for pos, shift in CRIB_SHIFTS if 26 <= pos <= 34}
        expected = {26: 3, 27: 1, 28: 0, 29: 20, 30: 25, 31: 6, 32: 18, 33: 0, 34: 21}
        assert ne == expected

    def test_berlin_shifts_correct(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        berlin = {pos: shift for pos, shift in CRIB_SHIFTS if 63 <= pos <= 68}
        expected = {63: 12, 64: 20, 65: 24, 66: 10, 67: 11, 68: 6}
        assert berlin == expected

    def test_clock_shifts_correct(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS
        clock = {pos: shift for pos, shift in CRIB_SHIFTS if 69 <= pos <= 73}
        expected = {69: 10, 70: 14, 71: 17, 72: 13, 73: 0}
        assert clock == expected

    def test_solve_key_csp_returns_dict(self):
        from kryptos.k4.key_csp import solve_key_csp
        result = solve_key_csp(key_lengths=range(2, 10))
        assert isinstance(result, dict)

    def test_key_length_1_always_inconsistent(self):
        from kryptos.k4.key_csp import solve_key_csp
        # L=1 means every position maps to slot 0. Shifts 7,17,3,23,... are all different → inconsistent.
        result = solve_key_csp(key_lengths=[1])
        assert 1 not in result

    def test_consistent_lengths_have_partial_keys(self):
        from kryptos.k4.key_csp import solve_key_csp
        result = solve_key_csp(key_lengths=range(2, 15))
        for L, key in result.items():
            assert len(key) == L
            # Each constrained slot must be a valid shift (0-25)
            for s in key:
                if s is not None:
                    assert 0 <= s < 26

    def test_partial_key_to_alphabet_converts(self):
        from kryptos.k4.key_csp import partial_key_to_alphabet
        key = [0, 7, None, 25]
        letters = partial_key_to_alphabet(key)
        assert letters == ["A", "H", "?", "Z"]

    def test_run_key_csp_attack_returns_summary(self):
        from kryptos.k4.key_csp import run_key_csp_attack
        summary = run_key_csp_attack(key_lengths=range(2, 8), null_artifact_path="K4_P18_TEST_NULL.json")
        assert "consistent_lengths" in summary
        assert "csp_results" in summary
        assert "best_candidates" in summary
        assert "attack" in summary

    def test_shifts_for_text_helper(self):
        from kryptos.k4.key_csp import _shifts_for_text
        # L(11) - E(4) = 7
        pairs = _shifts_for_text("LRVQ", "EAST", 22)
        assert pairs[0] == (22, 7)
        assert pairs[1] == (23, 17)
        assert pairs[2] == (24, 3)
        assert pairs[3] == (25, 23)
