"""Test transposition solving with dictionary-based scoring."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    score_combined_with_words,
    solve_columnar_permutation_simulated_annealing_multi_start,
)


def test_with_different_scoring():
    """Test SA solver with n-gram vs dictionary scoring."""
    print("=" * 80)
    print("TRANSPOSITION SOLVING: N-gram vs Dictionary Scoring")
    print("=" * 80)

    # Known test case from K1
    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT"
    period = 5
    true_perm = [2, 4, 0, 3, 1]  # Known permutation

    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)

    print(f"\nPlaintext:  {plaintext}")
    print(f"Ciphertext: {ciphertext}")
    print(f"Period: {period}")
    print(f"True permutation: {true_perm}")
    print()

    # Create a custom solver that uses word-based scoring
    import math
    import random

    def solve_with_word_scoring(ciphertext: str, period: int, num_restarts: int = 5) -> tuple[list[int], float]:
        """SA solver using combined word+ngram scoring."""
        best_perm: list[int] = list(range(period))
        best_score = float('-inf')

        for _ in range(num_restarts):
            # Start with random permutation
            current_perm = list(range(period))
            random.shuffle(current_perm)

            current_text = apply_columnar_permutation_reverse(ciphertext, period, current_perm)
            current_score = score_combined_with_words(current_text)

            temperature = 10.0
            cooling_rate = 0.995

            for _ in range(5000):
                # Generate neighbor
                neighbor_perm = current_perm.copy()
                i, j = random.sample(range(period), 2)
                neighbor_perm[i], neighbor_perm[j] = neighbor_perm[j], neighbor_perm[i]

                neighbor_text = apply_columnar_permutation_reverse(ciphertext, period, neighbor_perm)
                neighbor_score = score_combined_with_words(neighbor_text)

                delta = neighbor_score - current_score

                if delta > 0 or random.random() < math.exp(delta / temperature):
                    current_perm = neighbor_perm
                    current_score = neighbor_score

                temperature *= cooling_rate

                if temperature < 0.01:
                    break

            if current_score > best_score:
                best_score = current_score
                best_perm = current_perm

        return best_perm, best_score

    # Test 1: N-gram scoring (baseline)
    print("Testing with n-gram scoring (baseline)...")
    perm_ngram, score_ngram = solve_columnar_permutation_simulated_annealing_multi_start(
        ciphertext,
        period,
        num_restarts=5,
        max_iterations=5000,
    )

    decrypted_ngram = apply_columnar_permutation_reverse(ciphertext, period, perm_ngram)
    matches_ngram = sum(p == t for p, t in zip(perm_ngram, true_perm))
    accuracy_ngram = matches_ngram / len(true_perm)

    print(f"  Found permutation: {perm_ngram}")
    print(f"  Score: {score_ngram:.6f}")
    print(f"  Accuracy: {accuracy_ngram:.1%} ({matches_ngram}/{len(true_perm)} correct)")
    print(f"  Decrypted: {decrypted_ngram[:40]}...")
    print()

    # Test 2: Combined scoring (n-grams + words)
    print("Testing with combined scoring (n-grams + words)...")
    perm_combined, score_combined_val = solve_with_word_scoring(ciphertext, period, num_restarts=5)

    decrypted_combined = apply_columnar_permutation_reverse(ciphertext, period, perm_combined)
    matches_combined = sum(p == t for p, t in zip(perm_combined, true_perm))
    accuracy_combined = matches_combined / len(true_perm)

    print(f"  Found permutation: {perm_combined}")
    print(f"  Score: {score_combined_val:.6f}")
    print(f"  Accuracy: {accuracy_combined:.1%} ({matches_combined}/{len(true_perm)} correct)")
    print(f"  Decrypted: {decrypted_combined[:40]}...")
    print()

    # Summary
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"N-gram scoring:    {accuracy_ngram:.1%} accuracy")
    print(f"Combined scoring:  {accuracy_combined:.1%} accuracy")

    if accuracy_combined > accuracy_ngram:
        print("\n✓ Dictionary scoring IMPROVED results")
    elif accuracy_combined == accuracy_ngram:
        print("\n= Dictionary scoring maintained performance")
    else:
        print("\n✗ Dictionary scoring reduced performance")


if __name__ == "__main__":
    test_with_different_scoring()
