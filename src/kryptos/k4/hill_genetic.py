"""Genetic algorithm for Hill 3x3 cipher key search.

Hill 3x3 has 26^9 ≈ 5.4 trillion possible keys, making exhaustive search infeasible.
This module implements a genetic algorithm to search the keyspace intelligently.
"""

from __future__ import annotations

import random
from math import gcd

from kryptos.k4.hill_cipher import (
    MOD,
    hill_decrypt,
    matrix_det,
    matrix_inv_mod,
)
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
    flat1 = [parent1[i][j] for i in range(3) for j in range(3)]
    flat2 = [parent2[i][j] for i in range(3) for j in range(3)]

    point = random.randint(1, 8)
    child_flat = flat1[:point] + flat2[point:]

    child = [[child_flat[i * 3 + j] for j in range(3)] for i in range(3)]
    return child


def ensure_invertible(matrix: list[list[int]]) -> list[list[int]]:
    if matrix_inv_mod(matrix) is not None:
        return matrix

    for _ in range(10):
        i, j = random.randint(0, 2), random.randint(0, 2)
        old_val = matrix[i][j]
        matrix[i][j] = (matrix[i][j] + random.randint(1, 25)) % 26
        if matrix_inv_mod(matrix) is not None:
            return matrix
        matrix[i][j] = old_val

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

    for _ in range(generations):
        scored_population = [(key, fitness(key, ciphertext)) for key in population]

        scored_population.sort(key=lambda x: x[1], reverse=True)

        elites = [key for key, _ in scored_population[:elite_count]]

        new_population = elites[:]

        while len(new_population) < population_size:
            parent1 = tournament_select(scored_population, tournament_size=5)
            parent2 = tournament_select(scored_population, tournament_size=5)

            child = crossover_matrices(parent1, parent2)

            child = mutate_matrix(child, mutation_rate)

            child = ensure_invertible(child)

            new_population.append(child)

        population = new_population

    final_results = []
    for key in population[:100]:
        score = fitness(key, ciphertext)
        plaintext = hill_decrypt(ciphertext, key)
        if plaintext:
            final_results.append((key, score, plaintext))

    final_results.sort(key=lambda x: x[1], reverse=True)
    return final_results


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
