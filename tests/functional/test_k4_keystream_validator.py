"""Tests for keystream_validator — confirmed K4 crib shift computation."""

from kryptos.k4.keystream_validator import (
    K4_CRIBS,
    K4_EXPECTED_KEYSTREAMS,
    compute_shifts_at_cribs,
    crib_hit_count,
    keystream_summary,
    validate_k4_cribs,
)

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


class TestComputeShifts:
    def test_east_shifts(self):
        observed = compute_shifts_at_cribs(K4, {"EAST": ("EAST", 21)})
        assert observed["EAST"] == [1, 11, 25, 2]

    def test_northeast_shifts(self):
        observed = compute_shifts_at_cribs(K4, {"NORTHEAST": ("NORTHEAST", 25)})
        assert observed["NORTHEAST"] == [3, 2, 24, 24, 6, 2, 10, 0, 25]

    def test_berlin_shifts(self):
        observed = compute_shifts_at_cribs(K4, {"BERLIN": ("BERLIN", 63)})
        assert observed["BERLIN"] == [12, 20, 24, 10, 11, 6]

    def test_clock_shifts(self):
        observed = compute_shifts_at_cribs(K4, {"CLOCK": ("CLOCK", 69)})
        assert observed["CLOCK"] == [10, 14, 17, 13, 0]

    def test_all_four_cribs(self):
        observed = compute_shifts_at_cribs(K4, K4_CRIBS)
        assert observed == K4_EXPECTED_KEYSTREAMS

    def test_extra_whitespace_stripped(self):
        k4_spaced = "OBKRUOXO GHULBSO LIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"  # noqa: E501
        observed = compute_shifts_at_cribs(k4_spaced, {"EAST": ("EAST", 21)})
        assert observed["EAST"] == [1, 11, 25, 2]


class TestValidateK4Cribs:
    def test_k4_validates_all_cribs(self):
        result = validate_k4_cribs(K4)
        assert all(result.values()), f"Some cribs failed: {result}"

    def test_garbled_ciphertext_fails(self):
        bad = "A" * 97
        result = validate_k4_cribs(bad)
        assert not any(result.values())

    def test_individual_crib_fail(self):
        # Corrupt one position in the EAST window
        k4_list = list(K4)
        k4_list[22] = "A"  # was 'L', breaks EAST
        corrupted = "".join(k4_list)
        result = validate_k4_cribs(corrupted)
        assert result["EAST"] is False
        assert result["NORTHEAST"] is True  # unaffected


class TestCribHitCount:
    def test_real_k4_scores_four(self):
        assert crib_hit_count(K4) == 4

    def test_empty_scores_zero(self):
        assert crib_hit_count("A" * 97) == 0

    def test_partial_corruption_scores_less(self):
        k4_list = list(K4)
        k4_list[22] = "A"
        corrupted = "".join(k4_list)
        assert crib_hit_count(corrupted) == 3


class TestKeystreamSummary:
    def test_summary_structure(self):
        summary = keystream_summary(K4)
        assert set(summary.keys()) == {"EAST", "NORTHEAST", "BERLIN", "CLOCK"}
        for _label, info in summary.items():
            assert "observed_shifts" in info
            assert "expected_shifts" in info
            assert "match" in info

    def test_all_match_on_real_k4(self):
        summary = keystream_summary(K4)
        assert all(info["match"] for info in summary.values())
