"""Test transposition on simple single-stage columnar transposition.

This validates that our permutation solver works correctly when not complicated
by double transposition, rotation, or other multi-stage transforms.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_reverse,
    detect_period_combined,
    solve_columnar_permutation,
)

# Longer English text for better statistics
PLAINTEXT = (
    "CRYPTOGRAPHYISTHEPRACTICEANDSTUDY"
    "OFSECURECOMMUNICATIONINTHEPRESENCE"
    "OFTHIRDPARTIESMOREGENERALLYITISA"
    "BOUTCONSTRUCTINGANDANALYZINGPROTO"
    "COLSTHATPREVENTTHIRDPARTIESORTHE"
    "PUBLICFROMREADINGPRIVATEMESSAGES"
)


def encrypt_columnar(plaintext: str, period: int, permutation: list[int]) -> str:
    """Encrypt using columnar transposition.

    Args:
        plaintext: Text to encrypt
        period: Number of columns
        permutation: Column reading order (e.g., [2,0,1] reads col 2, then 0, then 1)

    Returns:
        Ciphertext
    """
    text = ''.join(c for c in plaintext.upper() if c.isalpha())

    # Fill columns row-by-row
    columns = ['' for _ in range(period)]
    for i, char in enumerate(text):
        columns[i % period] += char

    # Read in permuted order
    ciphertext = ''.join(columns[p] for p in permutation)
    return ciphertext


def test_simple_transposition():
    """Test on simple single-stage transposition."""
    print("=" * 80)
    print("SIMPLE SINGLE-STAGE COLUMNAR TRANSPOSITION TEST")
    print("=" * 80)

    # Parameters
    period = 7
    # Random permutation for realistic test
    true_permutation = [3, 0, 5, 1, 6, 4, 2]

    print(f"Plaintext length: {len(PLAINTEXT)} chars")
    print(f"Period: {period}")
    print(f"True permutation: {true_permutation}")
    print()

    # Encrypt
    ciphertext = encrypt_columnar(PLAINTEXT, period, true_permutation)
    print(f"Ciphertext: {ciphertext[:100]}...")
    print()

    # Step 1: Detect period
    print("STEP 1: Period Detection")
    print("-" * 80)
    period_results = detect_period_combined(ciphertext, max_period=20)

    print("Top 5 period candidates:")
    for i, (p, conf, method) in enumerate(period_results[:5], 1):
        marker = "✓" if p == period else " "
        print(f"{marker} {i}. Period {p:2d}: confidence={conf:.4f} ({method})")

    detected_period = period_results[0][0]
    print()

    if detected_period == period:
        print("SUCCESS: Correct period detected as #1 candidate!")
    else:
        print(f"WARNING: Detected period {detected_period}, true period is {period}")
        # Continue with true period for permutation test
        detected_period = period

    print()

    # Step 2: Solve permutation
    print("STEP 2: Permutation Solving")
    print("-" * 80)
    print("Running hill-climbing solver...")

    recovered_perm, bigram_score = solve_columnar_permutation(ciphertext, detected_period, max_iterations=5000)

    print(f"Recovered permutation: {recovered_perm}")
    print(f"True permutation:      {true_permutation}")
    print(f"Bigram score: {bigram_score:.4f}")
    print()

    # Decrypt
    recovered_text = apply_columnar_permutation_reverse(ciphertext, detected_period, recovered_perm)

    print("Recovered text (first 100 chars):")
    print(recovered_text[:100])
    print()
    print("True plaintext (first 100 chars):")
    print(PLAINTEXT[:100])
    print()

    # Check correctness
    matches = sum(1 for i in range(len(PLAINTEXT)) if recovered_text[i] == PLAINTEXT[i])
    accuracy = matches / len(PLAINTEXT) * 100

    print(f"Character accuracy: {matches}/{len(PLAINTEXT)} ({accuracy:.1f}%)")

    if accuracy == 100:
        print("SUCCESS: PERFECT - Exact plaintext recovered!")
        return True
    elif accuracy > 95:
        print("SUCCESS: EXCELLENT - Near-perfect recovery!")
        return True
    elif accuracy > 80:
        print("WARNING: GOOD - High accuracy but not perfect")
        return False
    elif accuracy > 50:
        print("WARNING: PARTIAL - Some success")
        return False
    else:
        print("FAILED: Low accuracy")
        return False


def test_multiple_periods():
    """Test on multiple period sizes to validate robustness."""
    print("\n" + "=" * 80)
    print("MULTIPLE PERIOD TEST")
    print("=" * 80)

    test_periods = [5, 7, 9, 11]
    results = []

    for period in test_periods:
        # Random permutation
        perm = list(range(period))
        random.shuffle(perm)

        # Encrypt
        ciphertext = encrypt_columnar(PLAINTEXT, period, perm)

        # Detect period
        period_results = detect_period_combined(ciphertext, max_period=20)
        detected_period = period_results[0][0]
        period_correct = detected_period == period

        # Solve permutation (use true period for fair test)
        recovered_perm, _ = solve_columnar_permutation(ciphertext, period, max_iterations=5000)
        recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)

        # Check accuracy
        matches = sum(1 for i in range(len(PLAINTEXT)) if recovered_text[i] == PLAINTEXT[i])
        accuracy = matches / len(PLAINTEXT) * 100

        results.append((period, period_correct, accuracy))

        status = "OK" if accuracy > 95 else "WARN" if accuracy > 80 else "FAIL"
        print(f"{status} Period {period:2d}: Period detection={period_correct}, Accuracy={accuracy:5.1f}%")

    print()

    # Summary
    avg_accuracy = sum(acc for _, _, acc in results) / len(results)
    period_detection_rate = sum(1 for _, correct, _ in results if correct) / len(results) * 100

    print(f"Average accuracy: {avg_accuracy:.1f}%")
    print(f"Period detection rate: {period_detection_rate:.0f}%")

    if avg_accuracy > 95 and period_detection_rate > 75:
        print("\nSUCCESS: VALIDATION PASSED - Transposition solver working correctly!")
        return True
    else:
        print("\nWARNING: VALIDATION PARTIAL - Needs improvement")
        return False


if __name__ == "__main__":
    # Test 1: Single detailed test
    success_single = test_simple_transposition()

    # Test 2: Multiple periods
    success_multi = test_multiple_periods()

    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    if success_single and success_multi:
        print("SUCCESS: ALL TESTS PASSED - Transposition solver validated on simple cases")
        print()
        print("CONCLUSION:")
        print("The algorithm works correctly on single-stage transposition.")
        print("K3 failure is due to double transposition + rotation complexity,")
        print("not a fundamental algorithm flaw.")
    elif success_single or success_multi:
        print("WARNING: PARTIAL SUCCESS - Algorithm works but needs refinement")
    else:
        print("FAILED: Algorithm needs debugging")
