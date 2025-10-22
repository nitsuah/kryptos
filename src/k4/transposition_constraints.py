"""Constraint-based columnar transposition solver prototype (crib anchoring)."""

from __future__ import annotations

import itertools
from collections.abc import Sequence

from .cribs import normalize_cipher
from .scoring import combined_plaintext_score_cached as combined_plaintext_score
from .scoring import positional_crib_bonus


def _column_lengths(n: int, n_cols: int) -> list[int]:
    n_rows = (n + n_cols - 1) // n_cols
    full_cols = n % n_cols if n % n_cols != 0 else n_cols
    return [n_rows if i < full_cols else (n_rows - 1) for i in range(n_cols)]


def invert_columnar(ciphertext: str, n_cols: int, perm: tuple[int, ...]) -> str:
    """Invert columnar transposition with given column permutation."""
    ct = normalize_cipher(ciphertext)
    n = len(ct)
    col_lengths = _column_lengths(n, n_cols)
    cols: list[str] = []
    idx = 0
    for p in perm:
        L = col_lengths[p]
        cols.append(ct[idx : idx + L])
        idx += L
    original: list[str] = [''] * n_cols
    for read_idx, p in enumerate(perm):
        original[p] = cols[read_idx]
    n_rows = max(len(c) for c in original)
    out: list[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            col = original[c]
            if r < len(col):
                out.append(col[r])
    return ''.join(out)


def search_with_crib(ciphertext: str, crib: str, n_cols: int, max_perms: int = 1000) -> list[dict]:
    """Search permutations where decrypted text contains crib substring.
    Returns top results sorted by score.
    """
    ct = normalize_cipher(ciphertext)
    target = normalize_cipher(crib)
    perms_iter = itertools.permutations(range(n_cols))
    results: list[dict] = []
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
    max_perms: int = 2000,
) -> list[dict]:
    """Search permutations where decrypted text places crib starting within expected_index ± window.
    Returns top scored matches.
    """
    ct = normalize_cipher(ciphertext)
    target = normalize_cipher(crib)
    perms_iter = itertools.permutations(range(n_cols))
    results: list[dict] = []
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


# --- New: multi-crib positional anchoring ----------------------------------


def search_with_multiple_cribs_positions(
    ciphertext: str,
    positional_cribs: dict[str, Sequence[int]],
    n_cols: int,
    window: int = 5,
    max_perms: int = 5000,
    limit: int = 50,
) -> list[dict]:
    """Search permutations where all provided cribs appear within any of their expected indices ± window.
    positional_cribs: mapping crib -> iterable of expected start indices (0-based).
    Adds positional bonus to score via positional_crib_bonus.
    Returns up to limit best matches sorted by combined score.
    """
    if not positional_cribs:
        return []
    ct = normalize_cipher(ciphertext)
    crib_norm_map: dict[str, str] = {crib.upper(): normalize_cipher(crib) for crib in positional_cribs}
    perms_iter = itertools.permutations(range(n_cols))
    results: list[dict] = []
    for count, perm in enumerate(perms_iter):
        if count >= max_perms:
            break
        pt = invert_columnar(ct, n_cols, perm)
        # Check each crib for at least one occurrence within positional window
        all_ok = True
        occurrences: dict[str, int] = {}
        for crib, expected_positions in positional_cribs.items():
            target = crib_norm_map[crib.upper()]
            if not target:
                continue
            # find all occurrences
            starts: list[int] = []
            idx = pt.find(target)
            while idx != -1:
                starts.append(idx)
                idx = pt.find(target, idx + 1)
            if not starts:
                all_ok = False
                break
            # verify any occurrence near expected positions
            matched_pos = None
            for s in starts:
                if expected_positions and min(abs(s - ep) for ep in expected_positions) <= window:
                    matched_pos = s
                    break
            if matched_pos is None:
                all_ok = False
                break
            occurrences[crib.upper()] = matched_pos
        if not all_ok:
            continue
        base_score = combined_plaintext_score(pt)
        pos_bonus = positional_crib_bonus(pt, positional_cribs, window)
        score = base_score + pos_bonus
        results.append(
            {
                'perm': perm,
                'score': score,
                'text': pt,
                'positions': occurrences,
                'pos_bonus': pos_bonus,
            },
        )
    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:limit]


__all__ = [
    'invert_columnar',
    'search_with_crib',
    'search_with_crib_at_position',
    'search_with_multiple_cribs_positions',
]
