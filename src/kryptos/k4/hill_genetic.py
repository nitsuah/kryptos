"""Genetic algorithm for Hill 3x3 cipher key search.

Hill 3x3 has 26^9 ≈ 5.4 trillion possible keys, making exhaustive search infeasible.
This module implements a genetic algorithm to search the keyspace intelligently.
"""

from __future__ import annotations

import random
from math import gcd

from kryptos.k4.hill_cipher import MOD, hill_decrypt, matrix_det, matrix_inv_mod
from kryptos.k4.scoring import combined_plaintext_score


def random_invertible_3x3() -> list[list[int]]:
    max_attempts = 1000
    for _ in range(max_attempts):
        matrix = [[random.randint(0, 25) for _ in range(3)] for _ in range(3)]
        det = matrix_det(matrix) % MOD
        if gcd(det, MOD) == 1:
            return matrix
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def mutate_matrix(matrix: list[list[int]], mutation_rate: float = 0.1) -> list[list[int]]:
    new_matrix = [row[:] for row in matrix]
    for i in range(3):
        for j in range(3):
            if random.random() < mutation_rate:
                new_matrix[i][j] = random.randint(0, 25)
    return new_matrix


def crossover_matrices(parent1: list[list[int]], parent2: list[list[int]]) -> list[list[int]]:
    # Row-level crossover: each row is inherited independently from one parent.
    # This preserves Hill cipher row structure better than flat single-point crossover.
    return [(parent1[i] if random.random() < 0.5 else parent2[i])[:] for i in range(3)]


def ensure_invertible(matrix: list[list[int]]) -> list[list[int]]:
    if matrix_inv_mod(matrix) is not None:
        return matrix

    # Work on a copy to avoid mutating the caller's matrix.
    m = [row[:] for row in matrix]
    for _ in range(10):
        i, j = random.randint(0, 2), random.randint(0, 2)
        old_val = m[i][j]
        m[i][j] = (m[i][j] + random.randint(1, 25)) % 26
        if matrix_inv_mod(m) is not None:
            return m
        m[i][j] = old_val

    return random_invertible_3x3()


def fitness(key: list[list[int]], ciphertext: str) -> float:
    if matrix_inv_mod(key) is None:
        return -1000.0

    try:
        plaintext = hill_decrypt(ciphertext, key)
        if plaintext is None:
            return -1000.0
        return combined_plaintext_score(plaintext)
    except Exception:
        return -1000.0


def genetic_algorithm_hill3x3(
    ciphertext: str,
    population_size: int = 1000,
    generations: int = 100,
    mutation_rate: float = 0.1,
    elite_fraction: float = 0.2,
) -> list[tuple[list[list[int]], float, str]]:
    """Run genetic algorithm to search for Hill 3x3 cipher keys.

    Args:
        ciphertext: The ciphertext to decrypt
        population_size: Number of keys in each generation
        generations: Number of generations to evolve
        mutation_rate: Probability of mutating each matrix element
        elite_fraction: Fraction of population to preserve as elites

    Returns:
        List of (key, score, plaintext) tuples, sorted by score descending
    """
    population = [random_invertible_3x3() for _ in range(population_size)]

    elite_count = int(population_size * elite_fraction)

    global_best_key: list[list[int]] | None = None
    global_best_score = float("-inf")

    for _ in range(generations):
        scored_population = [(key, fitness(key, ciphertext)) for key in population]

        scored_population.sort(key=lambda x: x[1], reverse=True)

        # Track the all-time best so it is never lost to drift.
        gen_best_key, gen_best_score = scored_population[0]
        if gen_best_score > global_best_score:
            global_best_score = gen_best_score
            global_best_key = [row[:] for row in gen_best_key]

        elites = [key for key, _ in scored_population[:elite_count]]

        new_population = elites[:]

        # Inject the all-time best in case it was displaced by drift.
        if global_best_key is not None and global_best_key not in new_population:
            new_population[0] = [row[:] for row in global_best_key]

        while len(new_population) < population_size:
            parent1 = tournament_select(scored_population, tournament_size=5)
            parent2 = tournament_select(scored_population, tournament_size=5)

            child = crossover_matrices(parent1, parent2)

            child = mutate_matrix(child, mutation_rate)

            child = ensure_invertible(child)

            new_population.append(child)

        population = new_population

    # Local search: hill-climb the top candidates by trying ±1 on each cell.
    # This is cheap relative to GA cost and significantly improves final quality.
    top_keys = [
        key
        for key, _ in sorted(
            [(k, fitness(k, ciphertext)) for k in population[:50]],
            key=lambda x: x[1],
            reverse=True,
        )[:10]
    ]
    if global_best_key is not None and global_best_key not in top_keys:
        top_keys.insert(0, global_best_key)

    polished: list[list[list[int]]] = []
    for key in top_keys:
        polished.append(_local_search(key, ciphertext, rounds=3))
    population = list(population) + polished

    final_results = []
    seen: set[str] = set()
    for key in population[:100] + polished:
        key_id = str(key)
        if key_id in seen:
            continue
        seen.add(key_id)
        score = fitness(key, ciphertext)
        plaintext = hill_decrypt(ciphertext, key)
        if plaintext:
            final_results.append((key, score, plaintext))

    final_results.sort(key=lambda x: x[1], reverse=True)
    return final_results


def _local_search(key: list[list[int]], ciphertext: str, rounds: int = 3) -> list[list[int]]:
    """Hill-climb a key by exhaustively trying all 26 values for each cell."""
    best = [row[:] for row in key]
    best_score = fitness(best, ciphertext)
    for _ in range(rounds):
        improved = False
        for i in range(3):
            for j in range(3):
                for v in range(26):
                    if v == best[i][j]:
                        continue
                    candidate = [row[:] for row in best]
                    candidate[i][j] = v
                    if matrix_inv_mod(candidate) is None:
                        continue
                    s = fitness(candidate, ciphertext)
                    if s > best_score:
                        best_score = s
                        best = candidate
                        improved = True
        if not improved:
            break
    return best


def tournament_select(
    scored_population: list[tuple[list[list[int]], float]],
    tournament_size: int = 5,
) -> list[list[int]]:
    """Select an individual using tournament selection.

    Args:
        scored_population: List of (key, fitness_score) tuples
        tournament_size: Number of individuals in tournament

    Returns:
        Selected key matrix
    """
    tournament = random.sample(scored_population, min(tournament_size, len(scored_population)))
    winner = max(tournament, key=lambda x: x[1])
    return winner[0]


__all__ = [
    "random_invertible_3x3",
    "mutate_matrix",
    "crossover_matrices",
    "ensure_invertible",
    "fitness",
    "genetic_algorithm_hill3x3",
    "tournament_select",
]
