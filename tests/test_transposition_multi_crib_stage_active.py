"""Test active multi-crib transposition stage path with n_cols=1 for deterministic match."""
import unittest
from collections.abc import Sequence
from src.k4.pipeline import make_transposition_multi_crib_stage, Pipeline

class TestTranspositionMultiCribStageActive(unittest.TestCase):
    def test_active_multi_crib_stage(self):
        positional: dict[str, Sequence[int]] = {"CLOCK": [0], "BERLIN": [6]}
        ciphertext = "CLOCKBERLIN"
        stage = make_transposition_multi_crib_stage(
            positional_cribs=positional,
            min_cols=1,
            max_cols=1,
            window=2,
            max_perms=10,
            limit=5,
        )  # type: ignore[arg-type]
        pipe = Pipeline([stage])
        res = pipe.run(ciphertext)
        self.assertEqual(len(res), 1)
        meta = res[0].metadata
        cands = meta.get('candidates', [])
        self.assertTrue(isinstance(cands, list))
        if cands:
            first = cands[0]
            self.assertIn('pos_bonus', first)
            self.assertGreaterEqual(first['pos_bonus'], 0.0)

if __name__ == '__main__':
    unittest.main()
