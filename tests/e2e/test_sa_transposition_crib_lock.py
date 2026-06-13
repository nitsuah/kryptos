"""Verification of SA columnar transposition + early-crib locking.

Covers two K4 attack-toolkit capabilities end to end:

1. **Simulated-annealing columnar solver** (`solve_columnar_permutation_simulated_annealing`)
   recovers a planted columnar permutation on realistic-length English text,
   and the new ``seed_perm`` argument lets the search be seeded from a known
   pattern (e.g. K3's width/rotation) without ever scoring worse than the seed.

2. **Early-crib locking** (`search_with_multiple_cribs_positions`) prunes the
   columnar permutation space by >90% — before any expensive scoring — by
   rejecting permutations that don't place the cribs at their known positions,
   while always retaining the true permutation.

A documented caveat: ``score_combined`` only ranks the true permutation #1
once the text is long enough; on short fragments cyclic rearrangements can
outscore the truth (the same n-gram misranking noted for the K3 Monte Carlo).
Crib locking sidesteps that by constraining the search to crib-consistent
permutations rather than relying on the scoring objective alone.
"""

from __future__ import annotations

import itertools
import math
import random

import pytest

from kryptos.k4.transposition_analysis import (
    apply_columnar_permutation_encrypt,
    apply_columnar_permutation_reverse,
    score_combined,
    solve_columnar_permutation_simulated_annealing,
    solve_columnar_permutation_simulated_annealing_multi_start,
)
from kryptos.k4.transposition_constraints import search_with_multiple_cribs_positions

# Realistic-length plaintext so the scoring objective ranks the truth #1.
PLAINTEXT = (
    "THEUNITEDSTATESINTELLIGENCECOMMUNITYDISCOVEREDTHEHIDDENMESSAGE"
    "CONCEALEDWITHINTHESCULPTUREATLANGLEYVIRGINIANEARTHEHEADQUARTERS"
)
PERIOD = 7
TRUE_PERM = [3, 0, 5, 1, 6, 2, 4]


def _ciphertext() -> str:
    ct = apply_columnar_permutation_encrypt(PLAINTEXT, PERIOD, TRUE_PERM)
    # Sanity: encrypt/decrypt round-trips under the true permutation.
    assert apply_columnar_permutation_reverse(ct, PERIOD, TRUE_PERM) == PLAINTEXT
    return ct


class TestSimulatedAnnealingRecovery:
    def test_random_init_recovers_planted_plaintext(self):
        ct = _ciphertext()
        best_perm, _ = solve_columnar_permutation_simulated_annealing(
            ct, PERIOD, max_iterations=30000, rng=random.Random(0)
        )
        assert apply_columnar_permutation_reverse(ct, PERIOD, best_perm) == PLAINTEXT

    def test_true_permutation_scores_rank_one(self):
        ct = _ciphertext()
        ranked = sorted(
            (score_combined(apply_columnar_permutation_reverse(ct, PERIOD, list(p))), list(p))
            for p in itertools.permutations(range(PERIOD))
        )
        assert ranked[-1][1] == TRUE_PERM

    def test_seed_perm_at_truth_returns_truth(self):
        ct = _ciphertext()
        best_perm, best_score = solve_columnar_permutation_simulated_annealing(
            ct, PERIOD, max_iterations=20000, rng=random.Random(1), seed_perm=TRUE_PERM
        )
        # Seeded at the optimum, SA must not wander to a worse-scoring perm.
        assert apply_columnar_permutation_reverse(ct, PERIOD, best_perm) == PLAINTEXT
        assert best_score >= score_combined(PLAINTEXT) - 1e-9

    def test_seed_perm_rejects_non_permutation(self):
        ct = _ciphertext()
        with pytest.raises(ValueError, match="permutation"):
            solve_columnar_permutation_simulated_annealing(ct, PERIOD, seed_perm=[0, 0, 1, 2, 3, 4, 5])

    def test_multi_start_accepts_seed(self):
        ct = _ciphertext()
        best_perm, _ = solve_columnar_permutation_simulated_annealing_multi_start(
            ct, PERIOD, num_restarts=3, max_iterations=15000, rng=random.Random(2), seed_perm=TRUE_PERM
        )
        assert apply_columnar_permutation_reverse(ct, PERIOD, best_perm) == PLAINTEXT


class TestEarlyCribLocking:
    def test_single_crib_prunes_over_90_percent(self):
        ct = _ciphertext()
        total = math.factorial(PERIOD)  # 5040
        lang_idx = PLAINTEXT.find("LANGLEY")
        results = search_with_multiple_cribs_positions(
            ct, {"LANGLEY": [lang_idx]}, PERIOD, window=0, max_perms=total, limit=total
        )
        # Crib locking rejects all but a tiny fraction before scoring.
        assert len(results) / total < 0.10
        # And it never discards the true permutation.
        assert any(r["perm"] == tuple(TRUE_PERM) for r in results)

    def test_two_cribs_prune_further(self):
        ct = _ciphertext()
        total = math.factorial(PERIOD)
        lang_idx = PLAINTEXT.find("LANGLEY")
        disc_idx = PLAINTEXT.find("DISCOVERED")
        one = search_with_multiple_cribs_positions(
            ct, {"LANGLEY": [lang_idx]}, PERIOD, window=0, max_perms=total, limit=total
        )
        two = search_with_multiple_cribs_positions(
            ct,
            {"LANGLEY": [lang_idx], "DISCOVERED": [disc_idx]},
            PERIOD,
            window=0,
            max_perms=total,
            limit=total,
        )
        assert len(two) <= len(one)
        assert any(r["perm"] == tuple(TRUE_PERM) for r in two)

    def test_top_crib_locked_result_is_true_plaintext(self):
        ct = _ciphertext()
        total = math.factorial(PERIOD)
        lang_idx = PLAINTEXT.find("LANGLEY")
        disc_idx = PLAINTEXT.find("DISCOVERED")
        results = search_with_multiple_cribs_positions(
            ct,
            {"LANGLEY": [lang_idx], "DISCOVERED": [disc_idx]},
            PERIOD,
            window=0,
            max_perms=total,
            limit=total,
        )
        assert results, "crib lock should retain at least the true permutation"
        # Highest-scoring crib-consistent candidate is the real plaintext.
        assert results[0]["text"] == PLAINTEXT
