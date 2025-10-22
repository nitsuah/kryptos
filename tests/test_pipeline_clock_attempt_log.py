"""Test get_clock_attempt_log clear functionality after berlin clock stage run."""

import unittest

from src.k4.pipeline import Pipeline, get_clock_attempt_log, make_berlin_clock_stage


class TestPipelineClockAttemptLog(unittest.TestCase):
    def test_clock_attempt_log_clear(self):
        stage = make_berlin_clock_stage(step_seconds=86400, limit=2)  # single shift sequence (start/end of day)
        pipe = Pipeline([stage])
        pipe.run("OBKRUOXOGHULB")
        attempts = get_clock_attempt_log(clear=False)
        self.assertTrue(isinstance(attempts, list))
        cleared = get_clock_attempt_log(clear=True)
        self.assertTrue(len(attempts) >= len(cleared))
        self.assertEqual(get_clock_attempt_log(clear=False), [])


if __name__ == '__main__':
    unittest.main()
