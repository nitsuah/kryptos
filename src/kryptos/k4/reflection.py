"""Physical front/back reflection library for K4.

The sculpture has a right-hand copper panel with K4 ciphertext on the front
and the Vigenere tableau on the reverse. This module implements the
coordinate transforms needed to test "physical reflection transforms the
coordinate system used to read the second layer" as a hypothesis distinct
from merely reversing the ciphertext string.

Eight non-redundant coordinate transforms cover the full space the research
brief lists (several of its named operations — e.g. "reverse rows" and
"vertical flip" — are the same transform under different names; they are not
duplicated here). Four are shape-preserving (map an R x C grid back onto
itself) and compose cleanly into :mod:`kryptos.k4.geometry_combined_sweep`'s
permutation pipeline; the other four are shape-changing (transpose family,
R x C -> C x R) and are kept as standalone, fully-tested primitives.

The brief's front/back formulas — ``back(row, col)``, ``back(row, 23-col)``,
``back(3-row, col)``, ``back(3-row, 23-col)``, and their transposed
equivalents — turn out to be exactly this module's identity/flip_h/flip_v/
rotate_180 family (and their transposed counterparts). ``back_*`` names are
provided as literal aliases so callers can use the brief's own vocabulary.
"""

from __future__ import annotations

from collections.abc import Callable

from .geometry24 import COLS, ROWS

Coord = tuple[int, int]
Transform = Callable[[int, int], Coord]


def identity(r: int, c: int) -> Coord:
    return (r, c)


def flip_h(r: int, c: int) -> Coord:
    """Mirror left-right (reverse each row's content)."""
    return (r, COLS - 1 - c)


def flip_v(r: int, c: int) -> Coord:
    """Mirror top-bottom (reverse row order)."""
    return (ROWS - 1 - r, c)


def rotate_180(r: int, c: int) -> Coord:
    return (ROWS - 1 - r, COLS - 1 - c)


def transpose(r: int, c: int) -> Coord:
    """Swap axes: R x C -> C x R."""
    return (c, r)


def anti_transpose(r: int, c: int) -> Coord:
    """Reflect across the anti-diagonal: R x C -> C x R."""
    return (COLS - 1 - c, ROWS - 1 - r)


def flip_h_then_transpose(r: int, c: int) -> Coord:
    return transpose(*flip_h(r, c))


def flip_v_then_transpose(r: int, c: int) -> Coord:
    return transpose(*flip_v(r, c))


TRANSFORMS: dict[str, Transform] = {
    "identity": identity,
    "flip_h": flip_h,
    "flip_v": flip_v,
    "rotate_180": rotate_180,
    "transpose": transpose,
    "anti_transpose": anti_transpose,
    "flip_h_then_transpose": flip_h_then_transpose,
    "flip_v_then_transpose": flip_v_then_transpose,
}

# Shape-preserving transforms (R x C -> R x C) — the set the combined sweep
# composes with fill orders and column rotations without a shape mismatch.
SHAPE_PRESERVING: list[str] = ["identity", "flip_h", "flip_v", "rotate_180"]

# Shape-changing (transpose family, R x C -> C x R).
SHAPE_CHANGING: list[str] = ["transpose", "anti_transpose", "flip_h_then_transpose", "flip_v_then_transpose"]

# Literal aliases matching the research brief's own naming, per its formulas:
#   back(row, col), back(row, 23-col), back(3-row, col), back(3-row, 23-col)
back_identity = identity
back_mirror_col = flip_h  # back(row, COLS-1-col)
back_mirror_row = flip_v  # back(ROWS-1-row, col)
back_mirror_both = rotate_180  # back(ROWS-1-row, COLS-1-col)

# ... and their transposed equivalents.
back_identity_transposed = transpose
back_mirror_col_transposed = flip_h_then_transpose
back_mirror_row_transposed = flip_v_then_transpose
back_mirror_both_transposed = anti_transpose

BACK_MAPPINGS: dict[str, Transform] = {
    "back_identity": back_identity,
    "back_mirror_col": back_mirror_col,
    "back_mirror_row": back_mirror_row,
    "back_mirror_both": back_mirror_both,
    "back_identity_transposed": back_identity_transposed,
    "back_mirror_col_transposed": back_mirror_col_transposed,
    "back_mirror_row_transposed": back_mirror_row_transposed,
    "back_mirror_both_transposed": back_mirror_both_transposed,
}


def apply_transform(name: str, coords: list[Coord]) -> list[Coord]:
    """Apply a registered transform to a list of (row, col) coordinates."""
    fn = TRANSFORMS[name]
    return [fn(r, c) for (r, c) in coords]


__all__ = [
    "BACK_MAPPINGS",
    "SHAPE_CHANGING",
    "SHAPE_PRESERVING",
    "TRANSFORMS",
    "anti_transpose",
    "apply_transform",
    "back_identity",
    "back_identity_transposed",
    "back_mirror_both",
    "back_mirror_both_transposed",
    "back_mirror_col",
    "back_mirror_col_transposed",
    "back_mirror_row",
    "back_mirror_row_transposed",
    "flip_h",
    "flip_h_then_transpose",
    "flip_v",
    "flip_v_then_transpose",
    "identity",
    "rotate_180",
    "transpose",
]
