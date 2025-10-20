"""Constrained Hill cipher key solving using known crib pairs (BERLIN/CLOCK)."""
from __future__ import annotations
from typing import List, Dict
from itertools import combinations
from .hill_cipher import solve_2x2_key, hill_decrypt
from .scoring import combined_plaintext_score

# Example known cribs (plaintext -> cipher segment) from Kryptos K4 clues
KNOWN_CRIBS = {
    'BERLIN': 'NYPVTT',
    'CLOCK': 'MZFPK'
}

_cache_holder: Dict[str, List[Dict]] = {}

def derive_candidate_keys() -> List[Dict]:
    """Derive candidate 2x2 Hill cipher keys from individual and pairwise crib segments.
    Returns list of dicts with caching:
    {'key': key_matrix, 'source': 'single:BERLIN' or 'pair:BERLIN+CLOCK'}
    """
    if 'keys' in _cache_holder:
        return _cache_holder['keys']
    keys: List[Dict] = []
    # Single cribs
    for plain, cipher in KNOWN_CRIBS.items():
        k = solve_2x2_key(plain, cipher)
        if k:
            keys.append({'key': k, 'source': f'single:{plain}'})
    # Pairwise combinations
    crib_items = list(KNOWN_CRIBS.items())
    for (p1,c1),(p2,c2) in combinations(crib_items, 2):
        plain_block = (p1[:2] + p2[:2])
        cipher_block = (c1[:2] + c2[:2])
        k2 = solve_2x2_key(plain_block, cipher_block)
        if k2:
            keys.append({'key': k2, 'source': f'pair:{p1}+{p2}'})
    # Store cache
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
                'key': k, 'source': info['source'],
                'score': combined_plaintext_score(dec), 'text': dec
            })
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['KNOWN_CRIBS','derive_candidate_keys','decrypt_and_score']
