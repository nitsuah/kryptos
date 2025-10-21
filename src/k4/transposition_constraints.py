"""Constraint-based columnar transposition solver prototype (crib anchoring)."""
from __future__ import annotations
from typing import List, Tuple, Dict
import itertools
from .scoring import combined_plaintext_score
from .cribs import normalize_cipher

def _column_lengths(n: int, n_cols: int) -> List[int]:
    n_rows = (n + n_cols - 1) // n_cols
    full_cols = n % n_cols if n % n_cols != 0 else n_cols
    return [n_rows if i < full_cols else (n_rows - 1) for i in range(n_cols)]

def invert_columnar(ciphertext: str, n_cols: int, perm: Tuple[int, ...]) -> str:
    """Invert columnar transposition with given column permutation."""
    ct = normalize_cipher(ciphertext)
    n = len(ct)
    col_lengths = _column_lengths(n, n_cols)
    cols: List[str] = []
    idx = 0
    for p in perm:
        L = col_lengths[p]
        cols.append(ct[idx:idx+L])
        idx += L
    original: List[str] = [''] * n_cols
    for read_idx, p in enumerate(perm):
        original[p] = cols[read_idx]
    n_rows = max(len(c) for c in original)
    out: List[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            col = original[c]
            if r < len(col):
                out.append(col[r])
    return ''.join(out)

def search_with_crib(ciphertext: str, crib: str, n_cols: int, max_perms: int = 1000) -> List[Dict]:
    """Search permutations where decrypted text contains crib substring.
    Returns top results sorted by score.
    """
    ct = normalize_cipher(ciphertext)
    target = normalize_cipher(crib)
    perms_iter = itertools.permutations(range(n_cols))
    results: List[Dict] = []
    for count, perm in enumerate(perms_iter):
        if count >= max_perms:
            break
        pt = invert_columnar(ct, n_cols, perm)
        if target in pt:
            score = combined_plaintext_score(pt)
            results.append({'perm': perm, 'score': score, 'text': pt})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:25]

def search_with_crib_at_position(
    ciphertext: str,
    crib: str,
    n_cols: int,
    expected_index: int,
    window: int = 5,
    max_perms: int = 2000
) -> List[Dict]:
    """Search permutations where decrypted text places crib starting within expected_index ± window.
    Returns top scored matches.
    """
    ct = normalize_cipher(ciphertext)
    target = normalize_cipher(crib)
    perms_iter = itertools.permutations(range(n_cols))
    results: List[Dict] = []
    for count, perm in enumerate(perms_iter):
        if count >= max_perms:
            break
        pt = invert_columnar(ct, n_cols, perm)
        idx = pt.find(target)
        if idx != -1 and abs(idx - expected_index) <= window:
            score = combined_plaintext_score(pt)
            results.append({'perm': perm, 'score': score, 'text': pt, 'start_idx': idx})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:25]

__all__ = ['invert_columnar','search_with_crib','search_with_crib_at_position']
