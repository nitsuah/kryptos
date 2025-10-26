"""Test autonomous K3-style columnar transposition solving.

Tests whether our SA solver can actually recover transposition permutations
without knowing the key. This validates the claim of "27.5% success rate" or
provides real measured capability.
"""

import random

from kryptos.k4.transposition_analysis import (
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    solve_columnar_permutation_simulated_annealing,
)


def test_k3_autonomous_period_5():
    """Test SA solver on period-5 transposition (baseline)."""
    # Known plaintext (English-like)
    plaintext = (
        "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISCAMETOTBESORTED"
        "THEFINALRESTINGPLACEWASINDEEDABEAUTIFULLOCATIONTOENDTHISWORK"
    )

    # Random permutation (period 5)
    period = 5
    true_permutation = [2, 4, 0, 3, 1]  # Scrambled column order

    # Apply transposition
    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

    # Try to recover permutation autonomously
    recovered_perm, score = solve_columnar_permutation_simulated_annealing(
        ciphertext,
        period,
        max_iterations=50000,
        initial_temp=50.0,
        cooling_rate=0.9995,
    )

    # Check if recovered correctly
    assert len(recovered_perm) == period, "Permutation length mismatch"

    # Decrypt with recovered permutation
    recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)

    # Success if recovered plaintext matches original (allowing for some variation)
    match_ratio = sum(1 for a, b in zip(recovered_text, plaintext) if a == b) / len(plaintext)

    # Log result
    print("\nK3 Period-5 Test (single run - probabilistic):")
    print(f"  True permutation:      {true_permutation}")
    print(f"  Recovered permutation: {recovered_perm}")
    print(f"  Score: {score:.4f}")
    print(f"  Match ratio: {match_ratio:.1%}")
    print(f"  Success: {'✓' if match_ratio > 0.9 else '✗'}")
    print(f"  Recovered text: {recovered_text[:80]}...")
    print("\n  NOTE: This is a single probabilistic run. See Monte Carlo test for success rate.")


def test_k3_autonomous_period_6():
    """Test SA solver on period-6 transposition."""
    plaintext = (
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        "ITWASWHATTHEYWANTEDTOREMEMBERANDTHEYWOULDNOTFORGETTHISMOMENT"
    )

    period = 6
    true_permutation = [3, 0, 5, 1, 4, 2]

    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

    recovered_perm, score = solve_columnar_permutation_simulated_annealing(
        ciphertext,
        period,
        max_iterations=50000,
    )

    recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
    match_ratio = sum(1 for a, b in zip(recovered_text, plaintext) if a == b) / len(plaintext)

    print("\nK3 Period-6 Test (single run - probabilistic):")
    print(f"  True permutation:      {true_permutation}")
    print(f"  Recovered permutation: {recovered_perm}")
    print(f"  Score: {score:.4f}")
    print(f"  Match ratio: {match_ratio:.1%}")
    print(f"  Success: {'✓' if match_ratio > 0.9 else '✗'}")
    print("\n  NOTE: This is a single probabilistic run. See Monte Carlo test for success rate.")


def test_k3_autonomous_period_7():
    """Test SA solver on period-7 transposition (harder)."""
    plaintext = (
        "VIRTUALLYINVISIBLEBYTHEIROWNMAKINGTHEYHADCREATEDTHEWORLDAROUND"
        "THEMANDTHEYWOULDLIVEINITTHROUGHOUTTHERESTOFTHEIREXISTENCENOW"
    )

    period = 7
    # Random permutation
    true_permutation = list(range(period))
    random.seed(42)
    random.shuffle(true_permutation)

    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

    recovered_perm, score = solve_columnar_permutation_simulated_annealing(
        ciphertext,
        period,
        max_iterations=100000,  # More iterations for harder case
        initial_temp=100.0,
    )

    recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
    match_ratio = sum(1 for a, b in zip(recovered_text, plaintext) if a == b) / len(plaintext)

    print("\nK3 Period-7 Test (single run - probabilistic):")
    print(f"  True permutation:      {true_permutation}")
    print(f"  Recovered permutation: {recovered_perm}")
    print(f"  Score: {score:.4f}")
    print(f"  Match ratio: {match_ratio:.1%}")
    print(f"  Success: {'✓' if match_ratio > 0.8 else '✗'}")
    print("\n  NOTE: Period 7 is harder. This is a single probabilistic run.")


def test_k3_monte_carlo_period_5(runs=10):
    """Monte Carlo test: Run period-5 recovery multiple times to get success rate.

    This validates the "27.5% success rate" claim from Phase 6 roadmap.
    """
    plaintext = (
        "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISCAMETOTBESORTED"
        "THEFINALRESTINGPLACEWASINDEEDABEAUTIFULLOCATIONTOENDTHISWORK"
    )

    period = 5
    successes = 0

    print(f"\nK3 Monte Carlo Test (period {period}, {runs} runs):")

    for run in range(runs):
        # Random permutation each run
        true_permutation = list(range(period))
        random.shuffle(true_permutation)

        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_permutation)

        recovered_perm, score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations=50000,
        )

        recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)
        match_ratio = sum(1 for a, b in zip(recovered_text, plaintext) if a == b) / len(plaintext)

        success = match_ratio > 0.9
        if success:
            successes += 1

        print(f"  Run {run+1}: {'✓' if success else '✗'} ({match_ratio:.1%} match)")

    success_rate = successes / runs
    print(f"\nSuccess rate: {success_rate:.1%} ({successes}/{runs})")

    # Document actual measured rate
    assert success_rate > 0, "SA solver never succeeded"

    # Warning if much lower than claimed 27.5%
    if success_rate < 0.2:
        print(f"WARNING: Success rate ({success_rate:.1%}) much lower than roadmap claim (27.5%)")
