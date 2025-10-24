"""Test crib-aware scoring integration."""

import tempfile
import unittest
from pathlib import Path

from kryptos.k4.scoring import crib_bonus
from kryptos.spy.crib_store import CribObservation, promote_cribs


class TestCribAwareScoring(unittest.TestCase):
    def setUp(self):
        """Set up temporary paths for promoted cribs."""
        self.temp_dir = tempfile.mkdtemp()
        self.obs_path = Path(self.temp_dir) / "observations.jsonl"
        self.promoted_path = Path(self.temp_dir) / "promoted_cribs.txt"
        # Patch paths
        import kryptos.spy.crib_store as cs

        self._orig_obs = cs.OBSERVATIONS_PATH
        self._orig_promoted = cs.PROMOTED_CRIBS_PATH
        cs.OBSERVATIONS_PATH = self.obs_path
        cs.PROMOTED_CRIBS_PATH = self.promoted_path
        # Clear scoring cache
        import kryptos.k4.scoring as scoring

        scoring._promoted_cribs_cache.clear()

    def tearDown(self):
        """Restore original paths."""
        import kryptos.k4.scoring as scoring
        import kryptos.spy.crib_store as cs

        cs.OBSERVATIONS_PATH = self._orig_obs
        cs.PROMOTED_CRIBS_PATH = self._orig_promoted
        scoring._promoted_cribs_cache.clear()
        # Clean up
        if self.obs_path.exists():
            self.obs_path.unlink()
        if self.promoted_path.exists():
            self.promoted_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_promoted_crib_increases_score(self):
        """Test that candidates with promoted cribs score higher."""
        # Baseline: text without promoted crib
        text_without = "THEQUICKBROWNFOXJUMPS"
        score_without = crib_bonus(text_without)
        # Promote a new crib
        obs = [
            CribObservation("FOX", "run_001", 0.85),
            CribObservation("FOX", "run_002", 0.90),
        ]
        promote_cribs(obs)
        # Clear cache so scoring picks up the new promoted crib
        import kryptos.k4.scoring as scoring

        scoring._promoted_cribs_cache.clear()
        # Text with promoted crib
        text_with = "THEQUICKBROWNFOXJUMPS"
        score_with = crib_bonus(text_with)
        # Score should be higher due to promoted crib
        self.assertGreater(
            score_with,
            score_without,
            f"Promoted crib should increase score: {score_with} > {score_without}",
        )

    def test_candidate_ranking_with_promoted_crib(self):
        """Test that candidates are ranked correctly with promoted cribs."""
        # Promote a distinctive crib
        obs = [
            CribObservation("QUANTUM", "run_001", 0.85),
            CribObservation("QUANTUM", "run_002", 0.90),
        ]
        promote_cribs(obs)
        import kryptos.k4.scoring as scoring

        scoring._promoted_cribs_cache.clear()
        # Candidate with promoted crib
        candidate_a = "THEQUANTUMFIELDTHEORY"
        # Candidate without
        candidate_b = "THECLASSICALPHYSICSMODEL"
        score_a = crib_bonus(candidate_a)
        score_b = crib_bonus(candidate_b)
        # Candidate A should score higher
        self.assertGreater(score_a, score_b, "Candidate with promoted crib should rank higher")


if __name__ == "__main__":
    unittest.main()
