"""ADFGVX fractionating cipher implementation.

ADFGVX was used by German forces in WW1 and is a candidate hypothesis for
layers of K4's encryption.  It combines a 6×6 Polybius square fractionation
(encoding each plaintext character as two letters drawn from {A,D,F,G,V,X})
with a columnar transposition keyed by a second keyword.

The 6×6 square holds the 26-letter alphabet (I and J are kept distinct, with
digits 0–9 filling the remaining 10 cells) or, in the 5×5 ADFGX variant,
25 letters with I=J.  This module implements the ADFGVX (6×6) variant by
default but exports helpers to build any desired square.

Typical K4-relevant use: encrypt K4 with candidate (square_key, column_key)
and score the result; or decrypt K4 under these keys and score the output.
"""

from __future__ import annotations

import math
from typing import Sequence

ADFGVX_CHARS: str = "ADFGVX"
_DEFAULT_ALPHA: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# ---------------------------------------------------------------------------
# Square construction
# ---------------------------------------------------------------------------

def build_polybius_square(keyword: str, alphabet: str = _DEFAULT_ALPHA) -> list[list[str]]:
    """Build a 6×6 ADFGVX Polybius square keyed by *keyword*.

    Characters in *keyword* appear first (deduplicated, preserving order),
    followed by remaining characters from *alphabet* in order.

    Args:
        keyword:  Key word/phrase that determines the square layout.
        alphabet: Character set to fill the square (default: A-Z + 0-9 = 36 chars).

    Returns:
        6×6 list-of-lists of single characters.
    """
    keyword = keyword.upper()
    alphabet = alphabet.upper()
    seen: set[str] = set()
    keyed: list[str] = []
    for ch in keyword:
        if ch in alphabet and ch not in seen:
            keyed.append(ch)
            seen.add(ch)
    for ch in alphabet:
        if ch not in seen:
            keyed.append(ch)
            seen.add(ch)
    if len(keyed) != 36:
        raise ValueError(
            f"ADFGVX square requires exactly 36 characters; got {len(keyed)}"
        )
    return [keyed[i * 6 : i * 6 + 6] for i in range(6)]


def square_index(square: Sequence[Sequence[str]], char: str) -> tuple[int, int]:
    """Return (row, col) for *char* in *square*.  Raises KeyError if absent."""
    char = char.upper()
    for r, row in enumerate(square):
        for c, cell in enumerate(row):
            if cell == char:
                return r, c
    raise KeyError(f"Character {char!r} not found in square")


# ---------------------------------------------------------------------------
# ADFGVX encrypt / decrypt
# ---------------------------------------------------------------------------

def adfgvx_encrypt(
    plaintext: str,
    square_key: str,
    column_key: str,
    alphabet: str = _DEFAULT_ALPHA,
) -> str:
    """Encrypt *plaintext* with ADFGVX.

    Pipeline:
        plaintext → Polybius fractionation → columnar transposition → ciphertext

    Args:
        plaintext:   Input text.  Non-alphabet chars are dropped.
        square_key:  Keyword for the Polybius square.
        column_key:  Keyword that determines columnar transposition order.
        alphabet:    Characters for the square (default A-Z + 0-9).

    Returns:
        ADFGVX ciphertext string (letters in {A,D,F,G,V,X}).
    """
    square = build_polybius_square(square_key, alphabet)
    chars = _clean(plaintext, alphabet)

    # Fractionation: each char → two ADFGVX letters
    fractionated: list[str] = []
    for ch in chars:
        r, c = square_index(square, ch)
        fractionated.append(ADFGVX_CHARS[r])
        fractionated.append(ADFGVX_CHARS[c])

    # Columnar transposition
    return _columnar_encrypt("".join(fractionated), column_key)


def adfgvx_decrypt(
    ciphertext: str,
    square_key: str,
    column_key: str,
    alphabet: str = _DEFAULT_ALPHA,
) -> str:
    """Decrypt *ciphertext* with ADFGVX.

    Args:
        ciphertext:  ADFGVX ciphertext (must be even length).
        square_key:  Keyword for the Polybius square.
        column_key:  Keyword for the columnar transposition.
        alphabet:    Characters for the square (default A-Z + 0-9).

    Returns:
        Recovered plaintext (uppercase letters/digits).
    """
    square = build_polybius_square(square_key, alphabet)
    ct = "".join(c for c in ciphertext.upper() if c in ADFGVX_CHARS)
    if len(ct) % 2 != 0:
        raise ValueError("ADFGVX ciphertext length must be even after stripping.")

    # Invert columnar transposition
    fractionated = _columnar_decrypt(ct, column_key)

    # Invert fractionation
    out: list[str] = []
    for i in range(0, len(fractionated), 2):
        r = ADFGVX_CHARS.index(fractionated[i])
        c = ADFGVX_CHARS.index(fractionated[i + 1])
        out.append(square[r][c])
    return "".join(out)


# ---------------------------------------------------------------------------
# Columnar transposition helpers
# ---------------------------------------------------------------------------

def _clean(text: str, alphabet: str) -> str:
    return "".join(c for c in text.upper() if c in alphabet)


def _col_order(key: str) -> list[int]:
    """Return column reading order for a transposition key (alphabetical rank)."""
    key = key.upper()
    indexed = sorted(range(len(key)), key=lambda i: (key[i], i))
    order = [0] * len(key)
    for rank, col in enumerate(indexed):
        order[col] = rank
    return order


def _columnar_encrypt(text: str, key: str) -> str:
    n_cols = len(key)
    n_rows = math.ceil(len(text) / n_cols)
    # No padding — last row may be incomplete (standard ADFGVX practice)
    grid = [list(text[i * n_cols : (i + 1) * n_cols]) for i in range(n_rows)]
    order = _col_order(key)
    # Read columns in alphabetical order of key; shorter columns are from ragged last row
    col_sequence = sorted(range(n_cols), key=lambda c: order[c])
    out: list[str] = []
    for col in col_sequence:
        for row in grid:
            if col < len(row):
                out.append(row[col])
    return "".join(out)


def _columnar_decrypt(ciphertext: str, key: str) -> str:
    n_cols = len(key)
    n = len(ciphertext)
    n_rows = math.ceil(n / n_cols)
    # Columns 0 … (n_cols - n_short - 1) each have n_rows chars;
    # the remaining n_short columns have n_rows - 1 chars.
    n_short = n_cols * n_rows - n
    col_lengths = [n_rows if j < (n_cols - n_short) else n_rows - 1 for j in range(n_cols)]

    order = _col_order(key)
    col_sequence = sorted(range(n_cols), key=lambda c: order[c])  # alphabetical read order

    # Split ciphertext into columns, slicing in the order they were written (col_sequence)
    columns: dict[int, str] = {}
    pos = 0
    for col in col_sequence:
        length = col_lengths[col]
        columns[col] = ciphertext[pos : pos + length]
        pos += length

    # Reconstruct row-major plaintext
    out: list[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            if r < len(columns[c]):
                out.append(columns[c][r])
    return "".join(out)


__all__ = [
    "ADFGVX_CHARS",
    "build_polybius_square",
    "square_index",
    "adfgvx_encrypt",
    "adfgvx_decrypt",
]
