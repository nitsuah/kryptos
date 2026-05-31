"""Tests for SPY agent pattern recognition."""

import unittest

from kryptos.agents.spy import SpyAgent, quick_spy_analysis, spy_report


class TestSpyAgent(unittest.TestCase):
    def test_spy_detects_crib_match(self):
        """SPY should detect exact crib matches."""
        plaintext = "THEBERLINCLOCKISHERE"
        spy = SpyAgent(cribs=['BERLIN', 'CLOCK'])

        analysis = spy.analyze_candidate(plaintext)

        crib_matches = [i for i in analysis['insights'] if i.category == 'crib']
        self.assertGreater(len(crib_matches), 0, "Should detect BERLIN and/or CLOCK")

        # Check for BERLIN
        berlin_found = any('BERLIN' in i.description for i in crib_matches)
        self.assertTrue(berlin_found, "Should find BERLIN crib")

    def test_spy_detects_repeats(self):
        """SPY should detect repeating substrings."""
        # ABC repeats 3 times
        plaintext = "ABCDEFABCGHIABCJKL"
        spy = SpyAgent()

        analysis = spy.analyze_candidate(plaintext)

        repeat_insights = [i for i in analysis['insights'] if i.category == 'repeat']
        self.assertGreater(len(repeat_insights), 0, "Should detect ABC repeating")

    def test_spy_detects_palindromes(self):
        """SPY should detect palindromic patterns."""
        plaintext = "ABCDEFGHIHGFEDCBA"
        spy = SpyAgent()

        analysis = spy.analyze_candidate(plaintext)

        palindrome_insights = [i for i in analysis['insights'] if i.category == 'palindrome']
        self.assertGreater(len(palindrome_insights), 0, "Should detect palindrome")

    def test_spy_detects_common_words(self):
        """SPY should detect common English words."""
        plaintext = "THEANDFORALLOFUSWASHERE"
        spy = SpyAgent()

        analysis = spy.analyze_candidate(plaintext)

        word_insights = [i for i in analysis['insights'] if i.category == 'words']
        self.assertGreater(len(word_insights), 0, "Should detect common words (THE, AND, FOR)")

    def test_spy_pattern_score_higher_for_structured_text(self):
        """Structured text with patterns should score higher than random."""
        structured = "THEBERLINCLOCKTHEBERLINCLOCKTHEBERLIN"
        random_text = "XQZVBKJWPMTHGLFDNRSCYXQZVBKJWPMTHGL"

        spy = SpyAgent(cribs=['BERLIN', 'CLOCK'])

        structured_analysis = spy.analyze_candidate(structured)
        random_analysis = spy.analyze_candidate(random_text)

        self.assertGreater(
            structured_analysis['pattern_score'],
            random_analysis['pattern_score'],
            "Structured text should have higher pattern score",
        )

    def test_spy_detects_anagrams(self):
        """SPY should detect anagrams of cribs."""
        # BERLIN anagram: LIBERN
        plaintext = "THELIBERNWASHERE"
        spy = SpyAgent(cribs=['BERLIN'])

        analysis = spy.analyze_candidate(plaintext)

        anagram_insights = [i for i in analysis['insights'] if i.category == 'anagram']
        self.assertGreater(len(anagram_insights), 0, "Should detect BERLIN anagram (LIBERN)")

    def test_spy_ranks_candidates(self):
        """SPY should rank candidates by pattern quality."""
        candidates = [
            {'id': '1', 'plaintext': 'XQZVBKJWPMTHGLFDNRSC'},  # Random
            {'id': '2', 'plaintext': 'THEBERLINCLOCKISHERE'},  # Has cribs
            {'id': '3', 'plaintext': 'ABCABCABCABCABCABCAB'},  # Has repeats
        ]

        spy = SpyAgent(cribs=['BERLIN', 'CLOCK'])
        ranked = spy.rank_candidates(candidates)

        # Candidate 2 or 3 should rank first (both have strong patterns)
        self.assertIn(ranked[0]['id'], ['2', '3'], "Patterned candidates should rank above random")

        # Random candidate should rank last
        self.assertEqual(ranked[2]['id'], '1', "Random text should rank last")

        # Top candidate should have positive pattern score
        self.assertGreater(
            ranked[0]['pattern_score'],
            ranked[2]['pattern_score'],
            "Top candidate should outscore random",
        )

    def test_quick_spy_analysis_works(self):
        """Quick analysis function should work."""
        plaintext = "THEBERLINCLOCKISHERE"
        analysis = quick_spy_analysis(plaintext, cribs=['BERLIN'])

        self.assertIn('insights', analysis)
        self.assertIn('pattern_score', analysis)
        self.assertGreater(len(analysis['insights']), 0)

    def test_spy_report_generates_readable_output(self):
        """SPY report should generate human-readable output."""
        plaintext = "THEBERLINCLOCKISHERE"
        report = spy_report(plaintext, cribs=['BERLIN', 'CLOCK'])

        self.assertIn('SPY AGENT', report)
        self.assertIn('BERLIN', report)
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 100, "Report should be substantive")

    def test_spy_detects_frequency_anomalies(self):
        """SPY should detect unusual frequency patterns."""
        # Lots of E's
        anomalous = "EEEEETHEREWASEEEEEE"
        spy = SpyAgent()

        analysis = spy.analyze_candidate(anomalous)

        freq_insights = [i for i in analysis['insights'] if i.category == 'frequency_anomaly']
        self.assertGreater(len(freq_insights), 0, "Should detect E frequency anomaly")


if __name__ == '__main__':
    unittest.main()
