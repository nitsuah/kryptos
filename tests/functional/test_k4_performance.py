"""Performance guard tests for K4 pipeline."""

import os
import time
import unittest
from pathlib import Path

from kryptos.k4 import decrypt_best


def _running_in_container() -> bool:
    """Best-effort container detection for flaky micro-benchmark guards."""
    if Path("/.dockerenv").exists():
        return True
    cgroup_path = Path("/proc/1/cgroup")
    if cgroup_path.exists():
        try:
            content = cgroup_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        lowered = content.lower()
        return any(token in lowered for token in ("docker", "containerd", "kubepods", "podman"))
    return False


class TestK4Performance(unittest.TestCase):
    @unittest.skipIf(
        os.environ.get("PERF_DISABLE") == "1" or _running_in_container(),
        "Performance tests disabled (PERF_DISABLE=1 or container runtime)",
    )
    def test_small_composite_run_performance(self):
        """Test that a small composite pipeline run completes within acceptable time.

        This is a smoke test to catch major performance regressions.
        Uses a small limit to keep runtime reasonable.
        """
        # Small K4 ciphertext (full 97 chars)
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        # Very small limit for quick execution
        limit = 5
        start = time.perf_counter()
        result = decrypt_best(ciphertext, strategy="default", limit=limit, report=False)
        elapsed = time.perf_counter() - start
        # Assert basic result structure
        self.assertIsNotNone(result.plaintext)
        self.assertIsInstance(result.score, (int, float))
        self.assertIsInstance(result.candidates, list)
        self.assertGreater(len(result.candidates), 0, "Should return at least one candidate")
        # Performance guard: should complete in < 5 seconds on typical hardware
        # This is a generous threshold to avoid flakiness on slow CI
        max_seconds = 5.0
        self.assertLess(
            elapsed,
            max_seconds,
            f"Composite run took {elapsed:.2f}s, expected < {max_seconds}s. "
            f"This may indicate a performance regression.",
        )


if __name__ == "__main__":
    unittest.main()
