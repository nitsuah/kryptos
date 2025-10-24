"""Hill cipher utilities (2x2 / 3x3) for K4 hypothesis exploration."""

from __future__ import annotations

from collections.abc import Sequence
from math import gcd

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = 26


def _char_to_int(c: str) -> int:
    return ALPHABET.index(c)


def _int_to_char(i: int) -> str:
    return ALPHABET[i % MOD]


def _chunks(seq: Sequence[int], size: int):
    for i in range(0, len(seq), size):
        chunk = seq[i : i + size]
        if len(chunk) == size:
            yield chunk


def mod_inv(a: int, m: int = MOD) -> int | None:
    """Modular inverse of a mod m, or None if not invertible."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def matrix_det(mat: list[list[int]]) -> int:
    """
    Determinant of a 2x2 or 3x3 matrix.
    """
    n = len(mat)
    if n == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    if n == 3:
        a, b, c = mat[0]
        d, e, f = mat[1]
        g, h, i = mat[2]
        return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    raise ValueError("Only 2x2 or 3x3 supported")


def matrix_inv_mod(mat: list[list[int]], m: int = MOD) -> list[list[int]] | None:
    """
    Modular inverse of a 2x2 or 3x3 matrix mod m, or None if not invertible.
    """
    n = len(mat)
    det = matrix_det(mat) % m
    inv_det = mod_inv(det, m)
    if inv_det is None:
        return None
    if n == 2:
        a, b = mat[0]
        c, d = mat[1]
        adj = [[d, -b], [-c, a]]
    elif n == 3:
        a, b, c = mat[0]
        d, e, f = mat[1]
        g, h, i = mat[2]
        # Cofactors
        C11 = e * i - f * h
        C12 = -(d * i - f * g)
        C13 = d * h - e * g

        C21 = -(b * i - c * h)
        C22 = a * i - c * g
        C23 = -(a * h - b * g)

        C31 = b * f - c * e
        C32 = -(a * f - c * d)
        C33 = a * e - b * d
        # Construct adjugate matrix by transposing the cofactor matrix
        adj = [
            [C11, C21, C31],
            [C12, C22, C32],
            [C13, C23, C33],
        ]
    else:
        raise ValueError("Only 2x2 or 3x3 supported")
    inv = [[(inv_det * val) % m for val in row] for row in adj]
    return inv


def hill_encrypt_block(block: Sequence[int], key: list[list[int]]) -> list[int]:
    """Encrypt a block using Hill cipher with given key."""
    size = len(key)
    return [sum(key[row][col] * block[col] for col in range(size)) % MOD for row in range(size)]


def hill_decrypt_block(block: Sequence[int], key: list[list[int]]) -> list[int] | None:
    """Decrypt a block using Hill cipher with given key."""
    inv = matrix_inv_mod(key)
    if inv is None:
        return None
    size = len(inv)
    return [sum(inv[row][col] * block[col] for col in range(size)) % MOD for row in range(size)]


def hill_encrypt(text: str, key: list[list[int]]) -> str:
    """Encrypt text using Hill cipher with given key."""
    t = ''.join(c for c in text.upper() if c.isalpha())
    nums = [_char_to_int(c) for c in t]
    size = len(key)
    out: list[int] = []
    for chunk in _chunks(nums, size):
        out.extend(hill_encrypt_block(chunk, key))
    return ''.join(_int_to_char(n) for n in out)


def hill_decrypt(text: str, key: list[list[int]]) -> str | None:
    """Decrypt text using Hill cipher with given key."""
    t = ''.join(c for c in text.upper() if c.isalpha())
    nums = [_char_to_int(c) for c in t]
    size = len(key)
    out: list[int] = []
    for chunk in _chunks(nums, size):
        dec = hill_decrypt_block(chunk, key)
        if dec is None:
            return None
        out.extend(dec)
    return ''.join(_int_to_char(n) for n in out)


def invertible_2x2_keys() -> list[list[list[int]]]:
    """Generate all invertible 2x2 Hill cipher keys mod 26."""
    keys: list[list[list[int]]] = []
    for a in range(26):
        for b in range(26):
            for c in range(26):
                for d in range(26):
                    det = (a * d - b * c) % 26
                    if gcd(det, 26) == 1:
                        keys.append([[a, b], [c, d]])
    return keys


def solve_2x2_key(plain: str, cipher: str) -> list[list[int]] | None:
    """Solve for 2x2 Hill cipher key mapping plain to cipher (first 4 letters each)."""
    p = ''.join(ch for ch in plain.upper() if ch.isalpha())
    ct = ''.join(ch for ch in cipher.upper() if ch.isalpha())
    if len(p) < 4 or len(ct) < 4:
        return None
    P = [[_char_to_int(p[0]), _char_to_int(p[2])], [_char_to_int(p[1]), _char_to_int(p[3])]]
    C = [[_char_to_int(ct[0]), _char_to_int(ct[2])], [_char_to_int(ct[1]), _char_to_int(ct[3])]]
    detP = (P[0][0] * P[1][1] - P[0][1] * P[1][0]) % 26
    inv_detP = mod_inv(detP)
    if inv_detP is None:
        return None
    adjP = [[P[1][1], -P[0][1]], [-P[1][0], P[0][0]]]
    Pinv = [[(inv_detP * v) % 26 for v in row] for row in adjP]
    K = [
        [
            (C[0][0] * Pinv[0][0] + C[0][1] * Pinv[1][0]) % 26,
            (C[0][0] * Pinv[0][1] + C[0][1] * Pinv[1][1]) % 26,
        ],
        [
            (C[1][0] * Pinv[0][0] + C[1][1] * Pinv[1][0]) % 26,
            (C[1][0] * Pinv[0][1] + C[1][1] * Pinv[1][1]) % 26,
        ],
    ]
    if mod_inv((K[0][0] * K[1][1] - K[0][1] * K[1][0]) % 26) is None:
        return None
    return K


def brute_force_crib(cipher_segment: str, plain_segment: str, limit: int = 1000) -> list[dict]:
    """Brute-force search for 2x2 Hill cipher keys mapping plain_segment to cipher_segment."""
    p = ''.join(ch for ch in plain_segment.upper() if ch.isalpha())[:4]
    ct = ''.join(ch for ch in cipher_segment.upper() if ch.isalpha())[:4]
    if len(p) < 4 or len(ct) < 4:
        return []
    results: list[dict] = []
    count = 0
    for key in invertible_2x2_keys():
        if count >= limit:
            break
        enc = hill_encrypt(p, key)[:4]
        if enc == ct:
            results.append({'key': key, 'enc': enc})
        count += 1
    return results


__all__ = [
    'mod_inv',
    'matrix_det',
    'matrix_inv_mod',
    'hill_encrypt_block',
    'hill_decrypt_block',
    'hill_encrypt',
    'hill_decrypt',
    'invertible_2x2_keys',
    'solve_2x2_key',
    'brute_force_crib',
]
