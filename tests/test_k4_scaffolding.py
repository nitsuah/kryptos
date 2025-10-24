"""Scaffolding tests for K4 hypothesis modules.

Currently uses placeholders; real ciphertext for K4 not yet integrated.
"""

import logging
import os
import sys
import unittest

# Ensure root path for IDE resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestK4Scaffold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use canonical kryptos namespace directly
        from kryptos.k4 import (
            combined_plaintext_score,
            partitions_for_k4,
            slice_by_partition,
        )
        from kryptos.k4.substitution_solver import solve_substitution

        # Wrap as staticmethods so they don't receive 'self'
        cls.partitions_for_k4 = staticmethod(partitions_for_k4)  # type: ignore[arg-type]
        cls.slice_by_partition = staticmethod(slice_by_partition)  # type: ignore[arg-type]
        cls.combined_plaintext_score = staticmethod(combined_plaintext_score)  # type: ignore[arg-type]
        cls.solve_substitution = staticmethod(solve_substitution)  # type: ignore[arg-type]

    def test_partitions_generation(self):
        """Test generation of partitions for K4 segmentation."""
        parts = self.partitions_for_k4()
        self.assertTrue(len(parts) > 0)
        # Check all sum to presumed length 97
        for p in parts[:50]:
            self.assertEqual(sum(p), 97)

    def test_slice_by_partition(self):
        """Test slicing text by a given partition."""
        text = 'A' * 97
        part = (12, 12, 12, 12, 12, 12, 12, 13)  # sums to 97
        segs = self.slice_by_partition(text, part)
        self.assertEqual(len(segs), len(part))
        # ensure each segment length matches the partition sizes
        for s, expected in zip(segs, part, strict=True):
            self.assertEqual(len(s), expected)

    def test_scoring_basic(self):
        """Test basic plaintext scoring functionality."""
        score = self.combined_plaintext_score('THEAND')
        self.assertIsInstance(score, float)

    def test_substitution_solver_runs(self):
        plain, score, mapping = self.solve_substitution('ABCXYZ')
        self.assertIsInstance(plain, str)
        self.assertIsInstance(score, float)
        self.assertIsInstance(mapping, dict)

    def test_real_k4_ciphertext_structure(self):
        """Test that real K4 ciphertext fragment can be loaded and scored."""
        # K4 first 74 characters (before the "?" section)
        k4_fragment = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"

        # Verify structure
        self.assertEqual(len(k4_fragment), 74, "K4 first fragment should be 74 characters")
        self.assertTrue(k4_fragment.isalpha(), "K4 should be all alphabetic")
        self.assertTrue(k4_fragment.isupper(), "K4 should be all uppercase")

        # Test that it can be scored
        score = self.combined_plaintext_score(k4_fragment)
        self.assertIsInstance(score, float)

        # K4 ciphertext should score poorly (should be indistinguishable from random)
        # Below our 2σ threshold (-326.68)
        self.assertLess(
            score,
            -300.0,
            f"K4 ciphertext should score poorly (random-like), got {score:.2f}",
        )


if __name__ == '__main__':
    unittest.main()
