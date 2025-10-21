"""Route / pattern transposition variants (spiral, boustrophedon, diagonal).

Provides functions to place ciphertext into a rectangular grid by column count and
read out using various traversal patterns to generate candidate plaintexts.
"""
from __future__ import annotations
from collections.abc import Callable
from .scoring import combined_plaintext_score_cached as combined_plaintext_score

def _to_grid(text: str, cols: int) -> list[list[str]]:
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if cols <= 0:
        return []
    rows = (len(seq) + cols - 1) // cols
    grid = [[''] * cols for _ in range(rows)]
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx < len(seq):
                grid[r][c] = seq[idx]
                idx += 1
    return grid

def _read_spiral(grid: list[list[str]]) -> str:
    if not grid:
        return ''
    top, left = 0, 0
    bottom, right = len(grid) - 1, len(grid[0]) - 1
    out: list[str] = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            out.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(grid[r][left])
            left += 1
    return ''.join(out)

def _read_boustrophedon(grid: list[list[str]]) -> str:
    out: list[str] = []
    for r, row in enumerate(grid):
        if r % 2 == 0:
            out.extend(row)
        else:
            out.extend(reversed(row))
    return ''.join(out)

def _read_diagonal(grid: list[list[str]]) -> str:
    if not grid:
        return ''
    rows = len(grid)
    cols = len(grid[0])
    out: list[str] = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = d - r
            if 0 <= c < cols:
                out.append(grid[r][c])
    return ''.join(out)

_ROUTE_FUNCS: dict[str, Callable[[list[list[str]]], str]] = {
    'spiral': _read_spiral,
    'boustrophedon': _read_boustrophedon,
    'diagonal': _read_diagonal,
}

def generate_route_variants(
        ciphertext: str,
        cols_min: int = 5,
        cols_max: int = 8,
        routes: tuple[str, ...] = (
            'spiral',
            'boustrophedon',
            'diagonal',
        ),
) -> list[dict]:
    """
    Generate transposition route variants of the given ciphertext.

    Args:
        ciphertext (str): The input ciphertext to be arranged and read out.
        cols_min (int, optional): Minimum number of columns for the grid. Defaults to 5.
        cols_max (int, optional): Maximum number of columns for the grid. Defaults to 8.
        routes (Tuple[str, ...], optional): Traversal patterns to use. Defaults to
            ('spiral', 'boustrophedon', 'diagonal').

    Returns:
        List[Dict]: A list of dictionaries, each with the following keys:
            - 'route' (str): The name of the traversal pattern used.
            - 'cols' (int): The number of columns in the grid.
            - 'score' (float): The score assigned to the resulting plaintext.
            - 'text' (str): The resulting plaintext after applying the route.
    """
    results: list[dict] = []
    for cols in range(cols_min, cols_max + 1):
        grid = _to_grid(ciphertext, cols)
        for route in routes:
            reader = _ROUTE_FUNCS.get(route)
            if not reader:
                continue
            pt = reader(grid)
            score = combined_plaintext_score(pt)
            results.append({
                'route': route,
                'cols': cols,
                'score': score,
                'text': pt,
            })
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['generate_route_variants']
