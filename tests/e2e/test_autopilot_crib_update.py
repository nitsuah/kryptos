"""Test autopilot crib update integration."""

import json
import tempfile
import unittest
from pathlib import Path

from kryptos.autopilot import run_exchange


class TestAutopilotCribUpdate(unittest.TestCase):
    def setUp(self):
        """Set up temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_dir = self.temp_dir / "logs"
        self.log_dir.mkdir()
        self.spy_dir = self.temp_dir / "spy"
        self.spy_dir.mkdir()
        # Patch paths
        import kryptos.autopilot as ap
        import kryptos.spy.crib_store as cs

        self._orig_log_dir = ap.LOG_DIR
        self._orig_obs = cs.OBSERVATIONS_PATH
        self._orig_promoted = cs.PROMOTED_CRIBS_PATH
        ap.LOG_DIR = self.log_dir
        cs.OBSERVATIONS_PATH = self.spy_dir / "observations.jsonl"
        cs.PROMOTED_CRIBS_PATH = self.spy_dir / "promoted_cribs.txt"

    def tearDown(self):
        """Restore paths and clean up."""
        import kryptos.autopilot as ap
        import kryptos.spy.crib_store as cs

        ap.LOG_DIR = self._orig_log_dir
        cs.OBSERVATIONS_PATH = self._orig_obs
        cs.PROMOTED_CRIBS_PATH = self._orig_promoted
        # Clean up temp files
        for f in self.log_dir.glob("*"):
            f.unlink()
        self.log_dir.rmdir()
        for f in self.spy_dir.glob("*"):
            f.unlink()
        self.spy_dir.rmdir()
        self.temp_dir.rmdir()

    def test_exchange_logs_crib_update(self):
        """Test that run_exchange logs crib update event."""
        out_path = run_exchange(plan_text="test plan", autopilot=False)
        self.assertTrue(out_path.exists(), "Exchange log file should exist")
        # Read log entries
        with out_path.open("r", encoding="utf-8") as fh:
            lines = [json.loads(line) for line in fh if line.strip()]
        # Should have persona actions + crib update event
        events = [entry for entry in lines if entry.get("event") == "cribs_updated"]
        self.assertGreater(len(events), 0, "Should have at least one cribs_updated event")
        event = events[0]
        self.assertIn("cribs_total", event)
        self.assertIn("new", event)
        self.assertIsInstance(event["cribs_total"], int)
        self.assertIsInstance(event["new"], int)


if __name__ == "__main__":
    unittest.main()
