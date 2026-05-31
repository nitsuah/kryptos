"""Tests for SPY Web Intelligence incremental learning."""

import pytest

from kryptos.agents.spy_web_intel import SpyWebIntel


class TestIncrementalLearning:
    """Test that SPY doesn't reprocess old content."""

    def test_content_hash_uniqueness(self, tmp_path):
        """Test that content hashing detects duplicates."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        # Same content should produce same hash
        content1 = "This is a test content about KRYPTOS"
        content2 = "This is a test content about KRYPTOS"
        content3 = "This is different content about KRYPTOS"

        hash1 = spy._content_hash(content1)
        hash2 = spy._content_hash(content2)
        hash3 = spy._content_hash(content3)

        assert hash1 == hash2, "Same content should have same hash"
        assert hash1 != hash3, "Different content should have different hash"

    def test_is_content_new(self, tmp_path):
        """Test that new content detection works."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        content = "NORTHEAST is a confirmed crib in K4"

        # First time should be new
        assert spy._is_content_new(content) is True

        # Second time should not be new
        assert spy._is_content_new(content) is False

    def test_extract_cribs_skips_processed_content(self, tmp_path):
        """Test that extract_potential_cribs skips already-processed content."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        text = 'Sanborn said "NORTHEAST" is confirmed in K4.'

        # First extraction should return cribs
        cribs1 = spy.extract_potential_cribs(text)
        assert len(cribs1) > 0, "Should extract cribs first time"

        # Second extraction of same text should return empty
        cribs2 = spy.extract_potential_cribs(text)
        assert len(cribs2) == 0, "Should skip already-processed content"

    def test_processed_hashes_persist_across_sessions(self, tmp_path):
        """Test that processed content hashes are saved and loaded."""
        # First session
        spy1 = SpyWebIntel(cache_dir=tmp_path)
        content = "Test content about BERLIN and CLOCK"

        assert spy1._is_content_new(content) is True
        spy1._save_cache()

        # Second session (new instance)
        spy2 = SpyWebIntel(cache_dir=tmp_path)
        assert spy2._is_content_new(content) is False, "Should remember processed content"

    def test_different_content_processed_separately(self, tmp_path):
        """Test that different content is processed independently."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        content1 = "First article about KRYPTOS"
        content2 = "Second article about PALIMPSEST"

        # Both should be new initially
        assert spy._is_content_new(content1) is True
        assert spy._is_content_new(content2) is True

        # After processing, only these exact contents should be marked
        assert spy._is_content_new(content1) is False
        assert spy._is_content_new(content2) is False

        # New content should still be processed
        content3 = "Third article about ABSCISSA"
        assert spy._is_content_new(content3) is True

    def test_cache_size_growth(self, tmp_path):
        """Test that cache grows with unique content."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        # Process several unique pieces of content
        for i in range(10):
            content = f"Article {i} about Kryptos with unique content"
            spy._is_content_new(content)

        # Should have 10 unique hashes
        assert len(spy.processed_content_hashes) == 10

        # Process duplicates - cache shouldn't grow
        for i in range(10):
            content = f"Article {i} about Kryptos with unique content"
            spy._is_content_new(content)

        assert len(spy.processed_content_hashes) == 10, "Duplicates shouldn't grow cache"


@pytest.mark.integration
class TestWebIntelLearning:
    """Integration tests for learning over time."""

    def test_continuous_learning_session(self, tmp_path):
        """Test that SPY learns incrementally across multiple checks."""
        spy = SpyWebIntel(cache_dir=tmp_path)

        # Simulate three web scraping sessions
        session1_texts = [
            "Sanborn confirmed NORTHEAST in 2020",
            "The sculpture is located at CIA headquarters",
        ]

        session2_texts = [
            "Sanborn confirmed NORTHEAST in 2020",  # Duplicate
            "New interview mentions BERLIN CLOCK",  # New
        ]

        session3_texts = [
            "The sculpture is located at CIA headquarters",  # Duplicate
            "New clue discovered about PALIMPSEST",  # New
        ]

        # Session 1: Process initial texts
        cribs_s1 = []
        for text in session1_texts:
            cribs_s1.extend(spy.extract_potential_cribs(text))
        assert len(cribs_s1) > 0, "Should extract cribs in session 1"

        # Session 2: Should skip duplicate, process new
        cribs_s2 = []
        for text in session2_texts:
            cribs_s2.extend(spy.extract_potential_cribs(text))
        # Should only extract from new text (not duplicate)
        assert len(cribs_s2) < len(cribs_s1) * 2, "Should skip duplicate from session 1"

        # Session 3: Should skip both duplicates, process new
        cribs_s3 = []
        for text in session3_texts:
            cribs_s3.extend(spy.extract_potential_cribs(text))
        assert len(cribs_s3) < len(cribs_s1) * 2, "Should skip duplicates from sessions 1 & 2"

        # Total unique content processed
        assert len(spy.processed_content_hashes) == 4, "Should track all 4 unique texts"
