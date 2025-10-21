"""Tests for PipelineExecutor._prune logic and berlin clock pattern bonus integration.

Focus: ensure crib bonus threshold admits extra candidates beyond top_n and
pattern bonus reflected in baseline_stats metrics.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure local src path importable when running tests directly
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.k4.executor import PipelineConfig, PipelineExecutor  # noqa: E402
from src.k4.pipeline import Stage  # noqa: E402
from src.k4.scoring import baseline_stats  # noqa: E402


class DummyStage(Stage):
    pass


class TestExecutorPruningAndPattern(unittest.TestCase):
    def _make_executor(self, top_n=2, cap=6, bonus_thresh=5.0):
        cfg = PipelineConfig(
            ordering=[],  # no run needed for pruning unit tests
            pruning_top_n=top_n,
            candidate_cap_per_stage=cap,
            crib_bonus_threshold=bonus_thresh,
        )
        return PipelineExecutor(cfg)

    def test_prune_includes_bonus_candidates(self):
        ex = self._make_executor(top_n=2, cap=6, bonus_thresh=5.0)
        # Construct candidates: scores descending; one outside top_n with crib_bonus above threshold
        candidates = [
            {'text': 'AAAA', 'score': 100.0, 'crib_bonus': 0.0},
            {'text': 'BBBB', 'score': 90.0, 'crib_bonus': 0.0},
            {'text': 'CLOCK BERLIN', 'score': 10.0, 'crib_bonus': 6.0},  # should be kept despite low score
            {'text': 'CCCC', 'score': 80.0, 'crib_bonus': 0.0},
        ]
        pruned = ex._prune(candidates)  # intentional internal access for unit isolation
        texts = [c['text'] for c in pruned]
        # top_n: AAAA, BBBB + bonus candidate 'CLOCK BERLIN'
        self.assertIn('CLOCK BERLIN', texts)
        self.assertEqual(texts[0], 'AAAA')
        self.assertEqual(texts[1], 'BBBB')

    def test_prune_caps_final_size(self):
        ex = self._make_executor(top_n=3, cap=4, bonus_thresh=5.0)
        candidates = [{'text': f'T{i}', 'score': 100 - i} for i in range(10)]
        pruned = ex._prune(candidates)  # intentional internal access for unit isolation
        self.assertLessEqual(len(pruned), 4)

    def test_pattern_bonus_metric_present(self):
        stats = baseline_stats('BERLIN CLOCK')
        # pattern bonus should be 1.0 (berlin before clock) => float 1.0
        self.assertEqual(stats.get('berlin_clock_pattern_bonus'), 1.0)
        stats2 = baseline_stats('CLOCK BERLIN')
        # ordering inverted => bonus 0.0
        self.assertEqual(stats2.get('berlin_clock_pattern_bonus'), 0.0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
