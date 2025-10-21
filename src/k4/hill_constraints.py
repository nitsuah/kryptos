"""Constrained Hill cipher key solving using known crib pairs (BERLIN/CLOCK)."""
from __future__ import annotations
from itertools import combinations, permutations
from .hill_cipher import solve_2x2_key, hill_decrypt, matrix_inv_mod, ALPHABET
from .scoring import combined_plaintext_score_cached as combined_plaintext_score  # cached

# Example known cribs (plaintext -> cipher segment) from Kryptos K4 clues
KNOWN_CRIBS = {
    'BERLIN': 'NYPVTT',
    'CLOCK': 'MZFPK',
}

_cache_holder: dict[str, list[dict]] = {}
_hill_attempts: list[dict] = []

def get_hill_attempt_log(clear: bool = False) -> list[dict]:
    out = list(_hill_attempts)
    if clear:
        _hill_attempts.clear()
    return out

# --- 3x3 helpers (refined) -------------------------------------------------

def _assemble_3x3_variants(seq: str) -> list[list[list[int]]]:
    """Return multiple 3x3 matrix assemblies from a 9-letter sequence.
    Strategies:
    - row: fill rows left->right (default)
    - col: fill columns top->bottom
    - diag: place letters along diagonals (remaining fill row-major)
    Deduplicate identical matrices.
    """
    seq = ''.join(ch for ch in seq.upper() if ch.isalpha())
    if len(seq) < 9:
        return []
    letters = seq[:9]
    variants: list[list[list[int]]] = []
    seen: set[tuple[int, ...]] = set()

    # row-major
    row = [[ALPHABET.index(letters[r*3 + c]) for c in range(3)] for r in range(3)]
    flat = tuple(v for rr in row for v in rr)
    variants.append(row)
    seen.add(flat)

    # column-major
    col_mat = [[0]*3 for _ in range(3)]
    idx = 0
    for c in range(3):
        for r in range(3):
            col_mat[r][c] = ALPHABET.index(letters[idx])
            idx += 1
    flat = tuple(v for rr in col_mat for v in rr)
    if flat not in seen:
        variants.append(col_mat)
        seen.add(flat)

    # diagonal emphasis (first 3 main diag, next 2 anti-diag (excluding center), rest fill)
    diag_mat = [[-1] * 3 for _ in range(3)]  # use -1 sentinel
    assigned: set[tuple[int, int]] = set()
    # main diagonal (3 cells)
    for i, (r, c) in enumerate([(0, 0), (1, 1), (2, 2)]):
        diag_mat[r][c] = ALPHABET.index(letters[i])
        assigned.add((r, c))
    # anti-diagonal excluding center (2 cells)
    for j, (r, c) in enumerate([(0, 2), (2, 0)], start=3):
        diag_mat[r][c] = ALPHABET.index(letters[j])
        assigned.add((r, c))
    # fill remaining cells row-major with remaining letters
    fill_idx = 5
    for r in range(3):
        for c in range(3):
            if (r, c) not in assigned:
                diag_mat[r][c] = ALPHABET.index(letters[fill_idx])
                fill_idx += 1
    flat = tuple(v for rr in diag_mat for v in rr)
    if flat not in seen:
        variants.append(diag_mat)
        seen.add(flat)

    return variants

def _solve_3x3_keys(plain: str, cipher: str) -> list[list[list[int]]]:
    """Attempt to derive 3x3 keys from concatenated 9-letter plain/cipher slices using multiple assemblies.
    Returns list of invertible key matrices (may be empty)."""
    p = ''.join(ch for ch in plain.upper() if ch.isalpha())
    c = ''.join(ch for ch in cipher.upper() if ch.isalpha())
    if len(p) < 9 or len(c) < 9:
        return []
    p = p[:9]
    c = c[:9]
    P_variants = _assemble_3x3_variants(p)
    C_variants = _assemble_3x3_variants(c)
    keys: list[list[list[int]]] = []
    for Pv in P_variants:
        Pinv = matrix_inv_mod(Pv)
        if Pinv is None:
            continue
        for Cv in C_variants:
            K: list[list[int]] = []
            for r in range(3):
                row: list[int] = []
                for col in range(3):
                    val = 0
                    for k in range(3):
                        val += Cv[r][k] * Pinv[k][col]
                    row.append(val % 26)
                K.append(row)
            if matrix_inv_mod(K) is not None:
                flat = tuple(v for row in K for v in row)
                if flat not in {tuple(v for row in kk for v in row) for kk in keys}:
                    keys.append(K)
    return keys

# --- 3x3 candidate generator (orders + sliding windows refined) ------------

def _generate_3x3_candidates(cribs: dict[str, str]) -> list[dict]:
    items = list(cribs.items())
    results: list[dict] = []
    seen: set[tuple[int, ...]] = set()
    for order in permutations(items, len(items)):
        plain_concat = ''.join(p for p, _ in order)
        cipher_concat = ''.join(c for _, c in order)
        max_len = min(len(plain_concat), len(cipher_concat))
        if max_len < 9:
            continue
        # all overlapping 9-char windows
        for start in range(0, max_len - 9 + 1):
            p_slice = plain_concat[start:start+9]
            c_slice = cipher_concat[start:start+9]
            keys = _solve_3x3_keys(p_slice, c_slice)
            for k in keys:
                flat = tuple(v for row in k for v in row)
                if flat in seen:
                    continue
                seen.add(flat)
                order_tag = '+'.join(p for p, _ in order)
                results.append({'key': k, 'source': f'trial3x3:{order_tag}:win{start}', 'size': 3})
    return results

# --- Public API --------------------------------------------------------------

def derive_candidate_keys() -> list[dict]:
    """Derive candidate 2x2 and refined 3x3 Hill cipher keys from crib segments.
    Generates single/pair 2x2 keys and multiple window/order 3x3 heuristic keys.
    Caches results.
    """
    if 'keys' in _cache_holder:
        return _cache_holder['keys']
    keys: list[dict] = []
    # Single cribs (2x2)
    for plain, cipher in KNOWN_CRIBS.items():
        k = solve_2x2_key(plain, cipher)
        if k:
            keys.append({'key': k, 'source': f'single:{plain}', 'size': 2})
    # Pairwise combinations (2x2)
    crib_items = list(KNOWN_CRIBS.items())
    for (p1, c1), (p2, c2) in combinations(crib_items, 2):
        plain_block = (p1[:2] + p2[:2])
        cipher_block = (c1[:2] + c2[:2])
        k2 = solve_2x2_key(plain_block, cipher_block)
        if k2:
            keys.append({'key': k2, 'source': f'pair:{p1}+{p2}', 'size': 2})
    # Expanded refined 3x3 heuristic candidates
    keys.extend(_generate_3x3_candidates(KNOWN_CRIBS))
    _cache_holder['keys'] = keys
    return keys

def decrypt_and_score(
    ciphertext: str,
    prune_3x3: bool = True,
    partial_len: int = 60,
    partial_min: float = -800.0,
) -> list[dict]:
    """Decrypt ciphertext using candidate keys and score results.
    Each result dict: {'key': key_matrix, 'source': source, 'score': score, 'text': decrypted}.
    """
    key_infos = derive_candidate_keys()
    results: list[dict] = []
    seen_texts: set[str] = set()
    for info in key_infos:
        k = info['key']
        dec = hill_decrypt(ciphertext, k)
        attempt_entry = {
            'source': info['source'],
            'size': info.get('size', len(k)),
            'key': k,
            'ok': bool(dec),
        }
        if dec:
            if prune_3x3 and info.get('size') == 3:
                partial = dec[:partial_len]
                pscore = combined_plaintext_score(partial)
                attempt_entry['partial_score'] = pscore
                if pscore < partial_min:
                    attempt_entry['pruned'] = True
                    _hill_attempts.append(attempt_entry)
                    continue
            if dec not in seen_texts:
                seen_texts.add(dec)
                score = combined_plaintext_score(dec)
                attempt_entry['score'] = score
                results.append({
                    'key': k,
                    'source': info['source'],
                    'size': info.get('size', len(k)),
                    'score': score,
                    'text': dec,
                    'trace': [
                        {
                            'stage': 'hill',
                            'transformation': f"key:{info['source']}",
                            'size': info.get('size', len(k)),
                        },
                    ],
                })
        _hill_attempts.append(attempt_entry)
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['KNOWN_CRIBS', 'derive_candidate_keys', 'decrypt_and_score', 'get_hill_attempt_log']
