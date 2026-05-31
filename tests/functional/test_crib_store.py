"""Tests for dynamic crib store."""

import tempfile
import unittest
from pathlib import Path

from kryptos.spy.crib_store import (
    CribObservation,
    load_observations,
    load_promoted_cribs,
    promote_cribs,
    save_observation,
)


class TestCribStore(unittest.TestCase):
    def setUp(self):
        """Create temporary directories for test isolation."""
        self.temp_dir = tempfile.mkdtemp()
        self.obs_path = Path(self.temp_dir) / "observations.jsonl"
        self.promoted_path = Path(self.temp_dir) / "promoted_cribs.txt"
        # Patch module paths
        import kryptos.spy.crib_store as cs

        self._orig_obs = cs.OBSERVATIONS_PATH
        self._orig_promoted = cs.PROMOTED_CRIBS_PATH
        cs.OBSERVATIONS_PATH = self.obs_path
        cs.PROMOTED_CRIBS_PATH = self.promoted_path

    def tearDown(self):
        """Restore original paths."""
        import kryptos.spy.crib_store as cs

        cs.OBSERVATIONS_PATH = self._orig_obs
        cs.PROMOTED_CRIBS_PATH = self._orig_promoted
        # Clean up temp files
        if self.obs_path.exists():
            self.obs_path.unlink()
        if self.promoted_path.exists():
            self.promoted_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_save_and_load_observation(self):
        """Test saving and loading observations."""
        save_observation("BERLIN", "run_001", 0.85)
        save_observation("CLOCK", "run_001", 0.90)
        obs = load_observations()
        self.assertEqual(len(obs), 2)
        self.assertEqual(obs[0].token, "BERLIN")
        self.assertEqual(obs[0].run_id, "run_001")
        self.assertAlmostEqual(obs[0].confidence, 0.85, places=2)

    def test_promote_cribs_requires_two_runs(self):
        """Cribs need >= 2 distinct runs to be promoted."""
        # Only one run
        new_obs = [
            CribObservation("BERLIN", "run_001", 0.85),
            CribObservation("BERLIN", "run_001", 0.90),
        ]
        promoted = promote_cribs(new_obs)
        self.assertEqual(len(promoted), 0, "Should not promote with only 1 run")
        # Add second run
        new_obs2 = [CribObservation("BERLIN", "run_002", 0.88)]
        promoted = promote_cribs(new_obs2)
        self.assertIn("BERLIN", promoted)
        self.assertEqual(promoted["BERLIN"], 2, "Should see 2 distinct runs")

    def test_promote_requires_min_confidence(self):
        """Low confidence observations don't promote."""
        new_obs = [
            CribObservation("LOWCONF", "run_001", 0.50),
            CribObservation("LOWCONF", "run_002", 0.55),
        ]
        promoted = promote_cribs(new_obs)
        self.assertEqual(len(promoted), 0, "Confidence < 0.8 should not promote")

    def test_promote_requires_valid_token(self):
        """Only valid tokens (A-Z, len>=3) promote."""
        new_obs = [
            CribObservation("AB", "run_001", 0.85),  # too short
            CribObservation("AB", "run_002", 0.85),
            CribObservation("BE3", "run_003", 0.85),  # has digit
            CribObservation("BE3", "run_004", 0.85),
        ]
        promoted = promote_cribs(new_obs)
        self.assertEqual(len(promoted), 0, "Invalid tokens should not promote")

    def test_load_promoted_cribs(self):
        """Test loading promoted cribs file."""
        # Manually create promoted cribs
        self.promoted_path.parent.mkdir(parents=True, exist_ok=True)
        self.promoted_path.write_text("BERLIN\t2\t0.875\nCLOCK\t3\t0.900\n")
        cribs = load_promoted_cribs()
        self.assertEqual(len(cribs), 2)
        self.assertIn("BERLIN", cribs)
        self.assertIn("CLOCK", cribs)

    def test_crib_file_size_limit(self):
        """Test that crib file respects size limit and keeps highest confidence."""
        import kryptos.spy.crib_store as cs

        # Set low limit for testing
        orig_limit = cs.MAX_CRIBS_SIZE_BYTES
        cs.MAX_CRIBS_SIZE_BYTES = 300  # 300 bytes (fits ~10-15 entries of ~20 bytes each)
        try:
            # Create many observations with varying confidence (use letters A-Z cycling)
            obs = []
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for i in range(30):
                # Generate token like TOKENABC, TOKENBCD, etc.
                suffix = letters[i % 26] + letters[(i + 1) % 26] + letters[(i + 2) % 26]
                token = f"TOKEN{suffix}"  # All letters, no digits
                # Higher index = higher confidence
                conf = 0.85 + i * 0.005
                obs.append(CribObservation(token, "run_001", conf))
                obs.append(CribObservation(token, "run_002", conf))
            promote_cribs(obs)
            # File should exist and be within limit
            self.assertTrue(self.promoted_path.exists(), "Promoted cribs file should exist")
            content = self.promoted_path.read_text()
            self.assertGreater(len(content), 0, "File should have content")
            size = self.promoted_path.stat().st_size
            # Allow some margin for line endings
            self.assertLessEqual(size, 350, "File should be near size limit")
            # Verify cribs were saved
            cribs = load_promoted_cribs()
            self.assertGreater(len(cribs), 0, "Should keep at least one crib")
            self.assertLess(len(cribs), 30, "Should have trimmed entries to fit limit")
        finally:
            cs.MAX_CRIBS_SIZE_BYTES = orig_limit


if __name__ == "__main__":
    unittest.main()
