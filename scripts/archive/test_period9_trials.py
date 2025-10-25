"""Multiple trials comparing n-gram vs dictionary scoring on period 9."""

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
        current_perm = list(range(period))
        random.shuffle(current_perm)

        current_text = apply_columnar_permutation_reverse(ciphertext, period, current_perm)
        current_score = score_func(current_text)

        temperature = 10.0
        cooling_rate = 0.995

        for _ in range(max_iterations):
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


def run_trials(num_trials: int = 10):
    """Run multiple trials to compare scoring methods."""
    print("=" * 80)
    print(f"PERIOD 9 COMPARISON: {num_trials} TRIALS")
    print("=" * 80)

    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT" * 3
    period = 9
    true_perm = [4, 7, 1, 8, 2, 5, 0, 6, 3]

    ciphertext = apply_columnar_permutation_encrypt(plaintext, period, true_perm)

    print(f"\nPlaintext length: {len(plaintext)} chars")
    print(f"Period: {period}")
    print(f"True permutation: {true_perm}")
    print()

    ngram_accuracies = []
    combined_accuracies = []

    for trial in range(num_trials):
        print(f"Trial {trial + 1}/{num_trials}...", end=" ")

        # N-gram scoring
        perm_ngram, _ = solve_sa_with_scoring(ciphertext, period, score_combined)
        matches_ngram = sum(p == t for p, t in zip(perm_ngram, true_perm))
        accuracy_ngram = matches_ngram / len(true_perm)
        ngram_accuracies.append(accuracy_ngram)

        # Combined scoring
        perm_combined, _ = solve_sa_with_scoring(ciphertext, period, score_combined_with_words)
        matches_combined = sum(p == t for p, t in zip(perm_combined, true_perm))
        accuracy_combined = matches_combined / len(true_perm)
        combined_accuracies.append(accuracy_combined)

        print(f"N-gram: {accuracy_ngram:.1%}, Combined: {accuracy_combined:.1%}")

    # Calculate statistics
    avg_ngram = sum(ngram_accuracies) / len(ngram_accuracies)
    avg_combined = sum(combined_accuracies) / len(combined_accuracies)

    max_ngram = max(ngram_accuracies)
    max_combined = max(combined_accuracies)

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print("N-gram scoring:")
    print(f"  Average:  {avg_ngram:.1%}")
    print(f"  Best:     {max_ngram:.1%}")
    print()
    print("Combined scoring (n-grams + words):")
    print(f"  Average:  {avg_combined:.1%}")
    print(f"  Best:     {max_combined:.1%}")
    print()

    improvement = avg_combined - avg_ngram
    if improvement > 0.01:
        print(f"✓ Dictionary scoring IMPROVED by {improvement:.1%} on average")
    elif improvement < -0.01:
        print(f"✗ Dictionary scoring REDUCED by {abs(improvement):.1%} on average")
    else:
        print("= Dictionary scoring maintained performance")


if __name__ == "__main__":
    run_trials(10)
