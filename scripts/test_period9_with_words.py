"""Test dictionary scoring on period 9 (where n-gram scoring struggled)."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    score_combined,
    score_combined_with_words,
)


def solve_sa_with_scoring(
    ciphertext: str,
    period: int,
    score_func,
    num_restarts: int = 5,
    max_iterations: int = 10000,
) -> tuple[list[int], float]:
    """SA solver with custom scoring function."""
    best_perm: list[int] = list(range(period))
    best_score = float('-inf')

    for _ in range(num_restarts):
        # Start with random permutation
        current_perm = list(range(period))
        random.shuffle(current_perm)

        current_text = apply_columnar_permutation_reverse(ciphertext, period, current_perm)
        current_score = score_func(current_text)

        temperature = 10.0
        cooling_rate = 0.995

        for _ in range(max_iterations):
            # Generate neighbor
            neighbor_perm = current_perm.copy()
            i, j = random.sample(range(period), 2)
            neighbor_perm[i], neighbor_perm[j] = neighbor_perm[j], neighbor_perm[i]

            neighbor_text = apply_columnar_permutation_reverse(ciphertext, period, neighbor_perm)
            neighbor_score = score_func(neighbor_text)

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


def test_period_9():
    """Test on period 9 where n-gram scoring achieved only 44.9% accuracy."""
    print("=" * 80)
    print("PERIOD 9 TEST: N-gram vs Dictionary Scoring")
    print("=" * 80)

    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT" * 3  # Make longer
    period = 9
    true_perm = [4, 7, 1, 8, 2, 5, 0, 6, 3]  # Same as test_simulated_annealing.py

    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)

    print(f"\nPlaintext length: {len(plaintext)} chars")
    print(f"Period: {period}")
    print(f"True permutation: {true_perm}")
    print()

    # Test n-gram scoring
    print("Testing with n-gram scoring...")
    perm_ngram, score_ngram = solve_sa_with_scoring(
        ciphertext,
        period,
        score_combined,
        num_restarts=5,
        max_iterations=10000,
    )

    decrypted_ngram = apply_columnar_permutation_reverse(ciphertext, period, perm_ngram)
    matches_ngram = sum(p == t for p, t in zip(perm_ngram, true_perm))
    accuracy_ngram = matches_ngram / len(true_perm)

    print(f"  Found permutation: {perm_ngram}")
    print(f"  True permutation:  {true_perm}")
    print(f"  Score: {score_ngram:.6f}")
    print(f"  Accuracy: {accuracy_ngram:.1%} ({matches_ngram}/{len(true_perm)} correct)")
    print(f"  Decrypted preview: {decrypted_ngram[:50]}...")
    print()

    # Test combined scoring
    print("Testing with combined scoring (n-grams + words)...")
    perm_combined, score_combined_val = solve_sa_with_scoring(
        ciphertext,
        period,
        score_combined_with_words,
        num_restarts=5,
        max_iterations=10000,
    )

    decrypted_combined = apply_columnar_permutation_reverse(ciphertext, period, perm_combined)
    matches_combined = sum(p == t for p, t in zip(perm_combined, true_perm))
    accuracy_combined = matches_combined / len(true_perm)

    print(f"  Found permutation: {perm_combined}")
    print(f"  True permutation:  {true_perm}")
    print(f"  Score: {score_combined_val:.6f}")
    print(f"  Accuracy: {accuracy_combined:.1%} ({matches_combined}/{len(true_perm)} correct)")
    print(f"  Decrypted preview: {decrypted_combined[:50]}...")
    print()

    # Summary
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"N-gram scoring:    {accuracy_ngram:.1%} accuracy")
    print(f"Combined scoring:  {accuracy_combined:.1%} accuracy")

    improvement = accuracy_combined - accuracy_ngram
    if improvement > 0:
        print(f"\n✓ Dictionary scoring IMPROVED by {improvement:.1%}")
    elif improvement == 0:
        print("\n= Dictionary scoring maintained performance")
    else:
        print(f"\n✗ Dictionary scoring reduced by {abs(improvement):.1%}")


if __name__ == "__main__":
    # Set seed for reproducibility
    random.seed(42)
    test_period_9()
