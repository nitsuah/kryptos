"""Inverse transposition sweep for K4-ATTACK-2.

Strategy:
  For each candidate grid geometry (n_cols) and each column permutation P,
  apply P⁻¹ to the K4 ciphertext, then read the result using route patterns
  (ENE diagonal at 67.5°, standard columnar, spiral, etc.) and check whether
  the confirmed crib positions produce a recognisable keystream.

The sweep is deliberately separated from the crib validation logic so that
either component can be swapped or extended independently.

Grid geometries for 97 chars:
  10 cols → 10×10 (pad 3)
  7  cols → 7×14  (pad 1)   [or 14×7 transposed]
  8  cols → 8×13  (pad 7)

These are the three grids recommended in the K4-T1 physical-geometric spec.
"""

from __future__ import annotations

from itertools import permutations
from typing import Any

from .keystream_validator import K4_CRIBS, crib_hit_count, keystream_summary
from .transposition_analysis import apply_columnar_permutation_reverse
from .transposition_routes import _read_diagonal, _read_spiral, read_ene_diagonal, to_grid

# Grid sizes to sweep (n_cols for 97-char K4)
K4_GRID_GEOMETRIES: list[int] = [7, 8, 10]

# Reading routes to apply after inversion
SWEEP_ROUTES: dict[str, Any] = {
    "ene_diagonal": lambda text, cols: read_ene_diagonal(text, cols, angle_tan=2.414),
    "columnar": lambda text, cols: text,  # after P⁻¹, read straight through
    "spiral": lambda text, cols: "".join(_read_spiral(to_grid(text, cols))),
    "diagonal_45": lambda text, cols: "".join(_read_diagonal(to_grid(text, cols))),
}


def invert_permutation(perm: tuple[int, ...]) -> tuple[int, ...]:
    """Return the inverse of a permutation (as a tuple of 0-based ints)."""
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return tuple(inv)


def sweep_grid(
    ciphertext: str,
    n_cols: int,
    routes: tuple[str, ...] = ("ene_diagonal", "columnar"),
    min_hits: int = 1,
    max_perms: int | None = None,
    cribs: dict | None = None,
) -> list[dict[str, Any]]:
    """Enumerate column permutations for a given grid width, apply P⁻¹, then validate.

    Args:
        ciphertext:  Raw K4 ciphertext (non-alpha stripped internally).
        n_cols:      Number of columns for the columnar grid.
        routes:      Which reading routes to test after inversion.
        min_hits:    Minimum number of crib hits to include in results.
        max_perms:   Cap on permutations tested (None = exhaustive).
        cribs:       Crib dict to validate against (default: K4_CRIBS).

    Returns:
        List of result dicts sorted by crib_hits desc then by cols asc.
        Each dict has: n_cols, perm, inv_perm, route, crib_hits, crib_summary,
        candidate_text.
    """
    if cribs is None:
        cribs = K4_CRIBS

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    results: list[dict[str, Any]] = []

    perm_gen = permutations(range(n_cols))
    count = 0
    for perm in perm_gen:
        if max_perms is not None and count >= max_perms:
            break
        count += 1

        inverted = apply_columnar_permutation_reverse(ct, n_cols, list(perm))

        for route_name in routes:
            route_fn = SWEEP_ROUTES.get(route_name)
            if route_fn is None:
                continue
            candidate = route_fn(inverted, n_cols)
            hits = crib_hit_count(candidate, cribs=cribs)
            if hits >= min_hits:
                results.append(
                    {
                        "n_cols": n_cols,
                        "perm": perm,
                        "inv_perm": invert_permutation(perm),
                        "route": route_name,
                        "crib_hits": hits,
                        "crib_summary": keystream_summary(candidate),
                        "candidate_text": candidate,
                    }
                )

    results.sort(key=lambda r: (-r["crib_hits"], r["n_cols"]))
    return results


def full_sweep(
    ciphertext: str,
    grid_sizes: list[int] | None = None,
    routes: tuple[str, ...] = ("ene_diagonal", "columnar"),
    min_hits: int = 1,
    max_perms_per_grid: int | None = None,
    cribs: dict | None = None,
) -> dict[str, Any]:
    """Run sweep across all K4 grid geometries.

    Args:
        ciphertext:          K4 ciphertext.
        grid_sizes:          Column counts to test (default: K4_GRID_GEOMETRIES).
        routes:              Reading routes to apply after inversion.
        min_hits:            Minimum crib hits to surface in results.
        max_perms_per_grid:  Cap permutations per grid size (None = exhaustive,
                             WARNING: exhaustive is factorial — use a cap for large n_cols).
        cribs:               Crib dict (default: K4_CRIBS).

    Returns:
        Dict with 'results' (all hits across all grids) and 'best' (top result or None).
    """
    if grid_sizes is None:
        grid_sizes = K4_GRID_GEOMETRIES

    all_results: list[dict[str, Any]] = []
    for n_cols in grid_sizes:
        hits = sweep_grid(
            ciphertext,
            n_cols=n_cols,
            routes=routes,
            min_hits=min_hits,
            max_perms=max_perms_per_grid,
            cribs=cribs,
        )
        all_results.extend(hits)

    all_results.sort(key=lambda r: (-r["crib_hits"], r["n_cols"]))
    return {
        "results": all_results,
        "best": all_results[0] if all_results else None,
        "grid_sizes_tested": grid_sizes,
        "total_hits": len(all_results),
    }


__all__ = [
    "K4_GRID_GEOMETRIES",
    "SWEEP_ROUTES",
    "invert_permutation",
    "sweep_grid",
    "full_sweep",
]
