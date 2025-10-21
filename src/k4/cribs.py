"""Crib mapping utilities for K4 analysis."""
from __future__ import annotations

def normalize_cipher(text: str) -> str:
    """Return uppercase letters-only form of ciphertext/plaintext input."""
    return ''.join(c for c in text.upper() if c.isalpha())

def annotate_cribs(
    ciphertext: str,
    crib_plain_to_cipher: dict[str, str],
    one_based: bool = True,
) -> list[dict[str, object]]:
    """Annotate crib placements.

    Args:
        ciphertext: Raw or normalized ciphertext.
        crib_plain_to_cipher: Mapping of known plaintext crib -> expected cipher segment released
            by Sanborn.
        one_based: Whether positions should be reported one-based (default True per sculpture
            convention).

    Returns:
        List of annotation dicts with fields:
          plaintext, expected_cipher, expected_positions (tuple or None), found_positions (list[int]),
          alignment_ok (bool)
    """
    ct = normalize_cipher(ciphertext)
    results: list[dict[str, object]] = []
    for plain, expected_cipher in crib_plain_to_cipher.items():
        exp_norm = normalize_cipher(expected_cipher)
        # Expected positions: locate given expected cipher substring once if present
        idx = ct.find(exp_norm)
        expected_positions: tuple[int, int] | None = None
        if idx != -1:
            start = idx + (1 if one_based else 0)
            end = start + len(exp_norm) - (1 if one_based else 0)
            expected_positions = (start, end)
        # All occurrences of plaintext crib itself (if already decrypted somewhere hypothetical)
        plain_norm = normalize_cipher(plain)
        found_positions: list[int] = []
        search_start = 0
        while True:
            fi = ct.find(plain_norm, search_start)
            if fi == -1:
                break
            found_positions.append(fi + (1 if one_based else 0))
            search_start = fi + 1
        alignment_ok = expected_positions is not None
        results.append({
            'plaintext': plain_norm,
            'expected_cipher': exp_norm,
            'expected_positions': expected_positions,
            'found_positions': found_positions,
            'alignment_ok': alignment_ok,
        })
    return results

__all__ = ['normalize_cipher', 'annotate_cribs']
