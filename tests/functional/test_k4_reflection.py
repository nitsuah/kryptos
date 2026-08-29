"""Tests for kryptos.k4.reflection — physical front/back reflection library."""

from __future__ import annotations

from kryptos.k4 import reflection as refl
from kryptos.k4.geometry24 import COLS, ROWS


class TestShapePreserving:
    def test_identity(self):
        assert refl.identity(2, 5) == (2, 5)

    def test_flip_h_reverses_columns(self):
        assert refl.flip_h(1, 0) == (1, COLS - 1)
        assert refl.flip_h(1, COLS - 1) == (1, 0)

    def test_flip_v_reverses_rows(self):
        assert refl.flip_v(0, 3) == (ROWS - 1, 3)
        assert refl.flip_v(ROWS - 1, 3) == (0, 3)

    def test_rotate_180_is_flip_h_and_flip_v(self):
        for r in range(ROWS):
            for c in range(COLS):
                assert refl.rotate_180(r, c) == refl.flip_v(*refl.flip_h(r, c))

    def test_shape_preserving_stays_in_bounds(self):
        for name in refl.SHAPE_PRESERVING:
            fn = refl.TRANSFORMS[name]
            for r in range(ROWS):
                for c in range(COLS):
                    nr, nc = fn(r, c)
                    assert 0 <= nr < ROWS
                    assert 0 <= nc < COLS

    def test_shape_preserving_is_a_bijection(self):
        for name in refl.SHAPE_PRESERVING:
            fn = refl.TRANSFORMS[name]
            seen = {fn(r, c) for r in range(ROWS) for c in range(COLS)}
            assert len(seen) == ROWS * COLS


class TestShapeChanging:
    def test_transpose_swaps_axes(self):
        assert refl.transpose(1, 5) == (5, 1)

    def test_shape_changing_stays_in_transposed_bounds(self):
        for name in refl.SHAPE_CHANGING:
            fn = refl.TRANSFORMS[name]
            for r in range(ROWS):
                for c in range(COLS):
                    nr, nc = fn(r, c)
                    assert 0 <= nr < COLS
                    assert 0 <= nc < ROWS

    def test_shape_changing_is_a_bijection(self):
        for name in refl.SHAPE_CHANGING:
            fn = refl.TRANSFORMS[name]
            seen = {fn(r, c) for r in range(ROWS) for c in range(COLS)}
            assert len(seen) == ROWS * COLS


class TestBackMappings:
    def test_back_identity(self):
        assert refl.back_identity(2, 7) == (2, 7)

    def test_back_mirror_col_matches_brief_formula(self):
        for r in range(ROWS):
            for c in range(COLS):
                assert refl.back_mirror_col(r, c) == (r, COLS - 1 - c)

    def test_back_mirror_row_matches_brief_formula(self):
        for r in range(ROWS):
            for c in range(COLS):
                assert refl.back_mirror_row(r, c) == (ROWS - 1 - r, c)

    def test_back_mirror_both_matches_brief_formula(self):
        for r in range(ROWS):
            for c in range(COLS):
                assert refl.back_mirror_both(r, c) == (ROWS - 1 - r, COLS - 1 - c)

    def test_back_aliases_are_the_flip_family(self):
        assert refl.back_mirror_col is refl.flip_h
        assert refl.back_mirror_row is refl.flip_v
        assert refl.back_mirror_both is refl.rotate_180

    def test_transposed_equivalents_shape(self):
        for name, fn in refl.BACK_MAPPINGS.items():
            if name.endswith("_transposed"):
                nr, nc = fn(0, 0)
                assert 0 <= nr < COLS
                assert 0 <= nc < ROWS


def test_apply_transform():
    coords = [(0, 0), (1, 1)]
    result = refl.apply_transform("flip_h", coords)
    assert result == [(0, COLS - 1), (1, COLS - 2)]
