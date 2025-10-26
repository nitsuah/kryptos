"""Hill cipher search utilities separated from core primitives."""

from __future__ import annotations

from .hill_cipher import hill_decrypt
from .scoring import combined_plaintext_score


def score_decryptions(ciphertext: str, keys: list[list[list[int]]], limit: int = 100) -> list[dict]:
    results: list[dict] = []
    for k in keys[:limit]:
        dec = hill_decrypt(ciphertext, k)
        if dec:
            results.append({'key': k, 'score': combined_plaintext_score(dec), 'text': dec})
    results.sort(key=lambda r: r['score'], reverse=True)
    return results


__all__ = ['score_decryptions']
