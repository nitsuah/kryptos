"""Edge case tests for analysis module."""

import unittest

from kryptos.analysis import check_cribs, frequency_analysis


class TestAnalysisEdgeCases(unittest.TestCase):
    def test_frequency_analysis_empty(self):
        self.assertEqual(frequency_analysis(""), {})

    def test_check_cribs_none_found(self):
        self.assertEqual(check_cribs("ABCDEF", ["XYZ", "NOP"]), [])


if __name__ == '__main__':
    unittest.main()
