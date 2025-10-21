"""Columnar transposition search utilities for K4 hypotheses."""
from typing import List, Tuple, Iterable, Dict
import itertools
import random
from .scoring import combined_plaintext_score_cached as combined_plaintext_score  # cached

def apply_columnar_permutation(ciphertext: str, n_cols: int, perm: Tuple[int, ...]) -> str:
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
    cols: List[str] = []
    idx = 0
    for p in perm:
        L = col_lengths[p]
        cols.append(ct[idx:idx+L])
        idx += L
    # Initialize original_order with empty strings instead of None
    original_order: List[str] = [''] * n_cols
    for read_index, p in enumerate(perm):
        original_order[p] = cols[read_index]
    plaintext_chars: List[str] = []
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
    partial_min_score: float = -1e9
) -> List[Dict]:
    """Search columnar transposition permutations across a range of column counts.
    Factorial growth is limited by sampling permutations if necessary.
    Optional pruning: if prune=True, evaluate partial segment score and skip candidate
    if below partial_min_score.
    Returns list of dicts: {'cols': n_cols, 'perm': perm, 'score': score, 'text': plaintext}
    """
    results: List[Dict] = []
    for n_cols in range(min_cols, max_cols + 1):
        all_perms_iter: Iterable[Tuple[int,...]] = itertools.permutations(range(n_cols))
        for count, perm in enumerate(all_perms_iter):
            if count >= max_perms_per_width:
                break
            pt = apply_columnar_permutation(ciphertext, n_cols, perm)
            if prune:
                ps = _partial_score(pt, partial_length)
                if ps < partial_min_score:
                    continue
            score = combined_plaintext_score(pt)
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
    early_stop_threshold: float = 1500.0
) -> List[Dict]:
    """Adaptive columnar search.
    - Randomly samples permutations for each width (sample_perms)
    - Uses prefix (first prefix_len indices of permutation) to cache best partial scores
    - If partial score for a sampled permutation is far below cached best for its prefix, skip full scoring
    - Early stop: if a candidate exceeds early_stop_threshold, still continue gathering but threshold could inform future heuristics
    Returns top 50 scored candidates across all widths.
    """
    rng = random.Random(42)
    ct = ''.join(c for c in ciphertext if c.isalpha())
    all_results: List[Dict] = []
    prefix_cache: Dict[Tuple[int,...], float] = {}
    for n_cols in range(min_cols, max_cols + 1):
        perms = list(itertools.permutations(range(n_cols)))
        if len(perms) > sample_perms:
            perms = rng.sample(perms, sample_perms)
        for perm in perms:
            pt = apply_columnar_permutation(ct, n_cols, perm)
            partial = _partial_score(pt, partial_length)
            pref = perm[:prefix_len]
            best_pref = prefix_cache.get(pref)
            if best_pref is None or partial > best_pref:
                prefix_cache[pref] = partial
            else:
                # If partial too low compared to best prefix score, skip
                if partial < (best_pref - abs(best_pref) * 0.25):
                    continue
            score = combined_plaintext_score(pt)
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

__all__ = ['apply_columnar_permutation', 'search_columnar', 'search_columnar_adaptive']
