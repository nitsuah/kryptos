"""Test letter_coverage on empty input."""

import unittest

from kryptos.k4.scoring import letter_coverage


class TestScoringLetterCoverageEmpty(unittest.TestCase):
    def test_letter_coverage_empty(self):
        self.assertEqual(letter_coverage(""), 0.0)


if __name__ == '__main__':
    unittest.main()
