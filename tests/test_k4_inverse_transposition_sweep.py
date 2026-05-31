"""Tests for inverse transposition sweep and ENE diagonal reader."""

import pytest

from kryptos.k4.inverse_transposition_sweep import (
    K4_GRID_GEOMETRIES,
    SWEEP_ROUTES,
    full_sweep,
    invert_permutation,
    sweep_grid,
)
from kryptos.k4.transposition_routes import read_ene_diagonal, to_grid

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


class TestInvertPermutation:
    def test_identity(self):
        assert invert_permutation((0, 1, 2, 3)) == (0, 1, 2, 3)

    def test_reversal(self):
        assert invert_permutation((3, 2, 1, 0)) == (3, 2, 1, 0)

    def test_simple_rotation(self):
        perm = (1, 2, 3, 0)
        inv = invert_permutation(perm)
        # composing perm with its inverse should give identity
        result = tuple(perm[inv[i]] for i in range(4))
        assert result == (0, 1, 2, 3)

    def test_roundtrip(self):
        perm = (2, 0, 3, 1)
        inv = invert_permutation(perm)
        assert invert_permutation(inv) == perm


class TestENEDiagonalReader:
    def test_returns_same_length(self):
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = read_ene_diagonal(text, cols=5)
        assert len(result) == len(text)

    def test_contains_all_chars(self):
        text = "ABCDEFGHIJ"
        result = read_ene_diagonal(text, cols=5)
        assert sorted(result) == sorted(text)

    def test_different_from_original(self):
        # ENE reading should reorder, not leave identical to columnar fill
        text = K4
        result = read_ene_diagonal(text, cols=10)
        assert result != text
        assert len(result) == len(text)

    def test_45_degree_different_from_ene(self):
        text = K4
        ene = read_ene_diagonal(text, cols=10, angle_tan=2.414)
        std = read_ene_diagonal(text, cols=10, angle_tan=1.0)
        assert ene != std

    def test_to_grid_shape(self):
        grid = to_grid(K4, cols=10)
        assert len(grid) == 10       # ceil(97/10) = 10
        assert len(grid[0]) == 10
        # last row may have trailing empty strings
        total_filled = sum(1 for row in grid for cell in row if cell)
        assert total_filled == len(K4)


class TestSweepGrid:
    def test_returns_list(self):
        results = sweep_grid(K4, n_cols=4, max_perms=24, min_hits=0)
        assert isinstance(results, list)

    def test_each_result_has_required_keys(self):
        results = sweep_grid(K4, n_cols=4, max_perms=6, min_hits=0)
        for r in results:
            assert "n_cols" in r
            assert "perm" in r
            assert "crib_hits" in r
            assert "candidate_text" in r
            assert "route" in r

    def test_sorted_by_hits_desc(self):
        results = sweep_grid(K4, n_cols=4, max_perms=24, min_hits=0)
        hits = [r["crib_hits"] for r in results]
        assert hits == sorted(hits, reverse=True)

    def test_min_hits_filter(self):
        # With min_hits=999 nothing passes
        results = sweep_grid(K4, n_cols=4, max_perms=24, min_hits=999)
        assert results == []

    def test_identity_perm_returns_k4_crib_hits(self):
        # Identity permutation: P⁻¹ applied to K4 is K4 itself
        # Columnar route just reads it straight → should get 4 crib hits
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt
        # Build a ciphertext from K4 using a known perm; sweep should recover K4 (4 hits)
        test_perm = [1, 0, 2, 3]
        transposed = apply_columnar_permutation_encrypt(K4, 4, test_perm)
        results = sweep_grid(
            transposed, n_cols=4, routes=("columnar",),
            min_hits=4, max_perms=None
        )
        assert len(results) >= 1, "Sweep must find at least one 4-crib-hit candidate"
        assert results[0]["crib_hits"] == 4
        # All results must have valid crib range
        all_results = sweep_grid(K4, n_cols=4, max_perms=12, min_hits=0)
        assert all(0 <= r["crib_hits"] <= 4 for r in all_results)

    def test_max_perms_cap(self):
        results = sweep_grid(K4, n_cols=5, max_perms=10, min_hits=0)
        # 5! = 120 possible perms × 2 routes = 240, but we capped at 10 perms
        assert len(results) <= 10 * 2  # ≤ max_perms × len(default routes)


class TestFullSweep:
    def test_returns_expected_structure(self):
        result = full_sweep(K4, grid_sizes=[4], max_perms_per_grid=6)
        assert "results" in result
        assert "best" in result
        assert "total_hits" in result

    def test_grid_sizes_tested_recorded(self):
        result = full_sweep(K4, grid_sizes=[4, 5], max_perms_per_grid=2)
        assert result["grid_sizes_tested"] == [4, 5]

    def test_no_results_when_min_hits_too_high(self):
        result = full_sweep(K4, grid_sizes=[4], max_perms_per_grid=2, min_hits=999)
        assert result["best"] is None
        assert result["results"] == []

    def test_k4_grid_geometries_constant(self):
        assert K4_GRID_GEOMETRIES == [7, 8, 10]
