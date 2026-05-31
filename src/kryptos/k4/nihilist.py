"""Nihilist cipher implementation.

The Nihilist cipher (19th-century Russian revolutionary cipher) combines a
Polybius square encoding with a running numeric key.  It is a candidate
hypothesis for a substitution layer in K4.

Algorithm:
    1. Build a 5×5 Polybius square keyed by a keyword (I=J merged).
    2. Encode each plaintext letter as a 2-digit number (row*10 + col),
       rows and columns numbered 1–5.
    3. Encode each key letter the same way, repeating the key cyclically.
    4. Ciphertext digit-pair = plaintext digit-pair + key digit-pair
       (as plain integer addition; no modular reduction — values can exceed 99).

Decryption is the arithmetic inverse: subtract the key digit-pairs.

This module exposes encrypt/decrypt for plaintext analysis and a helper that
formats digit-pairs for inspection.
"""

from __future__ import annotations

_ALPHA_IJ = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # I=J merged, 25 chars


# ---------------------------------------------------------------------------
# Polybius square (5×5, I=J)
# ---------------------------------------------------------------------------

def build_square(keyword: str) -> list[list[str]]:
    """Build a 5×5 Polybius square keyed by *keyword* (I and J treated as I)."""
    keyword = keyword.upper().replace("J", "I")
    seen: set[str] = set()
    keyed: list[str] = []
    for ch in keyword:
        if ch in _ALPHA_IJ and ch not in seen:
            keyed.append(ch)
            seen.add(ch)
    for ch in _ALPHA_IJ:
        if ch not in seen:
            keyed.append(ch)
            seen.add(ch)
    assert len(keyed) == 25, f"square must have 25 chars, got {len(keyed)}"
    return [keyed[i * 5 : i * 5 + 5] for i in range(5)]


def _encode_char(square: list[list[str]], ch: str) -> int:
    """Return the Polybius code (2-digit int, e.g. 11 = row 1, col 1) for *ch*."""
    ch = ch.upper().replace("J", "I")
    for r, row in enumerate(square, 1):
        for c, cell in enumerate(row, 1):
            if cell == ch:
                return r * 10 + c
    raise KeyError(f"Character {ch!r} not in square")


def _decode_code(square: list[list[str]], code: int) -> str:
    """Recover the character at Polybius position encoded by *code*."""
    r, c = divmod(code, 10)
    if not (1 <= r <= 5 and 1 <= c <= 5):
        raise ValueError(f"Invalid Nihilist code {code}: row={r} col={c}")
    return square[r - 1][c - 1]


# ---------------------------------------------------------------------------
# Nihilist encrypt / decrypt
# ---------------------------------------------------------------------------

def nihilist_encrypt(plaintext: str, keyword: str, key: str) -> list[int]:
    """Encrypt *plaintext* with the Nihilist cipher.

    Args:
        plaintext:  Input text; non-alpha and J are handled automatically.
        keyword:    Polybius square keyword.
        key:        Running key (repeated cyclically).

    Returns:
        List of integer ciphertext values.
    """
    square = build_square(keyword)
    plain_chars = [c for c in plaintext.upper().replace("J", "I") if c in _ALPHA_IJ]
    key_chars   = [c for c in key.upper().replace("J", "I") if c in _ALPHA_IJ]
    if not key_chars:
        raise ValueError("key must contain at least one alpha character")

    ct: list[int] = []
    for i, ch in enumerate(plain_chars):
        p_code = _encode_char(square, ch)
        k_code = _encode_char(square, key_chars[i % len(key_chars)])
        ct.append(p_code + k_code)
    return ct


def nihilist_decrypt(ciphertext: list[int], keyword: str, key: str) -> str:
    """Decrypt a Nihilist ciphertext.

    Args:
        ciphertext: List of integer cipher values (as produced by nihilist_encrypt).
        keyword:    Polybius square keyword.
        key:        Running key (same as used for encryption).

    Returns:
        Recovered plaintext string.
    """
    square = build_square(keyword)
    key_chars = [c for c in key.upper().replace("J", "I") if c in _ALPHA_IJ]
    if not key_chars:
        raise ValueError("key must contain at least one alpha character")

    out: list[str] = []
    for i, ct_val in enumerate(ciphertext):
        k_code = _encode_char(square, key_chars[i % len(key_chars)])
        p_code = ct_val - k_code
        out.append(_decode_code(square, p_code))
    return "".join(out)


def format_ciphertext(values: list[int]) -> str:
    """Format ciphertext as space-separated numbers (readable form)."""
    return " ".join(str(v) for v in values)


def parse_ciphertext(text: str) -> list[int]:
    """Parse space-separated number string back to a list of ints."""
    return [int(t) for t in text.split() if t.strip()]


__all__ = [
    "build_square",
    "nihilist_encrypt",
    "nihilist_decrypt",
    "format_ciphertext",
    "parse_ciphertext",
]
