"""Tests for K4 Phase 2 frontier attacks: P11/P12/P13 (alphabets/clock), P17 (bigram), P18 (key CSP)."""

from __future__ import annotations


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
        from kryptos.k4.alt_keywords import ALT_KEYED_ALPHABETS, COMBINED_ALPHABETS
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
# P12 — Misspelling-derived alphabets
# ---------------------------------------------------------------------------
class TestMisspellingAlphabets:
    def test_misspelling_alphabets_count(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS

        # 3 base keywords × 3 swap combos = 9 alphabets
        assert len(MISSPELLING_ALPHABETS) == 9

    def test_all_alphabets_valid_26_unique(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS

        for name, alpha in MISSPELLING_ALPHABETS.items():
            assert len(alpha) == 26, f"{name} has wrong length"
            assert len(set(alpha)) == 26, f"{name} has duplicate letters"

    def test_il_swap_kryptos_swaps_i_and_l(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        base = KNOWN_KEYED_ALPHABETS["KRYPTOS"]
        swapped = MISSPELLING_ALPHABETS["KRYPTOS_swap_IL"]
        # I and L should be at each other's original positions
        pos_i_base, pos_l_base = base.index("I"), base.index("L")
        pos_i_swap, pos_l_swap = swapped.index("I"), swapped.index("L")
        assert pos_i_swap == pos_l_base
        assert pos_l_swap == pos_i_base

    def test_ae_swap_palimpsest_swaps_a_and_e(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        base = KNOWN_KEYED_ALPHABETS["PALIMPSEST"]
        swapped = MISSPELLING_ALPHABETS["PALIMPSEST_swap_AE"]
        pos_a_base, pos_e_base = base.index("A"), base.index("E")
        pos_a_swap, pos_e_swap = swapped.index("A"), swapped.index("E")
        assert pos_a_swap == pos_e_base
        assert pos_e_swap == pos_a_base

    def test_both_swaps_differ_from_single_swaps(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS

        both = MISSPELLING_ALPHABETS["KRYPTOS_swap_IL_AE"]
        il = MISSPELLING_ALPHABETS["KRYPTOS_swap_IL"]
        ae = MISSPELLING_ALPHABETS["KRYPTOS_swap_AE"]
        assert both != il
        assert both != ae

    def test_build_swapped_alphabet_identity(self):
        from kryptos.k4.misspelling_alphabets import build_swapped_alphabet

        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = build_swapped_alphabet(alpha, [])
        assert result == alpha

    def test_build_swapped_alphabet_ab_swap(self):
        from kryptos.k4.misspelling_alphabets import build_swapped_alphabet

        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = build_swapped_alphabet(alpha, [("A", "B")])
        assert result[0] == "B" and result[1] == "A"
        assert result[2:] == alpha[2:]

    def test_p12_module_importable(self):
        from kryptos.k4.misspelling_alphabets import run_misspelling_sweep  # noqa: F401

        assert callable(run_misspelling_sweep)

    def test_named_alphabets_include_all_bases(self):
        from kryptos.k4.misspelling_alphabets import MISSPELLING_ALPHABETS

        bases = {"KRYPTOS", "PALIMPSEST", "ABSCISSA"}
        for base in bases:
            names = [k for k in MISSPELLING_ALPHABETS if k.startswith(base)]
            assert len(names) == 3, f"Expected 3 variants for {base}, got {names}"


# ---------------------------------------------------------------------------
# P13 — Magnetic declination clock offset
# ---------------------------------------------------------------------------
class TestMagneticDeclination:
    def test_declination_minutes_approx_20(self):
        from kryptos.k4.k2_clock_states import MAGNETIC_DECLINATION_MINUTES

        # 9.9 / 360 * 720 = 19.8, rounded = 20
        assert MAGNETIC_DECLINATION_MINUTES == 20

    def test_declination_constant_negative(self):
        from kryptos.k4.k2_clock_states import MAGNETIC_DECLINATION_DEG

        assert MAGNETIC_DECLINATION_DEG < 0  # west declination at CIA HQ

    def test_offset_time_minutes_forward(self):
        from kryptos.k4.k2_clock_states import offset_time_minutes

        result = offset_time_minutes("13:00", 20)
        assert result == "13:20"

    def test_offset_time_minutes_backward(self):
        from kryptos.k4.k2_clock_states import offset_time_minutes

        result = offset_time_minutes("13:00", -20)
        assert result == "12:40"

    def test_offset_time_minutes_wrap_midnight(self):
        from kryptos.k4.k2_clock_states import offset_time_minutes

        result = offset_time_minutes("23:50", 20)
        assert result == "00:10"

    def test_magnetic_states_returns_list(self):
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states

        states = get_magnetic_declination_states()
        assert isinstance(states, list)
        assert len(states) >= 2  # at least ±20min from CIA timestamp

    def test_magnetic_states_have_required_keys(self):
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states

        states = get_magnetic_declination_states()
        for s in states:
            assert "time" in s
            assert "shifts" in s
            assert "source" in s
            assert "is_offset" in s
            assert s["is_offset"] is True

    def test_magnetic_states_cia_times_present(self):
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states

        states = get_magnetic_declination_states()
        times = {s["time"] for s in states}
        # 13:00 ± 20 min → 12:40 and 13:20
        assert "12:40" in times
        assert "13:20" in times

    def test_magnetic_states_berlin_times_present(self):
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states

        states = get_magnetic_declination_states()
        times = {s["time"] for s in states}
        # 19:00 ± 20 min → 18:40 and 19:20
        assert "18:40" in times
        assert "19:20" in times


# ---------------------------------------------------------------------------
# P14 — CIA→Berlin bearing
# ---------------------------------------------------------------------------
class TestBearingAttack:
    def test_bearing_is_approx_44_degrees(self):
        from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_DEG

        # Great-circle bearing CIA HQ → Berlin ≈ 44.4° NNE
        assert 42 < CIA_BERLIN_BEARING_DEG < 47

    def test_bearing_int_is_44(self):
        from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_INT

        # round(44.4) = 44
        assert CIA_BERLIN_BEARING_INT == 44

    def test_great_circle_bearing_function(self):
        from kryptos.k4.bearing_attack import great_circle_bearing

        # Due east from equator should be 90°
        b = great_circle_bearing(0, 0, 0, 10)
        assert abs(b - 90.0) < 1.0

    def test_great_circle_bearing_north(self):
        from kryptos.k4.bearing_attack import great_circle_bearing

        # Due north should be 0°
        b = great_circle_bearing(0, 0, 10, 0)
        assert abs(b - 0.0) < 1.0 or abs(b - 360.0) < 1.0

    def test_run_bearing_attack_returns_summary(self):
        from kryptos.k4.bearing_attack import run_bearing_attack

        summary = run_bearing_attack(null_artifact_path="K4_P14_TEST_NULL.json")
        assert "attack" in summary
        assert summary["attack"] == "P14_bearing"
        assert "cia_berlin_bearing_deg" in summary
        assert "best_candidates" in summary

    def test_caesar_shift_is_18_mod_26(self):
        from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_INT

        # round(44.4) = 44, 44 mod 26 = 18 = letter S
        assert CIA_BERLIN_BEARING_INT % 26 == 18


# ---------------------------------------------------------------------------
# P17 — Bigram constraints
# ---------------------------------------------------------------------------
class TestBigramConstraint:
    def test_find_doubled_pairs_returns_expected(self):
        from kryptos.k4.bigram_constraint import K4, find_doubled_pairs

        pairs = find_doubled_pairs(K4)
        positions = [p["position"] for p in pairs]
        # QQ at 25, SS at 32, SS at 42, ZZ at 46 (approx — depends on exact K4 indexing)
        assert len(pairs) >= 4, f"Expected ≥4 doubled pairs, got {len(pairs)} at {positions}"

    def test_qq_is_rare_doublet(self):
        from kryptos.k4.bigram_constraint import K4, find_doubled_pairs

        pairs = find_doubled_pairs(K4)
        qq_pairs = [p for p in pairs if p["letter"] == "Q"]
        assert len(qq_pairs) >= 1, "Expected QQ pair in K4"
        for p in qq_pairs:
            assert p["is_rare_doublet"], "Q should be flagged as rare doublet"

    def test_filter_candidates_passes_common_doublets(self):
        from kryptos.k4.bigram_constraint import filter_candidates_by_doublets

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

        # EAST @ 21-24: shifts [1, 11, 25, 2]
        east = {pos: shift for pos, shift in CRIB_SHIFTS if 21 <= pos <= 24}
        assert east == {21: 1, 22: 11, 23: 25, 24: 2}

    def test_northeast_shifts_correct(self):
        from kryptos.k4.key_csp import CRIB_SHIFTS

        # NORTHEAST @ 25-33: shifts [3, 2, 24, 24, 6, 2, 10, 0, 25]
        ne = {pos: shift for pos, shift in CRIB_SHIFTS if 25 <= pos <= 33}
        expected = {25: 3, 26: 2, 27: 24, 28: 24, 29: 6, 30: 2, 31: 10, 32: 0, 33: 25}
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
