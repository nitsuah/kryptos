"""Constrained Hill cipher key solving using known crib pairs (BERLIN/CLOCK)."""
from __future__ import annotations
from typing import List, Dict, Tuple, Set
from itertools import combinations, permutations
from .hill_cipher import solve_2x2_key, hill_decrypt, matrix_inv_mod, ALPHABET
from .scoring import combined_plaintext_score_cached as combined_plaintext_score  # cached

# Example known cribs (plaintext -> cipher segment) from Kryptos K4 clues
KNOWN_CRIBS = {
    'BERLIN': 'NYPVTT',
    'CLOCK': 'MZFPK'
}

_cache_holder: Dict[str, List[Dict]] = {}

# --- 3x3 helpers (refined) -------------------------------------------------

def _assemble_3x3_variants(seq: str) -> List[List[List[int]]]:
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
    variants: List[List[List[int]]] = []
    seen: Set[Tuple[int, ...]] = set()

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
            col_mat[r][c] = ALPHABET.index(letters[idx]); idx += 1
    flat = tuple(v for rr in col_mat for v in rr)
    if flat not in seen:
        variants.append(col_mat); seen.add(flat)

    # diagonal emphasis (place first 3 on main diag, next 3 on anti-diag, rest row-major)
    diag_mat = [[0]*3 for _ in range(3)]
    pos_letters = list(letters)
    if len(pos_letters) >= 9:
        # first 3 -> main diag (0,0),(1,1),(2,2)
        diag_positions = [(0,0),(1,1),(2,2)]
        for i,(r,c) in enumerate(diag_positions):
            diag_mat[r][c] = ALPHABET.index(pos_letters[i])
        # next 3 -> anti diag (0,2),(1,1),(2,0)
        anti_positions = [(0,2),(1,1),(2,0)]
        for j,(r,c) in enumerate(anti_positions, start=3):
            diag_mat[r][c] = ALPHABET.index(pos_letters[j])
        # fill remaining cells row-major with remaining letters
        fill_idx = 6
        for r in range(3):
            for c in range(3):
                if diag_mat[r][c] == 0 and (r,c) not in [(1,1)]:  # center already set
                    diag_mat[r][c] = ALPHABET.index(pos_letters[fill_idx]); fill_idx += 1
        flat = tuple(v for rr in diag_mat for v in rr)
        if flat not in seen:
            variants.append(diag_mat); seen.add(flat)

    return variants

def _solve_3x3_keys(plain: str, cipher: str) -> List[List[List[int]]]:
    """Attempt to derive 3x3 keys from concatenated 9-letter plain/cipher slices using multiple assemblies.
    Returns list of invertible key matrices (may be empty)."""
    p = ''.join(ch for ch in plain.upper() if ch.isalpha())
    c = ''.join(ch for ch in cipher.upper() if ch.isalpha())
    if len(p) < 9 or len(c) < 9:
        return []
    p = p[:9]; c = c[:9]
    P_variants = _assemble_3x3_variants(p)
    C_variants = _assemble_3x3_variants(c)
    keys: List[List[List[int]]] = []
    for Pv in P_variants:
        Pinv = matrix_inv_mod(Pv)
        if Pinv is None:
            continue
        for Cv in C_variants:
            K: List[List[int]] = []
            for r in range(3):
                row: List[int] = []
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

def _generate_3x3_candidates(cribs: Dict[str, str]) -> List[Dict]:
    items = list(cribs.items())
    results: List[Dict] = []
    seen: Set[Tuple[int, ...]] = set()
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

def derive_candidate_keys() -> List[Dict]:
    """Derive candidate 2x2 and refined 3x3 Hill cipher keys from crib segments.
    Generates single/pair 2x2 keys and multiple window/order 3x3 heuristic keys.
    Caches results.
    """
    if 'keys' in _cache_holder:
        return _cache_holder['keys']
    keys: List[Dict] = []
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

def decrypt_and_score(ciphertext: str) -> List[Dict]:
    """Decrypt ciphertext using candidate keys and score results.
    Each result dict: {'key': key_matrix, 'source': source, 'score': score, 'text': decrypted}.
    """
    key_infos = derive_candidate_keys()
    results: List[Dict] = []
    seen_texts: Set[str] = set()
    for info in key_infos:
        k = info['key']
        dec = hill_decrypt(ciphertext, k)
        if dec and dec not in seen_texts:
            seen_texts.add(dec)
            results.append({
                'key': k, 'source': info['source'], 'size': info.get('size', len(k)),
                'score': combined_plaintext_score(dec), 'text': dec,
                'trace': [{'stage': 'hill', 'transformation': f"key:{info['source']}", 'size': info.get('size', len(k))}]
            })
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['KNOWN_CRIBS', 'derive_candidate_keys', 'decrypt_and_score']
