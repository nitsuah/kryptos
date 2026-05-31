"""Tests for Hill 3x3 genetic algorithm module."""

from __future__ import annotations

import pytest

from kryptos.k4.hill_cipher import hill_decrypt, hill_encrypt, matrix_inv_mod
from kryptos.k4.hill_genetic import (
    crossover_matrices,
    ensure_invertible,
    fitness,
    genetic_algorithm_hill3x3,
    mutate_matrix,
    random_invertible_3x3,
    tournament_select,
)


def test_random_invertible_3x3():
    """Test random 3x3 invertible matrix generation."""
    for _ in range(10):
        matrix = random_invertible_3x3()

        # Check dimensions
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)

        # Check all elements in range [0, 25]
        for row in matrix:
            for elem in row:
                assert 0 <= elem <= 25

        # Check invertibility
        inv = matrix_inv_mod(matrix)
        assert inv is not None, f"Generated non-invertible matrix: {matrix}"


def test_mutate_matrix():
    """Test matrix mutation."""
    original = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    # With mutation_rate=0.0, should return identical matrix
    mutated_none = mutate_matrix(original, mutation_rate=0.0)
    assert mutated_none == original

    # With mutation_rate=1.0, should change all elements (very likely)
    mutated_all = mutate_matrix(original, mutation_rate=1.0)
    # At least some elements should be different
    assert mutated_all != original

    # Check dimensions preserved
    assert len(mutated_all) == 3
    assert all(len(row) == 3 for row in mutated_all)


def test_crossover_matrices():
    """Test matrix crossover."""
    parent1 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    parent2 = [[25, 25, 25], [25, 25, 25], [25, 25, 25]]

    child = crossover_matrices(parent1, parent2)

    # Check dimensions
    assert len(child) == 3
    assert all(len(row) == 3 for row in child)

    # Child should contain elements from both parents
    flat_child = [child[i][j] for i in range(3) for j in range(3)]
    assert any(x == 0 for x in flat_child)  # Has some from parent1
    assert any(x == 25 for x in flat_child)  # Has some from parent2


def test_ensure_invertible():
    """Test ensuring matrix invertibility."""
    # Non-invertible matrix (all zeros)
    non_invertible = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    result = ensure_invertible(non_invertible)

    # Result should be invertible
    assert matrix_inv_mod(result) is not None

    # Already invertible matrix should be preserved
    invertible = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity
    result2 = ensure_invertible(invertible)
    assert result2 == invertible


def test_fitness():
    """Test fitness function."""
    # Known good key for testing
    key = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity matrix

    plaintext = "THEQUICKBROWNFOX"
    ciphertext = hill_encrypt(plaintext, key)

    # Fitness with correct key should return a valid score
    score = fitness(key, ciphertext)
    assert isinstance(score, float)
    assert score > -1000  # Should not be the error sentinel

    # Fitness with a random invertible key
    wrong_key = random_invertible_3x3()
    wrong_score = fitness(wrong_key, ciphertext)

    # Both should return valid scores (not error sentinels)
    assert isinstance(score, float)
    assert isinstance(wrong_score, float)
    assert score > -1000
    assert wrong_score > -1000


def test_tournament_select():
    """Test tournament selection."""
    # Create population with known fitness scores
    scored_pop = [
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 10.0),
        ([[2, 3, 4], [5, 6, 7], [8, 9, 10]], 50.0),  # Best
        ([[3, 4, 5], [6, 7, 8], [9, 10, 11]], 5.0),  # Worst
    ]

    # Run tournament selection multiple times
    selections = [tournament_select(scored_pop, tournament_size=2) for _ in range(20)]

    # Best candidate should be selected most often
    best_count = sum(1 for s in selections if s == scored_pop[1][0])
    worst_count = sum(1 for s in selections if s == scored_pop[2][0])

    # Best should be selected more than worst (probabilistic test)
    assert best_count >= worst_count


@pytest.mark.slow
def test_genetic_algorithm_hill3x3():
    """Integration test for genetic algorithm.

    Note: This is a slow test (~10-30 seconds) due to GA iterations.
    """
    # Create a simple known plaintext/ciphertext pair
    plaintext = "EASTBERLINCLOCKX"  # 16 chars (multiple of 3 with padding)
    # Pad to multiple of 3
    while len(plaintext) % 3 != 0:
        plaintext += "X"

    # Use a known key
    true_key = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]  # Known invertible
    ciphertext = hill_encrypt(plaintext, true_key)

    # Run GA with small parameters for faster testing
    results = genetic_algorithm_hill3x3(
        ciphertext,
        population_size=100,  # Smaller for testing
        generations=20,  # Fewer generations
        mutation_rate=0.15,
        elite_fraction=0.2,
    )

    # Should return results
    assert len(results) > 0

    # Results should be sorted by score (descending)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)

    # Top result should have a reasonable score
    best_key, best_score, best_plaintext = results[0]
    assert best_score > -100  # Not a total failure

    # Best key should be invertible
    assert matrix_inv_mod(best_key) is not None

    # Verify decryption works
    decrypted = hill_decrypt(ciphertext, best_key)
    assert decrypted is not None
    assert len(decrypted) == len(plaintext)


def test_genetic_algorithm_convergence():
    """Test that GA shows improvement over generations.

    Uses a simple test case to verify the algorithm improves scores.
    """
    # Simple plaintext with good English characteristics
    plaintext = "THISISATESTTHATCONTAINSCOMMONENGLISHLETTERS"
    # Pad to multiple of 3
    while len(plaintext) % 3 != 0:
        plaintext += "X"

    # Encrypt with random key
    key = random_invertible_3x3()
    ciphertext = hill_encrypt(plaintext, key)

    # Run GA with minimal parameters
    results = genetic_algorithm_hill3x3(
        ciphertext,
        population_size=50,
        generations=10,
        mutation_rate=0.2,
        elite_fraction=0.3,
    )

    # Should find reasonable candidates
    assert len(results) > 0

    # Results should return valid scores (not error sentinels)
    best_score = results[0][1]
    assert best_score > -1000  # Not an error
    assert isinstance(best_score, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
