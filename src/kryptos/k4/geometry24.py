"""24-column grid geometry engine for K4 — physical/geometric pivot.

K4 is 97 characters. The Berlin World Clock provides a natural 24-position
structure, so this module tests the structural hypothesis::

    97 = (4 x 24) + 1

as a grid: 4 rows x 24 columns (96 cells) plus one remainder character. It
does *not* assume the 97th character is a null — ``remainder_mode`` lets a
caller test it as trailing content, leading content, or dropped entirely.

The grid is populated in standard row-major order (source position
``r * COLS + c``) and then *read out* along one of several named orders to
produce a permutation of the 97 source positions. That permutation is the
encrypt-direction gather:

    ciphertext[i] = plaintext[flat_indices[i]]

``apply_forward``/``apply_inverse`` apply and invert that permutation. This
is the standard columnar-transposition convention and is the shared
primitive used by :mod:`kryptos.k4.geometry_combined_sweep`.
"""

from __future__ import annotations

from collections.abc import Callable

ROWS = 4
COLS = 24
CORE_LEN = ROWS * COLS  # 96
TOTAL_LEN = CORE_LEN + 1  # 97

Coords = list[tuple[int, int]]


def _row_major(rows: int = ROWS, cols: int = COLS) -> Coords:
    return [(r, c) for r in range(rows) for c in range(cols)]


def _col_major(rows: int = ROWS, cols: int = COLS) -> Coords:
    return [(r, c) for c in range(cols) for r in range(rows)]


def _boustrophedon(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Row-wise serpentine: row 0 L->R, row 1 R->L, ... (aka "alternating row")."""
    coords: Coords = []
    for r in range(rows):
        row_cells = [(r, c) for c in range(cols)]
        coords.extend(row_cells if r % 2 == 0 else row_cells[::-1])
    return coords


def _alternating_col(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Column-wise serpentine: col 0 top->bottom, col 1 bottom->top, ..."""
    coords: Coords = []
    for c in range(cols):
        col_cells = [(r, c) for r in range(rows)]
        coords.extend(col_cells if c % 2 == 0 else col_cells[::-1])
    return coords


def _spiral(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Continuous clockwise spiral starting top-left."""
    coords: Coords = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    while top <= bottom and left <= right:
        coords.extend((top, c) for c in range(left, right + 1))
        top += 1
        coords.extend((r, right) for r in range(top, bottom + 1))
        right -= 1
        if top <= bottom:
            coords.extend((bottom, c) for c in range(right, left - 1, -1))
            bottom -= 1
        if left <= right:
            coords.extend((r, left) for r in range(bottom, top - 1, -1))
            left += 1
    return coords


def _num_rings(rows: int = ROWS, cols: int = COLS) -> int:
    return (min(rows, cols) + 1) // 2


def _ring_cells(k: int, rows: int = ROWS, cols: int = COLS) -> Coords:
    """Perimeter cells of the ring at depth ``k``, walked clockwise from top-left."""
    r0, r1 = k, rows - 1 - k
    c0, c1 = k, cols - 1 - k
    cells: Coords = [(r0, c) for c in range(c0, c1 + 1)]  # top row
    if r1 > r0:
        cells += [(r, c1) for r in range(r0 + 1, r1 + 1)]  # right column
        cells += [(r1, c) for c in range(c1 - 1, c0 - 1, -1)]  # bottom row
        if c1 > c0 and r1 > r0 + 1:
            cells += [(r, c0) for r in range(r1 - 1, r0, -1)]  # left column
    return cells


def _outside_in(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Ring-by-ring perimeter walk, outer ring first."""
    coords: Coords = []
    for k in range(_num_rings(rows, cols)):
        coords.extend(_ring_cells(k, rows, cols))
    return coords


def _center_out(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Ring-by-ring perimeter walk, innermost ring first (reverse of outside_in)."""
    coords: Coords = []
    for k in reversed(range(_num_rings(rows, cols))):
        coords.extend(_ring_cells(k, rows, cols))
    return coords


def circular_wrapped_order(offset: int = ROWS, rows: int = ROWS, cols: int = COLS) -> Coords:
    """Row-major order with a cyclic start-offset (a wrapped/circular origin)."""
    base = _row_major(rows, cols)
    offset %= len(base)
    return base[offset:] + base[:offset]


def _circular_wrapped_default(rows: int = ROWS, cols: int = COLS) -> Coords:
    """Registry entry for "circular_wrapped": a fixed, representative non-trivial
    offset (ROWS), matching the (rows, cols) -> Coords signature every other
    registry entry uses. Call ``circular_wrapped_order`` directly for arbitrary offsets.
    """
    return circular_wrapped_order(ROWS, rows, cols)


BASE_ORDERS: dict[str, Callable[[int, int], Coords]] = {
    "row_major": _row_major,
    "col_major": _col_major,
    "boustrophedon": _boustrophedon,
    "alternating_col": _alternating_col,
    "spiral": _spiral,
    "outside_in": _outside_in,
    "center_out": _center_out,
    "circular_wrapped": _circular_wrapped_default,
}

ORDER_NAMES: list[str] = [*BASE_ORDERS, *(f"{name}_reversed" for name in BASE_ORDERS)]

REMAINDER_MODES = ("trailing", "leading", "drop")


def order_coords(name: str, rows: int = ROWS, cols: int = COLS) -> Coords:
    """Return the 96-cell coordinate read-order for a registered order name."""
    if name.endswith("_reversed"):
        base_name = name[: -len("_reversed")]
        if base_name not in BASE_ORDERS:
            raise ValueError(f"Unknown order: {name}")
        return list(reversed(BASE_ORDERS[base_name](rows, cols)))
    if name not in BASE_ORDERS:
        raise ValueError(f"Unknown order: {name}")
    return BASE_ORDERS[name](rows, cols)


def coords_to_flat(
    coords: Coords,
    remainder_mode: str = "trailing",
    rows: int = ROWS,
    cols: int = COLS,
) -> list[int]:
    """Flatten a 96-cell coordinate order into a length-97 (or 96) source-index permutation.

    remainder_mode:
      "trailing" -> the 97th source position (rows*cols) is appended after the grid read.
      "leading"  -> the 97th source position is emitted first; grid cells shift +1.
      "drop"     -> the remainder is excluded entirely (tests the null hypothesis);
                    result has length rows*cols, not rows*cols+1.
    """
    flat_core = [r * cols + c for (r, c) in coords]
    if remainder_mode == "trailing":
        return [*flat_core, rows * cols]
    if remainder_mode == "leading":
        return [0, *(i + 1 for i in flat_core)]
    if remainder_mode == "drop":
        return flat_core
    raise ValueError(f"Unknown remainder_mode: {remainder_mode!r}")


def flat_indices_for_order(
    name: str,
    remainder_mode: str = "trailing",
    rows: int = ROWS,
    cols: int = COLS,
) -> list[int]:
    """Convenience wrapper: order_coords(name) -> coords_to_flat(...)."""
    return coords_to_flat(order_coords(name, rows, cols), remainder_mode, rows, cols)


def apply_forward(text: str, flat_indices: list[int]) -> str:
    """Encrypt-direction gather: out[i] = text[flat_indices[i]]."""
    return "".join(text[i] for i in flat_indices)


def apply_inverse(text: str, flat_indices: list[int]) -> str:
    """Decrypt-direction scatter: undoes apply_forward for the same flat_indices.

    ``text`` must have the same length as ``flat_indices`` (one character per
    permuted position). Returns the characters ordered by their original
    source index, i.e. ``apply_inverse(apply_forward(t, idx), idx) == t``
    whenever ``flat_indices`` covers a contiguous 0..N-1 range (true for the
    "trailing"/"leading" remainder modes).
    """
    if len(text) != len(flat_indices):
        raise ValueError(f"text length {len(text)} != flat_indices length {len(flat_indices)}")
    mapping = dict(zip(flat_indices, text, strict=True))
    return "".join(mapping[k] for k in sorted(mapping))


__all__ = [
    "BASE_ORDERS",
    "CORE_LEN",
    "COLS",
    "ORDER_NAMES",
    "REMAINDER_MODES",
    "ROWS",
    "TOTAL_LEN",
    "apply_forward",
    "apply_inverse",
    "circular_wrapped_order",
    "coords_to_flat",
    "flat_indices_for_order",
    "order_coords",
]
