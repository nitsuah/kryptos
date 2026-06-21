"""Tests for the 3-layer S→T→S composite chain (K4-ATTACK extension)."""

from kryptos.k4.composite import CompositeChainExecutor

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
_SHORT = "HIDDENMESSAGEHEREX"


class TestStoTSChain:
    executor = CompositeChainExecutor()

    def test_returns_list(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=3,
        )
        assert isinstance(result, list)

    def test_result_dicts_have_required_keys(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=3,
        )
        for item in result:
            assert "plaintext" in item
            assert "score" in item
            assert "outer_vigenere_key" in item
            assert "transposition_cols" in item
            assert "transposition_perm" in item
            assert "inner_vigenere_key" in item
            assert item["chain"] == "S→T→S"

    def test_top_n_respected(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=2,
        )
        assert len(result) <= 2

    def test_scores_are_floats(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=3,
        )
        for item in result:
            assert isinstance(item["score"], float)

    def test_sorted_by_score_descending(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=5,
        )
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_min_score_threshold_filters(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=10,
            min_score_threshold=1e9,  # impossibly high → empty
        )
        assert result == []

    def test_k4_input_does_not_crash(self):
        """Smoke test: S→T→S chain on actual K4 ciphertext must not raise."""
        result = self.executor.substitution_then_transposition_then_substitution(
            K4,
            vigenere_key_length=4,
            transposition_col_range=(5, 6),
            second_key_length=4,
            top_n=3,
        )
        assert isinstance(result, list)

    def test_chain_label(self):
        result = self.executor.substitution_then_transposition_then_substitution(
            _SHORT,
            vigenere_key_length=3,
            transposition_col_range=(3, 4),
            second_key_length=3,
            top_n=1,
        )
        if result:
            assert result[0]["chain"] == "S→T→S"
