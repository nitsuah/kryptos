"""K1/K2 Vigenère key-recovery stress suite (Phase 4: Validation & hardening).

Runs `kryptos.k4.vigenere_stress_tests.run_k1_k2_stress_suite` across the three
dimensions flagged as untested in `docs/analysis/K1_K2_VALIDATION_RESULTS.md`
("Consider Stress Testing"): noise, wrong key length, and partial ciphertext.

Each `recover_key_by_frequency` call costs ~5-7s regardless of input size (the
500k-candidate heap cap dominates), and the full suite makes 34 such calls
(16 noise + 10 key-length + 8 partial across K1+K2), so this is gated behind
KRYPTOS_RUN_SLOW_MONTE_CARLO like the other Monte Carlo e2e tests.
"""

import os

import pytest

from kryptos.k4.vigenere_stress_tests import K1_KEY, K2_KEY, run_k1_k2_stress_suite

if os.getenv("KRYPTOS_RUN_SLOW_MONTE_CARLO") != "1":
    pytest.skip(
        "Set KRYPTOS_RUN_SLOW_MONTE_CARLO=1 to run this slow module",
        allow_module_level=True,
    )


@pytest.mark.slow
def test_k1_k2_stress_suite():
    """Empirical results with seed=42 (`artifacts/k1_k2_stress_tests.json`):

    - **Noise**: K2 (367-char ciphertext) recovers ABSCISSA at all 8 trials
      (noise rates 0.0/0.05/0.10/0.20), with plaintext match ratio degrading
      gracefully from 1.0 to ~0.76 as noise increases. K1 (63-char ciphertext)
      only recovers PALIMPSEST at noise rates 0.0 and 0.05 (4/8 trials);
      at 10%/20% noise the recovered key is wrong and plaintext match ratio
      collapses to ~0.2-0.37.
    - **Wrong key length**: for both K1 and K2, only the true key length
      yields the correct key in the top-N candidates with a perfect
      plaintext match; all four off-by-(-2..+2) lengths fail for both.
    - **Partial ciphertext**: K2 recovers ABSCISSA exactly down to 25%
      (91 chars) of its ciphertext. K1 only recovers PALIMPSEST at 100%
      (63 chars); 75%/50%/25% truncations all fail.
    """
    summary = run_k1_k2_stress_suite(results_path="artifacts/k1_k2_stress_tests.json")
    k1 = summary["results"]["K1"]
    k2 = summary["results"]["K2"]

    # --- Sanity baseline: zero noise / full ciphertext always recovers the true key ---
    for section in (k1, k2):
        zero_noise_runs = [r for r in section["noise"] if r["noise_rate"] == 0.0]
        assert all(r["key_match"] and r["plaintext_match_ratio"] == 1.0 for r in zero_noise_runs)

        full_partial = next(r for r in section["partial_ciphertext"] if r["fraction"] == 1.0)
        assert full_partial["key_match"] and full_partial["plaintext_match_ratio"] == 1.0

    # --- Wrong key length: correct length always succeeds, all others always fail ---
    for section, key in ((k1, K1_KEY), (k2, K2_KEY)):
        for run in section["key_length"]:
            if run["key_length"] == len(key):
                assert run["correct_key_in_top"] and run["plaintext_match_ratio"] == 1.0
            else:
                assert not run["correct_key_in_top"]

    # --- K2: long ciphertext gives enough signal to survive noise and truncation ---
    assert all(r["key_match"] for r in k2["noise"])
    assert all(r["key_match"] and r["plaintext_match_ratio"] == 1.0 for r in k2["partial_ciphertext"])

    # --- K1: short ciphertext is fragile -- only low noise / full length recover the key ---
    k1_noise_success = sum(1 for r in k1["noise"] if r["key_match"])
    assert k1_noise_success == 4
    assert all(r["key_match"] for r in k1["noise"] if r["noise_rate"] <= 0.05)
    assert not any(r["key_match"] for r in k1["noise"] if r["noise_rate"] >= 0.10)

    k1_partial_success = [r["fraction"] for r in k1["partial_ciphertext"] if r["key_match"]]
    assert k1_partial_success == [1.0]
