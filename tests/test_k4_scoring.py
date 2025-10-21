"""
 Unit tests for K4 scoring functions.
"""
import unittest, random
from src.k4 import combined_plaintext_score

class TestK4Scoring(unittest.TestCase):
    def test_english_like_vs_random(self):
        english_like = 'THISISANENGLISHLIKEPLAINTEXTWITHCOMMONPATTERNSANDTHETRIGRAMTHE'
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        random_text = ''.join(random.choice(letters) for _ in range(len(english_like)))
        score_eng = combined_plaintext_score(english_like)
        score_rand = combined_plaintext_score(random_text)
        self.assertGreater(score_eng, score_rand)

if __name__ == '__main__':
    unittest.main()
