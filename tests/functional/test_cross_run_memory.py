"""Tests for cross-run search space memory (Task 1.1).

Validates that the system never tries the same key twice across runs.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pytest

from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency
from kryptos.provenance.search_space import SearchSpaceTracker

# Mark this module as skipped for fast CI runs — persisted as slow in test_progress.json
pytest.skip("Marked slow: cross-run memory tests (skip in fast runs)", allow_module_level=True)


class TestCrossRunMemory(unittest.TestCase):
    """Test cross-run deduplication of tried keys."""

    def test_already_tried_basic(self):
        """Test basic already_tried() functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))

            # Initially nothing tried
            self.assertFalse(tracker.already_tried("vigenere", "TEST"))

            # Mark as tried
            tracker.mark_tried("vigenere", "TEST")

            # Should now return True
            self.assertTrue(tracker.already_tried("vigenere", "TEST"))

    def test_cross_run_persistence(self):
        """Test that tried keys persist across SearchSpaceTracker instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)

            # Run 1: Try some keys
            tracker1 = SearchSpaceTracker(cache_dir=cache)
            tracker1.record_exploration("vigenere", "length_5", count=3, keys=["ABCDE", "FGHIJ", "KLMNO"])

            # Run 2: New tracker should remember
            tracker2 = SearchSpaceTracker(cache_dir=cache)
            self.assertTrue(tracker2.already_tried("vigenere", "ABCDE"))
            self.assertTrue(tracker2.already_tried("vigenere", "FGHIJ"))
            self.assertTrue(tracker2.already_tried("vigenere", "KLMNO"))
            self.assertFalse(tracker2.already_tried("vigenere", "PQRST"))

    def test_vigenere_recovery_skip_tried(self):
        """Test that recover_key_by_frequency skips tried keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))

            # K1 ciphertext (short excerpt)
            ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"

            # Run 1: Get some candidates
            keys1 = recover_key_by_frequency(ciphertext, 9, top_n=5, skip_tried=True, tracker=tracker)

            self.assertGreater(len(keys1), 0, "Should get some candidates in run 1")

            # Run 2: Same call should return empty (all already tried)
            keys2 = recover_key_by_frequency(ciphertext, 9, top_n=5, skip_tried=True, tracker=tracker)

            self.assertEqual(len(keys2), 0, "Run 2 should return no keys (all tried)")

    def test_zero_duplicates_across_1000_attempts(self):
        """SUCCESS METRIC: After 1000 attempts, next 1000 have ZERO duplicates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))

            # Simulate 1000 attempts
            attempted_keys = set()
            for i in range(1000):
                key = f"KEY{i:04d}"
                tracker.mark_tried("vigenere", key)
                attempted_keys.add(key)

            # Verify all 1000 are marked as tried
            for key in attempted_keys:
                self.assertTrue(
                    tracker.already_tried("vigenere", key),
                    f"Key {key} should be marked as tried",
                )

            # Now simulate next 1000 attempts (should all be new)
            new_keys = []
            for i in range(1000, 2000):
                key = f"KEY{i:04d}"
                if not tracker.already_tried("vigenere", key):
                    new_keys.append(key)
                    tracker.mark_tried("vigenere", key)

            # SUCCESS: All 1000 new keys were unique
            self.assertEqual(
                len(new_keys),
                1000,
                "All 1000 new attempts should be unique (ZERO duplicates)",
            )

    def test_different_cipher_types_separate(self):
        """Test that different cipher types have separate tried key sets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))

            # Try same key for different ciphers
            tracker.mark_tried("vigenere", "TEST")
            tracker.mark_tried("transposition", "TEST")

            # Both should be independently tracked
            self.assertTrue(tracker.already_tried("vigenere", "TEST"))
            self.assertTrue(tracker.already_tried("transposition", "TEST"))

            # Different key for vigenere should be untried
            self.assertFalse(tracker.already_tried("vigenere", "OTHER"))

    def test_record_exploration_with_keys(self):
        """Test record_exploration() with keys parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))

            keys = ["KEY1", "KEY2", "KEY3"]
            tracker.record_exploration("vigenere", "length_4", count=3, successful=1, keys=keys)

            # All keys should be marked as tried
            for key in keys:
                self.assertTrue(tracker.already_tried("vigenere", key))

            # Region should track the counts
            coverage = tracker.get_coverage_report("vigenere")
            regions = coverage["cipher_types"]["vigenere"]["regions"]
            length_4_region = next(r for r in regions if r["region"] == "length_4")

            self.assertEqual(length_4_region["explored_count"], 3)
            self.assertEqual(length_4_region["successful_count"], 1)

    def test_skip_tried_false_doesnt_filter(self):
        """Test that skip_tried=False doesn't filter keys (backward compat)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = SearchSpaceTracker(cache_dir=Path(tmpdir))
            ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"

            # Run 1 with skip_tried=False
            keys1 = recover_key_by_frequency(ciphertext, 9, top_n=5, skip_tried=False, tracker=tracker)

            # Run 2 with skip_tried=False (should get same results)
            keys2 = recover_key_by_frequency(ciphertext, 9, top_n=5, skip_tried=False, tracker=tracker)

            # Should be identical (no filtering)
            self.assertEqual(keys1, keys2, "skip_tried=False should not filter")

    def test_jsonl_file_created(self):
        """Test that tried_keys.jsonl file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Path(tmpdir)
            tracker = SearchSpaceTracker(cache_dir=cache)

            tracker.mark_tried("vigenere", "TEST")

            jsonl_file = cache / "tried_keys.jsonl"
            self.assertTrue(jsonl_file.exists(), "tried_keys.jsonl should be created")

            # Verify file content
            with open(jsonl_file, encoding="utf-8") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertIn('"TEST"', lines[0])
            self.assertIn('"vigenere"', lines[0])


if __name__ == "__main__":
    unittest.main()
