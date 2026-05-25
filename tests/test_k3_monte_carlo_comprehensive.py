"""Comprehensive Monte Carlo validation of K3-style transposition solving.

Validates actual success rates vs. roadmap claims across multiple periods.
"""

import os
import random

import pytest

from kryptos.k4.transposition_analysis import (
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    solve_columnar_permutation_simulated_annealing,
)
from kryptos.k4.solver_config import make_ci_solver_config

if os.getenv("KRYPTOS_RUN_SLOW_MONTE_CARLO") != "1":
    pytest.skip("Set KRYPTOS_RUN_SLOW_MONTE_CARLO=1 to run this slow module", allow_module_level=True)


@pytest.mark.slow
def test_k3_monte_carlo_period_5_50runs():
    """50-run Monte Carlo for period 5 to get accurate success rate."""
    plaintext = (
        "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISCAMETOTBESORTED"
        "THEFINALRESTINGPLACEWASINDEEDABEAUTIFULLOCATIONTOENDTHISWORK"
    )

    period = 5
    runs = 50
    successes = 0

    print(f"\n{'='*70}")
    print(f"K3 Monte Carlo: Period {period}, {runs} runs")
    print(f"{'='*70}")

    for run in range(runs):
        # Random permutation each run
        perm_rng = random.Random(1000 + run)
        true_permutation = list(range(period))
        perm_rng.shuffle(true_permutation)

        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

        recovered_perm, score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations=50000,
            config=make_ci_solver_config(seed=2000 + run),
        )

        recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
        match_ratio = sum(1 for a, b in zip(recovered_text, plaintext, strict=True) if a == b) / len(plaintext)

        success = match_ratio > 0.9
        if success:
            successes += 1

        symbol = '✓' if success else '✗'
        print(f"  Run {run+1:2d}: {symbol} ({match_ratio:5.1%} match, score={score:.4f})")

    success_rate = successes / runs
    print(f"\n{'='*70}")
    print(f"SUCCESS RATE: {success_rate:.1%} ({successes}/{runs})")
    print("Roadmap claim: 27.5%")
    print(f"Measured vs claimed: {success_rate/0.275:.1f}x better" if success_rate > 0.275 else "Worse than claimed")
    print(f"{'='*70}")

    # Must achieve at least 20% to validate any autonomous capability
    assert success_rate > 0.2, f"Success rate too low: {success_rate:.1%}"


@pytest.mark.slow
def test_k3_monte_carlo_period_6_30runs():
    """30-run Monte Carlo for period 6 (harder)."""
    plaintext = (
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        "ITWASWHATTHEYWANTEDTOREMEMBERANDTHEYWOULDNOTFORGETTHISMOMENT"
    )

    period = 6
    runs = 30
    successes = 0

    print(f"\n{'='*70}")
    print(f"K3 Monte Carlo: Period {period}, {runs} runs")
    print(f"{'='*70}")

    for run in range(runs):
        perm_rng = random.Random(3000 + run)
        true_permutation = list(range(period))
        perm_rng.shuffle(true_permutation)

        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

        recovered_perm, score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations=50000,
            config=make_ci_solver_config(seed=4000 + run),
        )

        recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
        match_ratio = sum(1 for a, b in zip(recovered_text, plaintext, strict=True) if a == b) / len(plaintext)

        success = match_ratio > 0.9
        if success:
            successes += 1

        symbol = '✓' if success else '✗'
        print(f"  Run {run+1:2d}: {symbol} ({match_ratio:5.1%} match, score={score:.4f})")

    success_rate = successes / runs
    print(f"\n{'='*70}")
    print(f"SUCCESS RATE: {success_rate:.1%} ({successes}/{runs})")
    print("Note: Period 6 is harder (720 possible permutations vs 120 for period 5)")
    print(f"{'='*70}")

    # Period 6 should maintain non-trivial autonomous recovery capability.
    assert success_rate >= 0.2, f"Period-6 success rate too low: {success_rate:.1%}"


@pytest.mark.slow
def test_k3_monte_carlo_period_7_20runs():
    """20-run Monte Carlo for period 7 (hardest)."""
    plaintext = (
        "VIRTUALLYINVISIBLEBYTHEIROWNMAKINGTHEYHADCREATEDTHEWORLDAROUND"
        "THEMANDTHEYWOULDLIVEINITTHROUGHOUTTHERESTOFTHEIREXISTENCENOW"
    )

    period = 7
    runs = 20
    successes = 0

    print(f"\n{'='*70}")
    print(f"K3 Monte Carlo: Period {period}, {runs} runs")
    print(f"{'='*70}")

    for run in range(runs):
        perm_rng = random.Random(5000 + run)
        true_permutation = list(range(period))
        perm_rng.shuffle(true_permutation)

        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

        recovered_perm, score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations=100000,  # More iterations for period 7
            initial_temp=100.0,
            config=make_ci_solver_config(seed=6000 + run),
        )

        recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
        match_ratio = sum(1 for a, b in zip(recovered_text, plaintext, strict=True) if a == b) / len(plaintext)

        success = match_ratio > 0.8  # Lower threshold for period 7
        if success:
            successes += 1

        symbol = '✓' if success else '✗'
        print(f"  Run {run+1:2d}: {symbol} ({match_ratio:5.1%} match, score={score:.4f})")

    success_rate = successes / runs
    print(f"\n{'='*70}")
    print(f"SUCCESS RATE: {success_rate:.1%} ({successes}/{runs})")
    print("Note: Period 7 is hardest (5040 possible permutations)")
    print("Note: Using >80% match threshold for period 7")
    print(f"{'='*70}")

    # Period 7 is harder but should still exceed a minimal useful hit-rate.
    assert success_rate >= 0.1, f"Period-7 success rate too low: {success_rate:.1%}"
