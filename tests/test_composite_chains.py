"""Tests for composite chain execution (V→T, T→V)."""

from __future__ import annotations

from kryptos.k4.composite import CompositeChainExecutor


class TestCompositeChains:
    """Test multi-stage cipher chains."""

    def test_vigenere_then_transposition_returns_valid_structure(self):
        """Test V→T chain returns proper structure."""
        # Use K2 ciphertext as test case
        ciphertext = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK"

        executor = CompositeChainExecutor()
        results = executor.vigenere_then_transposition(
            ciphertext,
            vigenere_key_length=8,
            transposition_col_range=(3, 5),
            top_n=10,
        )

        assert len(results) > 0, "Should return results"
        assert len(results) <= 10, "Should respect top_n limit"
        # Verify structure
        assert 'plaintext' in results[0]
        assert 'vigenere_key' in results[0]
        assert 'transposition_cols' in results[0]
        assert 'chain' in results[0]
        assert results[0]['chain'] == 'V→T'

    def test_transposition_then_vigenere_structure(self):
        """Test T→V chain returns proper structure."""
        # Simple test ciphertext
        ciphertext = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK"

        executor = CompositeChainExecutor()
        results = executor.transposition_then_vigenere(
            ciphertext,
            transposition_col_range=(5, 7),
            vigenere_key_length=8,
            top_n=5,
        )

        assert len(results) <= 5, "Should respect top_n limit"
        if results:
            assert 'plaintext' in results[0]
            assert 'vigenere_key' in results[0]
            assert 'transposition_cols' in results[0]
            assert 'chain' in results[0]
            assert results[0]['chain'] == 'T→V'

    def test_chain_returns_sorted_by_score(self):
        """Test chain results are sorted by score (highest first)."""
        ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"

        executor = CompositeChainExecutor()
        results = executor.vigenere_then_transposition(
            ciphertext,
            vigenere_key_length=8,
            transposition_col_range=(4, 6),
            top_n=10,
        )

        # Verify scores are descending
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]['score'] >= results[i + 1]['score'], "Results should be sorted by score descending"
