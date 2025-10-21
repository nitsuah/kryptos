"""Route / pattern transposition variants (spiral, boustrophedon, diagonal).

Provides functions to place ciphertext into a rectangular grid by column count and
read out using various traversal patterns to generate candidate plaintexts.
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Callable
from .scoring import combined_plaintext_score_cached as combined_plaintext_score

def _to_grid(text: str, cols: int) -> List[List[str]]:
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

def _read_spiral(grid: List[List[str]]) -> str:
    if not grid:
        return ''
    top, left = 0, 0
    bottom, right = len(grid) - 1, len(grid[0]) - 1
    out: List[str] = []
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

def _read_boustrophedon(grid: List[List[str]]) -> str:
    out: List[str] = []
    for r, row in enumerate(grid):
        if r % 2 == 0:
            out.extend(row)
        else:
            out.extend(reversed(row))
    return ''.join(out)

def _read_diagonal(grid: List[List[str]]) -> str:
    if not grid:
        return ''
    rows = len(grid)
    cols = len(grid[0])
    out: List[str] = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = d - r
            if 0 <= c < cols:
                out.append(grid[r][c])
    return ''.join(out)

_ROUTE_FUNCS: Dict[str, Callable[[List[List[str]]], str]] = {
    'spiral': _read_spiral,
    'boustrophedon': _read_boustrophedon,
    'diagonal': _read_diagonal,
}

def generate_route_variants(ciphertext: str, cols_min: int = 5, cols_max: int = 8, routes: Tuple[str, ...] = ('spiral','boustrophedon','diagonal')) -> List[Dict]:
    results: List[Dict] = []
    for cols in range(cols_min, cols_max + 1):
        grid = _to_grid(ciphertext, cols)
        for route in routes:
            reader = _ROUTE_FUNCS.get(route)
            if not reader:
                continue
            pt = reader(grid)
            score = combined_plaintext_score(pt)
            results.append({'route': route, 'cols': cols, 'score': score, 'text': pt})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['generate_route_variants']
