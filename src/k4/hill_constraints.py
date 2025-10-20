"""Constrained Hill cipher key solving using known crib pairs (BERLIN/CLOCK)."""
from __future__ import annotations
from typing import List, Dict
from .hill_cipher import solve_2x2_key, hill_decrypt
from .scoring import combined_plaintext_score

# Example known cribs (plaintext -> cipher segment) from Kryptos K4 clues
KNOWN_CRIBS = {
    'BERLIN': 'NYPVTT',
    'CLOCK': 'MZFPK'
}

def derive_candidate_keys() -> List[List[List[int]]]:
    """Derive candidate 2x2 Hill cipher keys from known crib pairs."""
    keys: List[List[List[int]]] = []
    for plain, cipher in KNOWN_CRIBS.items():
        k = solve_2x2_key(plain, cipher)
        if k:
            keys.append(k)
    return keys

def decrypt_and_score(ciphertext: str) -> List[Dict]:
    """Decrypt ciphertext using candidate keys and score results."""
    keys = derive_candidate_keys()
    results: List[Dict] = []
    for k in keys:
        dec = hill_decrypt(ciphertext, k)
        if dec:
            results.append({'key': k, 'score': combined_plaintext_score(dec), 'text': dec})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results

__all__ = ['KNOWN_CRIBS','derive_candidate_keys','decrypt_and_score']
