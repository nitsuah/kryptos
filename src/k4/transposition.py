"""Columnar transposition search utilities for K4 hypotheses."""

import itertools
import random
from collections.abc import Iterable

from .scoring import combined_plaintext_score_cached as combined_plaintext_score  # cached

# Attempt log storage
_attempt_log: list[dict] = []


def _log_attempt(cols: int, perm: tuple[int, ...], partial: float | None, final: float | None, pruned: bool) -> None:
    if len(_attempt_log) < 10000:  # cap to avoid runaway memory
        _attempt_log.append(
            {
                'cols': cols,
                'perm': perm,
                'partial_score': partial,
                'final_score': final,
                'pruned': pruned,
            },
        )


def get_transposition_attempt_log(clear: bool = False) -> list[dict]:
    """Return collected attempt log (permutation evaluations). Optionally clear after retrieval."""
    out = list(_attempt_log)
    if clear:
        _attempt_log.clear()
    return out


def apply_columnar_permutation(ciphertext: str, n_cols: int, perm: tuple[int, ...]) -> str:
    """Attempt to invert a columnar transposition given a permutation of column indices.
    Assumes ciphertext produced by reading columns top-to-bottom after permuting columns.
    This reconstruction is heuristic; for short text may be imperfect but good for scoring search.
    """
    ct = ''.join(c for c in ciphertext if c.isalpha())
    n = len(ct)
    if n_cols <= 0:
        return ct
    n_rows = (n + n_cols - 1) // n_cols
    # Approximate column lengths: first (n % n_cols) columns have n_rows, others n_rows-1
    full_cols = n % n_cols if n % n_cols != 0 else n_cols
    col_lengths = [n_rows if i < full_cols else (n_rows - 1) for i in range(n_cols)]
    # Split ciphertext into columns in permuted order
    cols: list[str] = []
    idx = 0
    for p in perm:
        L = col_lengths[p]
        cols.append(ct[idx : idx + L])
        idx += L
    original_order: list[str] = [''] * n_cols
    for read_index, p in enumerate(perm):
        original_order[p] = cols[read_index]
    plaintext_chars: list[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            cell = original_order[c]
            if r < len(cell):
                plaintext_chars.append(cell[r])
    return ''.join(plaintext_chars)


def _partial_score(text: str, length: int) -> float:
    """Score only a leading segment of text for pruning heuristics."""
    segment = text[:length]
    return combined_plaintext_score(segment)


def search_columnar(
    ciphertext: str,
    min_cols: int = 5,
    max_cols: int = 8,
    max_perms_per_width: int = 720,
    prune: bool = False,
    partial_length: int = 40,
    partial_min_score: float = -1e9,
) -> list[dict]:
    """Search columnar transposition permutations across a range of column counts.
    Factorial growth is limited by sampling permutations if necessary.
    Optional pruning: if prune=True, evaluate partial segment score and skip candidate
    if below partial_min_score.
    Returns list of dicts: {'cols': n_cols, 'perm': perm, 'score': score, 'text': plaintext}
    """
    results: list[dict] = []
    for n_cols in range(min_cols, max_cols + 1):
        all_perms_iter: Iterable[tuple[int, ...]] = itertools.permutations(range(n_cols))
        for count, perm in enumerate(all_perms_iter):
            if count >= max_perms_per_width:
                break
            pt = apply_columnar_permutation(ciphertext, n_cols, perm)
            pruned_flag = False
            if prune:
                ps = _partial_score(pt, partial_length)
                if ps < partial_min_score:
                    _log_attempt(n_cols, perm, ps, None, pruned=True)
                    pruned_flag = True
                    continue
            score = combined_plaintext_score(pt)
            _log_attempt(n_cols, perm, None if not prune else ps, score, pruned_flag)
            results.append({'cols': n_cols, 'perm': perm, 'score': score, 'text': pt})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:50]


# Adaptive search with sampling and prefix caching


def search_columnar_adaptive(
    ciphertext: str,
    min_cols: int = 5,
    max_cols: int = 8,
    sample_perms: int = 500,
    partial_length: int = 50,
    prefix_len: int = 3,
    prefix_cache_max: int = 5000,
    early_stop_threshold: float = 1500.0,
) -> list[dict]:
    """Adaptive columnar search.
    Randomly samples permutations; caches prefix partial scores; prunes low performers.
    """
    rng = random.Random(42)
    ct = ''.join(c for c in ciphertext if c.isalpha())
    all_results: list[dict] = []
    prefix_cache: dict[tuple[int, ...], float] = {}
    for n_cols in range(min_cols, max_cols + 1):
        perms = list(itertools.permutations(range(n_cols)))
        if len(perms) > sample_perms:
            perms = rng.sample(perms, sample_perms)
        for perm in perms:
            pt = apply_columnar_permutation(ct, n_cols, perm)
            partial = _partial_score(pt, partial_length)
            pref = perm[:prefix_len]
            best_pref = prefix_cache.get(pref)
            pruned_flag = False
            if best_pref is None or partial > best_pref:
                prefix_cache[pref] = partial
            else:
                if partial < (best_pref - abs(best_pref) * 0.25):
                    _log_attempt(n_cols, perm, partial, None, pruned=True)
                    pruned_flag = True
                    continue
            score = combined_plaintext_score(pt)
            _log_attempt(n_cols, perm, partial, score, pruned_flag)
            all_results.append({'cols': n_cols, 'perm': perm, 'score': score, 'partial': partial, 'text': pt})
            if score > early_stop_threshold:
                # Could log or flag; keep collecting for breadth
                pass
            if len(prefix_cache) > prefix_cache_max:
                # Simple eviction: shrink by removing lowest 20%
                sorted_items = sorted(prefix_cache.items(), key=lambda kv: kv[1], reverse=True)
                keep = int(len(sorted_items) * 0.8)
                prefix_cache = dict(sorted_items[:keep])
    all_results.sort(key=lambda r: r['score'], reverse=True)
    return all_results[:50]


__all__ = [
    'apply_columnar_permutation',
    'search_columnar',
    'search_columnar_adaptive',
    'get_transposition_attempt_log',
]
