"""Hill cipher utilities (2x2 / 3x3) for K4 hypothesis exploration."""
from __future__ import annotations
from typing import List, Sequence

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = 26

def _char_to_int(c: str) -> int:
    return ALPHABET.index(c)

def _int_to_char(i: int) -> str:
    return ALPHABET[i % MOD]

def _chunks(seq: Sequence[int], size: int):
    for i in range(0, len(seq), size):
        chunk = seq[i:i+size]
        if len(chunk) == size:
            yield chunk

def mod_inv(a: int, m: int = MOD) -> int | None:
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def matrix_det(mat: List[List[int]]) -> int:
    n = len(mat)
    if n == 2:
        return mat[0][0]*mat[1][1] - mat[0][1]*mat[1][0]
    if n == 3:
        a,b,c = mat[0]
        d,e,f = mat[1]
        g,h,i = mat[2]
        return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
    raise ValueError("Only 2x2 or 3x3 supported")

def matrix_inv_mod(mat: List[List[int]], m: int = MOD) -> List[List[int]] | None:
    n = len(mat)
    det = matrix_det(mat) % m
    inv_det = mod_inv(det, m)
    if inv_det is None:
        return None
    if n == 2:
        a,b = mat[0]
        c,d = mat[1]
        adj = [[d, -b], [-c, a]]
    elif n == 3:
        a,b,c = mat[0]; d,e,f = mat[1]; g,h,i = mat[2]
        adj = [
            [ (e*i - f*h), -(b*i - c*h), (b*f - c*e) ],
            [ -(d*i - f*g), (a*i - c*g), -(a*f - c*d) ],
            [ (d*h - e*g), -(a*h - b*g), (a*e - b*d) ]
        ]
    else:
        raise ValueError("Only 2x2 or 3x3 supported")
    # Multiply adjugate by inverse determinant mod m
    inv = [[(inv_det * val) % m for val in row] for row in adj]
    return inv

def hill_encrypt_block(block: Sequence[int], key: List[List[int]]) -> List[int]:
    size = len(key)
    return [ sum(key[row][col] * block[col] for col in range(size)) % MOD for row in range(size) ]

def hill_decrypt_block(block: Sequence[int], key: List[List[int]]) -> List[int] | None:
    inv = matrix_inv_mod(key)
    if inv is None:
        return None
    size = len(inv)
    return [ sum(inv[row][col] * block[col] for col in range(size)) % MOD for row in range(size) ]

def hill_encrypt(text: str, key: List[List[int]]) -> str:
    t = ''.join(c for c in text.upper() if c.isalpha())
    nums = [_char_to_int(c) for c in t]
    size = len(key)
    out: List[int] = []
    for chunk in _chunks(nums, size):
        out.extend(hill_encrypt_block(chunk, key))
    return ''.join(_int_to_char(n) for n in out)

def hill_decrypt(text: str, key: List[List[int]]) -> str | None:
    t = ''.join(c for c in text.upper() if c.isalpha())
    nums = [_char_to_int(c) for c in t]
    size = len(key)
    out: List[int] = []
    for chunk in _chunks(nums, size):
        dec = hill_decrypt_block(chunk, key)
        if dec is None:
            return None
        out.extend(dec)
    return ''.join(_int_to_char(n) for n in out)

__all__ = [
    'mod_inv','matrix_det','matrix_inv_mod','hill_encrypt_block','hill_decrypt_block','hill_encrypt','hill_decrypt'
]
