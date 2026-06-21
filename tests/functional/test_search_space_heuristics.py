"""Tests for cross-run memory heuristics added to SearchSpaceTracker."""

from pathlib import Path

from kryptos.provenance.search_space import SearchSpaceTracker, _levenshtein


class TestLevenshtein:
    def test_identical(self):
        assert _levenshtein("KRYPTOS", "KRYPTOS") == 0

    def test_single_sub(self):
        assert _levenshtein("KRYPTOS", "KRYPTOX") == 1

    def test_single_insert(self):
        assert _levenshtein("KRPTO", "KRYPTOS") == 2

    def test_empty(self):
        assert _levenshtein("", "ABC") == 3
        assert _levenshtein("ABC", "") == 3

    def test_symmetric(self):
        assert _levenshtein("NORTH", "SOUTH") == _levenshtein("SOUTH", "NORTH")


class TestAlreadyTriedFuzzy:
    def _tracker(self, tmp_path: Path) -> SearchSpaceTracker:
        return SearchSpaceTracker(cache_dir=tmp_path)

    def test_exact_hit(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        assert t.already_tried_fuzzy("vigenere", "KRYPTOS", tol=0) is True

    def test_fuzzy_hit_within_tol(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        # KRYPTOX is 1 edit from KRYPTOS
        assert t.already_tried_fuzzy("vigenere", "KRYPTOX", tol=1) is True

    def test_fuzzy_miss_outside_tol(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        # BERLIN is ≥2 edits from KRYPTOS
        assert t.already_tried_fuzzy("vigenere", "BERLIN", tol=1) is False

    def test_tol_zero_is_exact_only(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        assert t.already_tried_fuzzy("vigenere", "KRYPTOX", tol=0) is False
        assert t.already_tried_fuzzy("vigenere", "KRYPTOS", tol=0) is True

    def test_empty_tried_set(self, tmp_path):
        t = self._tracker(tmp_path)
        assert t.already_tried_fuzzy("vigenere", "ANYTHING", tol=1) is False

    def test_cipher_type_isolation(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        # Key is tried under "vigenere" but not under "beaufort"
        assert t.already_tried_fuzzy("beaufort", "KRYPTOX", tol=1) is False

    def test_length_gate_avoids_false_positives(self, tmp_path):
        t = self._tracker(tmp_path)
        t.mark_tried("vigenere", "A")
        # "KRYPTOS" is 6 edits from "A" — must NOT match with tol=1
        assert t.already_tried_fuzzy("vigenere", "KRYPTOS", tol=1) is False


class TestGetPriorityRecommendations:
    def _populated_tracker(self, tmp_path: Path) -> SearchSpaceTracker:
        t = SearchSpaceTracker(cache_dir=tmp_path)
        t.register_region("vigenere", "length_8", {"key_length": 8}, total_size=200_000_000)
        t.register_region("vigenere", "length_6", {"key_length": 6}, total_size=300_000_000)
        t.register_region("beaufort", "key_1", {}, total_size=10_000)
        t.record_exploration("vigenere", "length_8", count=1000, successful=5)
        return t

    def test_returns_list(self, tmp_path):
        t = self._populated_tracker(tmp_path)
        recs = t.get_priority_recommendations(top_n=3)
        assert isinstance(recs, list)

    def test_respects_top_n(self, tmp_path):
        t = self._populated_tracker(tmp_path)
        recs = t.get_priority_recommendations(top_n=2)
        assert len(recs) <= 2

    def test_contains_required_keys(self, tmp_path):
        t = self._populated_tracker(tmp_path)
        recs = t.get_priority_recommendations(top_n=3)
        for rec in recs:
            assert "cipher_type" in rec
            assert "region" in rec
            assert "adjusted_score" in rec
            assert "tried_key_count" in rec

    def test_unexplored_region_boosted(self, tmp_path):
        """Zero-coverage regions receive the diversity_bonus on top of their base score."""
        t = self._populated_tracker(tmp_path)
        # Register two equal-sized regions: one untouched, one partly explored
        t.register_region("test_cipher", "untouched", {}, total_size=1_000_000)
        t.register_region("test_cipher", "partial", {}, total_size=1_000_000)
        t.record_exploration("test_cipher", "partial", count=100)  # 0.01% coverage
        recs = t.get_priority_recommendations(top_n=10, diversity_bonus=20.0)
        untouched_rec = next((r for r in recs if r["region"] == "untouched"), None)
        partial_rec = next((r for r in recs if r["region"] == "partial"), None)
        assert untouched_rec is not None
        assert partial_rec is not None
        # The untouched region gets +20 diversity bonus; partial does not → higher adjusted score
        assert untouched_rec["adjusted_score"] > partial_rec["adjusted_score"]

    def test_tried_key_count_accurate(self, tmp_path):
        t = self._populated_tracker(tmp_path)
        t.mark_tried("vigenere", "KRYPTOS")
        t.mark_tried("vigenere", "ABSCISSA")
        recs = t.get_priority_recommendations(top_n=5)
        vig_recs = [r for r in recs if r["cipher_type"] == "vigenere"]
        if vig_recs:
            assert vig_recs[0]["tried_key_count"] == 2
