"""Tests for kryptos.k4.validation — validation pipeline + adversarial benchmarks."""

from __future__ import annotations

from kryptos.k4 import validation as v
from kryptos.k4.physical_grid import K4


def _planted_text() -> str:
    text = list("A" * 97)
    text[22:26] = "EAST"
    text[26:35] = "NORTHEAST"
    text[63:69] = "BERLIN"
    text[69:74] = "CLOCK"
    return "".join(text)


class TestCribMatchLevel:
    def test_real_k4_has_zero_known_matches(self):
        assert v.crib_match_level(K4) == 0

    def test_planted_text_matches_all(self):
        assert v.crib_match_level(_planted_text()) == 4


class TestComplexityAndOverfitting:
    def test_more_parameters_is_worse(self):
        assert v.complexity_score(3, 0) > v.complexity_score(5, 3)

    def test_brief_example_ordering(self):
        simple = v.overfitting_guard(crib_hits=4, param_count=3, exceptions=0)
        complicated = v.overfitting_guard(crib_hits=4, param_count=17 + 3, exceptions=3)
        assert simple > complicated

    def test_crib_hits_dominate_complexity(self):
        fewer_hits_simple = v.overfitting_guard(crib_hits=1, param_count=1, exceptions=0)
        more_hits_complex = v.overfitting_guard(crib_hits=2, param_count=10, exceptions=5)
        assert more_hits_complex > fewer_hits_simple


class TestIndependentReproduction:
    def test_matching_reproduction_passes(self):
        key_info = {"value": "X"}
        assert v.independent_reproduction_check(key_info, lambda ki: ki["value"], "X")

    def test_mismatched_reproduction_fails(self):
        key_info = {"value": "X"}
        assert not v.independent_reproduction_check(key_info, lambda ki: ki["value"], "Y")


class TestValidateCandidate:
    def test_promotes_only_on_full_match_and_reproduction(self):
        text = _planted_text()
        result = v.validate_candidate(text, {}, lambda ki: text, param_count=3)
        assert result["promote"] is True
        assert result["crib_hits"] == 4

    def test_does_not_promote_on_reproduction_mismatch(self):
        text = _planted_text()
        result = v.validate_candidate(text, {}, lambda ki: "WRONG" + text[5:], param_count=3)
        assert result["promote"] is False

    def test_does_not_promote_on_partial_crib_match(self):
        result = v.validate_candidate(K4, {}, lambda ki: K4, param_count=3)
        assert result["promote"] is False


class TestExternalCandidateBenchmark:
    def test_field_guide_registered(self):
        assert "solvekryptos_field_guide" in v.EXTERNAL_CANDIDATES

    def test_field_guide_fails_strict_validation(self):
        result = v.benchmark_external_candidate("solvekryptos_field_guide")
        assert result["verdict"] == "fails_strict_validation"
        assert result["exact_positional_hits"] == 2

    def test_field_guide_berlin_and_clock_exact(self):
        result = v.benchmark_external_candidate("solvekryptos_field_guide")
        assert result["per_crib"]["BERLIN"]["exact_match"] is True
        assert result["per_crib"]["CLOCK"]["exact_match"] is True

    def test_field_guide_east_northeast_off_by_one(self):
        result = v.benchmark_external_candidate("solvekryptos_field_guide")
        assert result["per_crib"]["EAST"]["offset_from_expected"] == -1
        assert result["per_crib"]["NORTHEAST"]["offset_from_expected"] == -1

    def test_normalized_length_matches_k4(self):
        result = v.benchmark_external_candidate("solvekryptos_field_guide")
        assert result["normalized_length"] == len(K4)


class TestStructuralDiagnostics:
    def test_w_delimiter_count_on_real_k4(self):
        result = v.check_w_delimiter_pattern()
        assert result["w_count"] == 5
        assert result["w_positions"] == [20, 36, 48, 58, 74]

    def test_stehle_window_on_real_k4(self):
        result = v.check_stehle_anomaly()
        assert result["window"] == K4[55:63]
        assert len(result["letter_diffs_mod26"]) == 7
