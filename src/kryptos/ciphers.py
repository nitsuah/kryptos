"""Cipher implementations (Vigenère, Kryptos K3 double rotational transposition, etc.).

Canonical implementation for cipher helpers. No side-effect logging configuration
is performed here; callers configure logging externally.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def vigenere_decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    """Decrypt a Vigenère cipher using the Kryptos keyed alphabet.

    Strips non-alpha from key; optionally preserves non-alpha chars from ciphertext.
    """
    key = ''.join(c for c in key.upper() if c.isalpha())
    if not key:
        raise ValueError("Key must contain at least one alphabetic character")
    out: list[str] = []
    klen = len(KEYED_ALPHABET)
    ki = 0
    for idx, ch in enumerate(ciphertext):
        if ch.isalpha():
            try:
                c_index = KEYED_ALPHABET.index(ch)
                k_char = key[ki % len(key)]
                k_index = KEYED_ALPHABET.index(k_char)
            except ValueError as e:  # invalid character not in keyed alphabet
                raise ValueError(f"Character '{ch}' or key char not in keyed alphabet") from e
            p_index = (c_index - k_index) % klen
            dec = KEYED_ALPHABET[p_index]
            out.append(dec)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "[%d] C=%s K=%s -> P=%s Cidx=%d Kidx=%d Pidx=%d",
                    idx,
                    ch,
                    k_char,
                    dec,
                    c_index,
                    k_index,
                    p_index,
                )
            ki += 1
        elif preserve_non_alpha:
            out.append(ch)
    return ''.join(out)


def kryptos_k3_decrypt(ciphertext: str) -> str:
    """Decrypt Kryptos K3 via documented double rotational transposition (no Vigenère)."""
    clean = ''.join(ciphertext.split())
    if clean.startswith('?'):
        clean = clean[1:]
    return double_rotational_transposition(clean)


def double_rotational_transposition(text: str) -> str:
    """Apply K3 double rotational transposition: 24x14 grid -> rotate -> reshape 8 cols -> rotate."""
    cols1, rows1 = 24, 14
    expected_len = cols1 * rows1
    if len(text) != expected_len:
        raise ValueError(f"K3 ciphertext must be {expected_len} chars (got {len(text)})")
    m1 = [list(text[i * cols1 : (i + 1) * cols1]) for i in range(rows1)]
    m2 = _rotate_right(m1)
    t1 = ''.join(''.join(r) for r in m2)
    cols2 = 8
    rows2 = len(t1) // cols2
    m3 = [list(t1[i * cols2 : (i + 1) * cols2]) for i in range(rows2)]
    m4 = _rotate_right(m3)
    return ''.join(''.join(r) for r in m4)


def _rotate_right(matrix: list[list[str]]) -> list[list[str]]:
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    return [[matrix[r][c] for r in range(rows - 1, -1, -1)] for c in range(cols)]


__all__ = [
    "vigenere_decrypt",
    "kryptos_k3_decrypt",
    "double_rotational_transposition",
]
