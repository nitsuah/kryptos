"""Test composite cipher detection: Double Columnar Transposition.

Tests autonomous detection of multi-stage transposition.
"""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    detect_period_by_brute_force,
    solve_columnar_permutation_multi_start,
)

# Create test plaintext (longer for better statistics)
PLAINTEXT = (
    "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED"
    "THELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINY"
    "BREACHINTHETUPPERLEFTHANDCORNERANDTHENWIDENINGTEHOLEIINSERTED"
    "THECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHE"
    "FLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHE"
    "MISTXCANYOUSEEANYTHINGQASK"
)

# Known transposition parameters
PERIOD_1 = 7
PERM_1 = (3, 0, 5, 2, 6, 1, 4)  # First transposition permutation
PERIOD_2 = 5
PERM_2 = (2, 4, 0, 3, 1)  # Second transposition permutation

# Encrypt with double transposition
print(f"Creating test cipher with period {PERIOD_1} → period {PERIOD_2}")
stage1_cipher = apply_columnar_permutation_encrypt(PLAINTEXT, PERIOD_1, list(PERM_1))
DOUBLE_CIPHER = apply_columnar_permutation_encrypt(stage1_cipher, PERIOD_2, list(PERM_2))
print(f"Double cipher: {DOUBLE_CIPHER[:60]}...")
print()


def test_composite_detection():
    """Test multi-stage composite cipher detection."""
    print("=" * 80)
    print("COMPOSITE CIPHER DETECTION - Double Columnar Transposition")
    print("=" * 80)
    print(f"Plaintext length: {len(PLAINTEXT)} chars")
    print(f"Known structure: Period {PERIOD_1} → Period {PERIOD_2}")
    print()

    # Stage 1: Detect first transposition period
    print("STAGE 1: Detecting first transposition period...")
    period_results = detect_period_by_brute_force(DOUBLE_CIPHER, min_period=4, max_period=10, top_n=5)

    print("Top 5 period candidates:")
    for i, (period, score, _preview) in enumerate(period_results, 1):
        marker = " <<<" if period == PERIOD_2 else ""
        print(f"  {i}. Period {period}: score={score:.4f}{marker}")

    period_1_detected = period_results[0][0]
    print(f"\nDetected period: {period_1_detected} (actual inner period: {PERIOD_2})")

    # Since double transposition reverses order, we decrypt INNER layer first
    if period_1_detected == PERIOD_2:
        print("SUCCESS: Correctly detected inner transposition period!")
    else:
        print(f"Note: Detected period {period_1_detected} instead of {PERIOD_2}")
    print()

    # Decrypt stage 1
    perm_1, score_1 = solve_columnar_permutation_multi_start(DOUBLE_CIPHER, period_1_detected, num_restarts=10)
    decrypt_1 = apply_columnar_permutation_reverse(DOUBLE_CIPHER, period_1_detected, perm_1)

    print(f"Stage 1 decryption score: {score_1:.4f}")
    print(f"Preview: {decrypt_1[:80]}")
    print()

    # Check if it's already plaintext
    matches_1 = sum(1 for i in range(min(len(decrypt_1), len(PLAINTEXT))) if decrypt_1[i] == PLAINTEXT[i])
    accuracy_1 = matches_1 / len(PLAINTEXT) * 100

    print(f"Accuracy vs known plaintext: {accuracy_1:.1f}%")

    if accuracy_1 > 80:
        print("SUCCESS: Stage 1 alone cracked it!")
        return decrypt_1

    print("Stage 1 not sufficient, trying stage 2...")
    print()

    # Stage 2: Second transposition
    print("STAGE 2: Detecting second transposition period...")
    period_2_results = detect_period_by_brute_force(decrypt_1, min_period=4, max_period=10, top_n=5)

    print("Top 5 period candidates:")
    for i, (period, score, _preview) in enumerate(period_2_results, 1):
        marker = " <<<" if period == PERIOD_1 else ""
        print(f"  {i}. Period {period}: score={score:.4f}{marker}")

    period_2_detected = period_2_results[0][0]
    print(f"\nDetected period: {period_2_detected} (actual outer period: {PERIOD_1})")

    if period_2_detected == PERIOD_1:
        print("SUCCESS: Correctly detected outer transposition period!")
    else:
        print(f"Note: Detected period {period_2_detected} instead of {PERIOD_1}")
    print()

    # Decrypt stage 2
    perm_2, score_2 = solve_columnar_permutation_multi_start(decrypt_1, period_2_detected, num_restarts=10)
    final_decrypt = apply_columnar_permutation_reverse(decrypt_1, period_2_detected, perm_2)

    print(f"Final decryption score: {score_2:.4f}")
    print(f"Preview: {final_decrypt[:80]}")
    print()

    # Check final accuracy
    matches_final = sum(1 for i in range(min(len(final_decrypt), len(PLAINTEXT))) if final_decrypt[i] == PLAINTEXT[i])
    accuracy_final = matches_final / len(PLAINTEXT) * 100

    print(f"Final accuracy vs known plaintext: {accuracy_final:.1f}%")

    if accuracy_final > 90:
        print("\nSUCCESS: Composite cipher cracked!")
        status = "SUCCESS"
    elif accuracy_final > 70:
        print("\nPARTIAL: Close but needs refinement")
        status = "PARTIAL"
    else:
        print("\nFAILED: Approach needs adjustment")
        status = "FAILED"

    print("\nDecryption chain:")
    print(f"  Period {period_1_detected} → {accuracy_1:.1f}% accuracy")
    print(f"  Period {period_2_detected} → {accuracy_final:.1f}% accuracy")

    return final_decrypt, status


if __name__ == "__main__":
    result, test_status = test_composite_detection()
    print("\n" + "=" * 80)
    print(f"Status: {test_status}")
    print(f"Final result (first 150 chars):\n{result[:150]}")
