"""Tests for diversified parallel hill variant execution in PipelineExecutor."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.k4.executor import PipelineConfig, PipelineExecutor  # noqa: E402
from src.k4.pipeline import make_hill_constraint_stage  # noqa: E402


class TestParallelHillVariants(unittest.TestCase):
    def test_variant_metadata_presence_and_diversity(self):
        hill_stage = make_hill_constraint_stage(name='hill', prune_3x3=True, partial_len=40, partial_min=-900.0)
        cfg = PipelineConfig(
            ordering=[hill_stage],
            parallel_hill_variants=3,  # request three variants
        )
        ex = PipelineExecutor(cfg)
        # Directly invoke parallel hill via getattr to avoid protected-member lint
        result = ex._run_parallel_hill(hill_stage, 'OBKRUOXOGHULBSOLIFB')
        variants_any = result.metadata.get('parallel_variants')
        self.assertIsNotNone(variants_any)
        self.assertIsInstance(variants_any, list)
        variants: list[dict] = variants_any  # type: ignore[assignment]
        self.assertEqual(len(variants), 3)
        partial_lens = {v.get('partial_len') for v in variants}
        self.assertGreaterEqual(len(partial_lens), 2)
        self.assertTrue(all('score' in v for v in variants))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
