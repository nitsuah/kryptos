"""Constrained Hill cipher key solving using known crib pairs (BERLIN/CLOCK)."""
from __future__ import annotations
from typing import List, Dict, Tuple, Set
from itertools import combinations, permutations
from .hill_cipher import solve_2x2_key, hill_decrypt, matrix_inv_mod, ALPHABET
from .scoring import combined_plaintext_score

# Example known cribs (plaintext -> cipher segment) from Kryptos K4 clues
KNOWN_CRIBS = {
    'BERLIN': 'NYPVTT',
    'CLOCK': 'MZFPK'
}

_cache_holder: Dict[str, List[Dict]] = {}

# New helper for 3x3 attempt (heuristic, uses first 9 letters concatenated)

def _solve_3x3_key(plain: str, cipher: str) -> List[List[int]] | None:
    p = ''.join(ch for ch in plain.upper() if ch.isalpha())[:9]
    c = ''.join(ch for ch in cipher.upper() if ch.isalpha())[:9]
    if len(p) < 9 or len(c) < 9:
        return None
    # Arrange into 3x3 matrices column-wise (simple heuristic)
    P = [[ALPHABET.index(p[r*3 + col]) for col in range(3)] for r in range(3)]
    C = [[ALPHABET.index(c[r*3 + col]) for col in range(3)] for r in range(3)]
    Pinv = matrix_inv_mod(P)
    if Pinv is None:
        return None
    K: List[List[int]] = []
    for r in range(3):
        row: List[int] = []
        for col in range(3):
            val = 0
            for k in range(3):
                val += C[r][k] * Pinv[k][col]
            row.append(val % 26)
        K.append(row)
    # Check invertibility
    if matrix_inv_mod(K) is None:
        return None
    return K

# New 3x3 candidate generator (orders + sliding windows)

def _generate_3x3_candidates(cribs: Dict[str, str]) -> List[Dict]:
    items = list(cribs.items())
    results: List[Dict] = []
    seen: Set[Tuple[int,...]] = set()
    for order in permutations(items, len(items)):
        plain_concat = ''.join(p for p,_ in order)
        cipher_concat = ''.join(c for _,c in order)
        # Sliding windows of length 9 if longer
        max_len = min(len(plain_concat), len(cipher_concat))
        for start in range(0, max(1, max_len - 9 + 1)):
            p_slice = plain_concat[start:start+9]
            c_slice = cipher_concat[start:start+9]
            k = _solve_3x3_key(p_slice, c_slice)
            if k:
                # Deduplicate by flattened key tuple
                flat = tuple(v for row in k for v in row)
                if flat in seen:
                    continue
                seen.add(flat)
                order_tag = '+'.join(p for p,_ in order)
                results.append({'key': k, 'source': f'trial3x3:{order_tag}:win{start}', 'size': 3})
    return results

def derive_candidate_keys() -> List[Dict]:
    """Derive candidate 2x2 and expanded 3x3 Hill cipher keys from crib segments.
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
    for (p1,c1),(p2,c2) in combinations(crib_items, 2):
        plain_block = (p1[:2] + p2[:2])
        cipher_block = (c1[:2] + c2[:2])
        k2 = solve_2x2_key(plain_block, cipher_block)
        if k2:
            keys.append({'key': k2, 'source': f'pair:{p1}+{p2}', 'size': 2})
    # Expanded 3x3 heuristic candidates
    keys.extend(_generate_3x3_candidates(KNOWN_CRIBS))
    _cache_holder['keys'] = keys
    return keys

def decrypt_and_score(ciphertext: str) -> List[Dict]:
    """Decrypt ciphertext using candidate keys and score results.
    Each result dict: {'key': key_matrix, 'source': source, 'score': score, 'text': decrypted}.
    """
    key_infos = derive_candidate_keys()
    results: List[Dict] = []
    for info in key_infos:
        k = info['key']
        dec = hill_decrypt(ciphertext, k)
        if dec:
            results.append({
                'key': k, 'source': info['source'], 'size': info.get('size', len(k)),
                'score': combined_plaintext_score(dec), 'text': dec
            })
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['KNOWN_CRIBS','derive_candidate_keys','decrypt_and_score']
