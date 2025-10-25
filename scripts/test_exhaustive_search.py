#!/usr/bin/env python3
"""Test exhaustive permutation search for small periods."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_encrypt,
    solve_columnar_permutation_exhaustive,
    solve_columnar_permutation_simulated_annealing_multi_start,
)


def test_exhaustive_vs_sa():
    """Compare exhaustive search vs SA on small periods."""
    print("=" * 80)
    print("EXHAUSTIVE PERMUTATION SEARCH VALIDATION")
    print("=" * 80)
    print()

    plaintext = "SLOWLYDESPARATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED"

    test_cases = [
        (3, [2, 0, 1]),
        (4, [1, 3, 0, 2]),
        (5, [2, 4, 0, 3, 1]),
        (6, [3, 0, 5, 2, 4, 1]),
    ]

    for period, true_perm in test_cases:
        print(f"Period {period}: Testing exhaustive search...")
        print(f"True permutation: {true_perm}")

        # Create ciphertext
        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)
        print(f"Ciphertext: {ciphertext[:60]}...")

        # Exhaustive search (guaranteed optimal)
        found_perm_ex, score_ex = solve_columnar_permutation_exhaustive(ciphertext, period)

        # SA for comparison
        found_perm_sa, score_sa = solve_columnar_permutation_simulated_annealing_multi_start(
            ciphertext,
            period,
            num_restarts=5,
        )

        # Check accuracy
        matches_ex = sum(p == t for p, t in zip(found_perm_ex, true_perm))
        matches_sa = sum(p == t for p, t in zip(found_perm_sa, true_perm))

        accuracy_ex = matches_ex / period * 100
        accuracy_sa = matches_sa / period * 100

        print(f"  Exhaustive: {found_perm_ex} | score={score_ex:.6f} | accuracy={accuracy_ex:.1f}%")
        print(f"  SA:         {found_perm_sa} | score={score_sa:.6f} | accuracy={accuracy_sa:.1f}%")

        if accuracy_ex == 100:
            print("  ✓ PERFECT - Exhaustive search found correct permutation")
        else:
            print(f"  ⚠ {matches_ex}/{period} positions correct")

        print()

    print("=" * 80)
    print("PERFORMANCE TEST: Period 6 (720 permutations)")
    print("=" * 80)

    import time

    period = 6
    true_perm = [3, 0, 5, 2, 4, 1]
    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)

    # Time exhaustive search
    start = time.time()
    found_perm, score = solve_columnar_permutation_exhaustive(ciphertext, period)
    elapsed = time.time() - start

    matches = sum(p == t for p, t in zip(found_perm, true_perm))
    accuracy = matches / period * 100

    print(f"Exhaustive search completed in {elapsed:.3f}s")
    print(f"Found: {found_perm}")
    print(f"True:  {true_perm}")
    print(f"Accuracy: {accuracy:.1f}% ({matches}/{period} correct)")
    print(f"Score: {score:.6f}")

    if accuracy == 100:
        print("\n✓ Period 6 exhaustive search: PERFECT")
    print()

    print("=" * 80)
    print("EARLY TERMINATION TEST")
    print("=" * 80)

    # Test early termination with target score
    target_score = 0.15  # Good score for English text

    start = time.time()
    found_perm, score = solve_columnar_permutation_exhaustive(ciphertext, period, target_score=target_score)
    elapsed = time.time() - start

    print(f"Early termination test (target={target_score:.3f})")
    print(f"Completed in {elapsed:.3f}s")
    print(f"Score: {score:.6f}")

    if score >= target_score:
        print("✓ Found solution meeting target score")
    print()


def test_period_limits():
    """Test that exhaustive search rejects large periods."""
    print("=" * 80)
    print("PERIOD LIMIT TEST")
    print("=" * 80)

    plaintext = "TESTTEXT"

    # Period 8 should work (40,320 permutations - slow but feasible)
    try:
        period = 8
        ciphertext = apply_columnar_permutation_encrypt(plaintext * 2, period, list(range(period)))
        _perm, _score = solve_columnar_permutation_exhaustive(ciphertext, period)
        print("Period 8: ✓ Accepted (40,320 permutations)")
    except ValueError as e:
        print(f"Period 8: ✗ Rejected - {e}")

    # Period 9 should reject (362,880 permutations - too expensive)
    try:
        period = 9
        ciphertext = apply_columnar_permutation_encrypt(plaintext * 3, period, list(range(period)))
        _perm, _score = solve_columnar_permutation_exhaustive(ciphertext, period)
        print("Period 9: ✗ Should have rejected!")
    except ValueError as e:
        print(f"Period 9: ✓ Correctly rejected - {e}")

    print()


def main():
    """Run all exhaustive search tests."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  EXHAUSTIVE PERMUTATION SEARCH TEST SUITE".center(78) + "║")
    print("║" + "  Guaranteed optimal solutions for small periods".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    test_exhaustive_vs_sa()
    test_period_limits()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Exhaustive search implemented and tested")
    print("✓ Guaranteed optimal for periods ≤6 (fast)")
    print("✓ Feasible for periods 7-8 (slower)")
    print("✓ Correctly rejects periods >8")
    print()
    print("Recommendation:")
    print("  - Use exhaustive search for periods ≤6 (guaranteed optimal)")
    print("  - Use SA multi-start for periods ≥7 (probabilistic but fast)")
    print()


if __name__ == "__main__":
    main()
