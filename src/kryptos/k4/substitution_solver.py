"""Monoalphabetic substitution solver (simple stochastic hill climb).

This is a lightweight solver intended for short K4 segments. It attempts to
maximize the combined_plaintext_score from scoring.py by permuting a mapping.
Not cryptographically exhaustive; serves as a heuristic filter.
"""

import random

from .scoring import combined_plaintext_score

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def initial_mapping() -> dict[str, str]:
    letters = list(ALPHABET)
    random.shuffle(letters)
    return {c: letters[i] for i, c in enumerate(ALPHABET)}


def apply_mapping(text: str, mapping: dict[str, str]) -> str:
    return ''.join(mapping.get(c, c) for c in text)


def invert_mapping(mapping: dict[str, str]) -> dict[str, str]:
    return {v: k for k, v in mapping.items()}


def random_swap(mapping: dict[str, str]) -> None:
    a, b = random.sample(ALPHABET, 2)
    mapping[a], mapping[b] = mapping[b], mapping[a]


def solve_substitution(ciphertext: str, iterations: int = 5000, restarts: int = 5) -> tuple[str, float, dict[str, str]]:
    best_plain = ''
    best_score = float('-inf')
    best_map: dict[str, str] = {}

    for _ in range(restarts):
        mapping = initial_mapping()
        plain = apply_mapping(ciphertext, mapping)
        score = combined_plaintext_score(plain)
        stagnant = 0
        for _it in range(iterations):
            candidate = dict(mapping)
            random_swap(candidate)
            cand_plain = apply_mapping(ciphertext, candidate)
            cand_score = combined_plaintext_score(cand_plain)
            if cand_score > score:
                mapping = candidate
                plain = cand_plain
                score = cand_score
                stagnant = 0
            else:
                stagnant += 1
            if stagnant > 400:
                for _s in range(3):
                    random_swap(mapping)
                plain = apply_mapping(ciphertext, mapping)
                score = combined_plaintext_score(plain)
                stagnant = 0
        if score > best_score:
            best_score = score
            best_plain = plain
            best_map = mapping
    return best_plain, best_score, best_map
