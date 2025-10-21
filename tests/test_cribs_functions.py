"""Tests for cribs utility functions."""
import unittest
from src.k4.cribs import normalize_cipher, annotate_cribs


class TestCribsFunctions(unittest.TestCase):
    def test_normalize_cipher(self):
        self.assertEqual(normalize_cipher("a-b C!"), "ABC")

    def test_annotate_cribs(self):
        ciphertext = "ABCDTESTEFGTESTXYZ"
        mapping = {"TEST": "TEST"}
        ann = annotate_cribs(ciphertext, mapping, one_based=True)
        self.assertEqual(len(ann), 1)
        entry = ann[0]  # type: ignore[assignment]
        self.assertTrue(entry['alignment_ok'])
        self.assertIn('expected_positions', entry)
        fp = entry['found_positions'] if isinstance(entry['found_positions'], list) else []
        self.assertTrue(len(fp) >= 1)


if __name__ == '__main__':
    unittest.main()
