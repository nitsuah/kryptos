"""Unit tests for src/scoring/fitness.py functions."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TestFitnessModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # import dynamically after possible sys.path modification above
        cls.fitness_mod = importlib.import_module("src.scoring.fitness")

    def test_load_ngram_data_missing(self):
        # missing path -> empty dict
        data = self.fitness_mod.load_ngram_data(None)
        self.assertEqual(data, {})
        data2 = self.fitness_mod.load_ngram_data("/non/existent/path.tsv")
        self.assertEqual(data2, {})

    def test_load_ngram_data_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as fh:
            fh.write("A 1.5\nB 2.0\nC\n")
            path = fh.name
        try:
            data = self.fitness_mod.load_ngram_data(path)
            self.assertIn("A", data)
            self.assertEqual(data.get("A"), 1.5)
            self.assertEqual(data.get("C"), 1.0)
        finally:
            os.unlink(path)

    def test_score_ngram_fallback(self):
        # when ngram_map is None or empty, returns proportional fallback
        s = "HELLO"
        v = self.fitness_mod._score_ngram(s, None)
        self.assertAlmostEqual(v, len(s) * 0.01)
        v2 = self.fitness_mod._score_ngram(s, {})
        self.assertAlmostEqual(v2, len(s) * 0.01)

    def test_compute_crib_bonus_counts(self):
        text = "ABCABCABC"
        bonus = self.fitness_mod.compute_crib_bonus(text, ["ABC"])
        # occurrences at 0,3,6 -> 3
        self.assertEqual(bonus, 3.0)
        self.assertEqual(self.fitness_mod.compute_crib_bonus(text, []), 0.0)

    def test_compute_clock_valid(self):
        # length divisible by 5 -> 1.0
        self.assertEqual(self.fitness_mod.compute_clock_valid("12345"), 1.0)
        self.assertEqual(self.fitness_mod.compute_clock_valid("1234"), 0.0)

    def test_score_candidate_uses_meta_and_weights(self):
        # Provide explicit meta values to ensure aggregation uses them
        meta = {"ngrams": {"A": 2.0}, "crib_bonus": 3.0, "clock_valid": 1.0}
        weights = {"ngram": 1.0, "crib": 0.5, "clock": 0.2}
        score = self.fitness_mod.score_candidate("AAA", meta, weights)
        # ngram score = sum(ngram_map.get(ch,0) for ch in text) -> 2.0 * 3 = 6.0
        expected = 6.0 * 1.0 + 3.0 * 0.5 + 1.0 * 0.2
        self.assertAlmostEqual(score, expected)

    def test_compute_meta_and_score_defaults(self):
        out = self.fitness_mod.compute_meta_and_score("XYZ", {"ngram": 1.0})
        self.assertIn("score", out)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
