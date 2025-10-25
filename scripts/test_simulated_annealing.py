"""Compare simulated annealing vs hill-climbing for transposition solving."""

from __future__ import annotations

import sys
import time
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    solve_columnar_permutation,
    solve_columnar_permutation_multi_start,
    solve_columnar_permutation_simulated_annealing,
    solve_columnar_permutation_simulated_annealing_multi_start,
)


def test_solver_comparison():
    """Compare different permutation solvers."""
    print("=" * 80)
    print("PERMUTATION SOLVER COMPARISON")
    print("=" * 80)

    # Create test cases with different periods
    plaintext = (
        "THECRYPTOGRAPHYOFTHEKRYPTOSWASSUPPOSEDTOBEANEASYONEBUT" "ITHASPROVEDTOBEONEOFTHEMOSTDIFFICULTPUZZLESINTHEWORLD"
    )

    test_cases = [
        (5, [2, 4, 0, 3, 1]),
        (7, [3, 0, 5, 2, 6, 1, 4]),
        (9, [4, 7, 1, 8, 2, 5, 0, 6, 3]),
    ]

    for period, true_perm in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Period {period} - Permutation: {true_perm}")
        print("=" * 80)

        # Encrypt
        ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)
        print(f"Ciphertext: {ciphertext[:60]}...")
        print()

        # Test 1: Hill-climbing (single)
        print("1. Hill-Climbing (single run):")
        start = time.time()
        hc_perm, hc_score = solve_columnar_permutation(ciphertext, period, max_iterations=5000)
        hc_time = time.time() - start

        hc_decrypted = apply_columnar_permutation_reverse(ciphertext, period, hc_perm)
        hc_accuracy = sum(1 for i in range(len(plaintext)) if hc_decrypted[i] == plaintext[i]) / len(plaintext) * 100

        print(f"   Permutation: {hc_perm}")
        print(f"   Score: {hc_score:.4f}")
        print(f"   Accuracy: {hc_accuracy:.1f}%")
        print(f"   Time: {hc_time:.3f}s")
        print()

        # Test 2: Hill-climbing (multi-start)
        print("2. Hill-Climbing (10 restarts):")
        start = time.time()
        ms_perm, ms_score = solve_columnar_permutation_multi_start(
            ciphertext,
            period,
            num_restarts=10,
            max_iterations=5000,
        )
        ms_time = time.time() - start

        ms_decrypted = apply_columnar_permutation_reverse(ciphertext, period, ms_perm)
        ms_accuracy = sum(1 for i in range(len(plaintext)) if ms_decrypted[i] == plaintext[i]) / len(plaintext) * 100

        print(f"   Permutation: {ms_perm}")
        print(f"   Score: {ms_score:.4f}")
        print(f"   Accuracy: {ms_accuracy:.1f}%")
        print(f"   Time: {ms_time:.3f}s")
        print()

        # Test 3: Simulated annealing
        print("3. Simulated Annealing:")
        start = time.time()
        sa_perm, sa_score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations=10000,
            initial_temp=10.0,
            cooling_rate=0.995,
        )
        sa_time = time.time() - start

        sa_decrypted = apply_columnar_permutation_reverse(ciphertext, period, sa_perm)
        sa_accuracy = sum(1 for i in range(len(plaintext)) if sa_decrypted[i] == plaintext[i]) / len(plaintext) * 100

        print(f"   Permutation: {sa_perm}")
        print(f"   Score: {sa_score:.4f}")
        print(f"   Accuracy: {sa_accuracy:.1f}%")
        print(f"   Time: {sa_time:.3f}s")
        print()

        # Test 4: Simulated annealing (multi-start)
        print("4. Simulated Annealing (5 restarts):")
        start = time.time()
        sa_ms_perm, sa_ms_score = solve_columnar_permutation_simulated_annealing_multi_start(
            ciphertext,
            period,
            num_restarts=5,
            max_iterations=10000,
            initial_temp=10.0,
            cooling_rate=0.995,
        )
        sa_ms_time = time.time() - start

        sa_ms_decrypted = apply_columnar_permutation_reverse(ciphertext, period, sa_ms_perm)
        sa_ms_accuracy = (
            sum(1 for i in range(len(plaintext)) if sa_ms_decrypted[i] == plaintext[i]) / len(plaintext) * 100
        )

        print(f"   Permutation: {sa_ms_perm}")
        print(f"   Score: {sa_ms_score:.4f}")
        print(f"   Accuracy: {sa_ms_accuracy:.1f}%")
        print(f"   Time: {sa_ms_time:.3f}s")
        print()

        # Summary
        print("SUMMARY:")
        print(f"  True permutation: {true_perm}")
        print()
        best_accuracy = max(hc_accuracy, ms_accuracy, sa_accuracy, sa_ms_accuracy)

        if hc_accuracy >= 95:
            print(f"  Hill-Climbing: SOLVED ({hc_accuracy:.1f}%)")
        elif ms_accuracy >= 95:
            print(f"  Multi-Start HC: SOLVED ({ms_accuracy:.1f}%)")
        elif sa_accuracy >= 95:
            print(f"  Simulated Annealing: SOLVED ({sa_accuracy:.1f}%)")
        elif sa_ms_accuracy >= 95:
            print(f"  Multi-Start SA: SOLVED ({sa_ms_accuracy:.1f}%)")
        else:
            print("  No solver reached 95% accuracy")
            print(f"  Best: {best_accuracy:.1f}%")

        if sa_ms_accuracy > ms_accuracy and sa_ms_accuracy > hc_accuracy:
            print(f"  Winner: Multi-Start SA (+{sa_ms_accuracy - max(hc_accuracy, ms_accuracy):.1f}%)")
        elif sa_accuracy > ms_accuracy and sa_accuracy > hc_accuracy:
            print(f"  Winner: Single SA (+{sa_accuracy - max(hc_accuracy, ms_accuracy):.1f}%)")
        elif ms_accuracy > hc_accuracy:
            print(f"  Winner: Multi-Start HC (+{ms_accuracy - hc_accuracy:.1f}%)")


if __name__ == "__main__":
    test_solver_comparison()
    print("\n" + "=" * 80)
    print("COMPARISON COMPLETE")
    print("=" * 80)
