"""Cipher implementations (Vigenère, Kryptos K3 double rotational transposition, etc.).

Canonical implementation for cipher helpers. No side-effect logging configuration
is performed here; callers configure logging externally.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

logger = logging.getLogger(__name__)

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def vigenere_decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
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
            except ValueError as e:
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


def k3_decrypt(ciphertext: str) -> str:
    clean = ''.join(ciphertext.split())
    if clean.startswith('?'):
        clean = clean[1:]
    return double_rotational_transposition(clean)


def double_rotational_transposition(text: str) -> str:
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
    if rows == 0:
        return []
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows - 1, -1, -1)] for c in range(cols)]


def rotate_matrix_right_90(matrix: Sequence[Sequence[str]]) -> list[list[str]]:
    rows = len(matrix)
    if rows == 0:
        return []
    cols = len(matrix[0])
    out: list[list[str]] = [["" for _ in range(rows)] for _ in range(cols)]
    for r in range(rows):
        for c in range(cols):
            out[c][rows - 1 - r] = matrix[r][c]
    return out


def transposition_decrypt(ciphertext: str, key: str | None = None) -> str:
    clean = ''.join(ciphertext.split())
    if clean.startswith('?'):
        clean = clean[1:]
    if key is None:
        return k3_decrypt(clean)
    width = 86
    height = 4
    needed = width * height
    if len(clean) < needed:
        clean = clean.ljust(needed, 'X')
    if len(clean) != needed:
        raise ValueError(f"Expected ciphertext length {needed}, got {len(clean)}")
    key_up = ''.join(c for c in key.upper() if c.isalpha())
    repeated_key = (key_up * ((width // len(key_up)) + 1))[:width]
    key_tuples = sorted((ch, idx) for idx, ch in enumerate(repeated_key))
    col_order = [idx for _ch, idx in key_tuples]
    cols: list[str] = []
    start = 0
    for _ in range(width):
        cols.append(clean[start : start + height])
        start += height
    grid = [["" for _ in range(width)] for _ in range(height)]
    for order, orig_col in enumerate(col_order):
        col_text = cols[order]
        for r in range(height):
            grid[r][orig_col] = col_text[r]
    return ''.join(''.join(row) for row in grid)


def polybius_decrypt(ciphertext: str, key_square: Sequence[Sequence[str]]) -> str:
    if len(key_square) != 5 or any(len(row) != 5 for row in key_square):
        raise ValueError("Key square must be a 5x5 grid.")
    if len(ciphertext) % 2 != 0:
        raise ValueError("Ciphertext length must be even.")
    pairs = [ciphertext[i : i + 2] for i in range(0, len(ciphertext), 2)]
    out: list[str] = []
    for pair in pairs:
        try:
            r = int(pair[0]) - 1
            c = int(pair[1]) - 1
            out.append(key_square[r][c])
        except (ValueError, IndexError) as exc:
            raise ValueError(f"Invalid pair in ciphertext: {pair}") from exc
    return ''.join(out)


def beaufort_decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    from kryptos.k4.beaufort import beaufort_decrypt as _beaufort_decrypt

    return _beaufort_decrypt(ciphertext, key, preserve_non_alpha)


def beaufort_encrypt(plaintext: str, key: str, preserve_non_alpha: bool = False) -> str:
    from kryptos.k4.beaufort import beaufort_encrypt as _beaufort_encrypt

    return _beaufort_encrypt(plaintext, key, preserve_non_alpha)


__all__ = [
    "vigenere_decrypt",
    "k3_decrypt",
    "double_rotational_transposition",
    "rotate_matrix_right_90",
    "transposition_decrypt",
    "polybius_decrypt",
    "beaufort_decrypt",
    "beaufort_encrypt",
]
