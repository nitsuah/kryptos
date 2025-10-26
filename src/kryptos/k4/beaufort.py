"""Beaufort cipher implementation.

Beaufort cipher is a reciprocal Vigenère variant where:
- Encryption: C[i] = (K[i] - P[i]) mod 26
- Decryption: P[i] = (K[i] - C[i]) mod 26

Note: Since subtraction is reversible, encryption = decryption in Beaufort.
"""

from __future__ import annotations

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def beaufort_decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    key = ''.join(c for c in key.upper() if c.isalpha())
    if not key:
        raise ValueError("Key must contain at least one alphabetic character")

    out: list[str] = []
    klen = len(KEYED_ALPHABET)
    ki = 0

    for ch in ciphertext:
        if ch.isalpha():
            try:
                c_index = KEYED_ALPHABET.index(ch.upper())
                k_char = key[ki % len(key)]
                k_index = KEYED_ALPHABET.index(k_char)
            except ValueError as e:
                raise ValueError(f"Character '{ch}' or key char not in keyed alphabet") from e

            p_index = (k_index - c_index) % klen
            out.append(KEYED_ALPHABET[p_index])
            ki += 1
        elif preserve_non_alpha:
            out.append(ch)

    return ''.join(out)


def beaufort_encrypt(plaintext: str, key: str, preserve_non_alpha: bool = False) -> str:
    key = ''.join(c for c in key.upper() if c.isalpha())
    if not key:
        raise ValueError("Key must contain at least one alphabetic character")

    out: list[str] = []
    klen = len(KEYED_ALPHABET)
    ki = 0

    for ch in plaintext:
        if ch.isalpha():
            try:
                p_index = KEYED_ALPHABET.index(ch.upper())
                k_char = key[ki % len(key)]
                k_index = KEYED_ALPHABET.index(k_char)
            except ValueError as e:
                raise ValueError(f"Character '{ch}' or key char not in keyed alphabet") from e

            c_index = (k_index - p_index) % klen
            out.append(KEYED_ALPHABET[c_index])
            ki += 1
        elif preserve_non_alpha:
            out.append(ch)

    return ''.join(out)


def recover_beaufort_key(ciphertext: str, key_length: int, top_n: int = 3) -> list[str]:
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())

    if len(ct) < key_length:
        return []

    columns = [[] for _ in range(key_length)]
    for i, char in enumerate(ct):
        columns[i % key_length].append(char)

    try:
        e_index = KEYED_ALPHABET.index('E')
    except ValueError:
        e_index = 4

    key_chars = []
    for column in columns:
        if not column:
            key_chars.append(['K'])
            continue

        freq: dict[str, int] = {}
        for char in column:
            freq[char] = freq.get(char, 0) + 1

        most_common = max(freq.keys(), key=lambda x, f=freq: f[x])
        c_index = KEYED_ALPHABET.index(most_common)

        k_index = (c_index + e_index) % len(KEYED_ALPHABET)
        key_char = KEYED_ALPHABET[k_index]

        key_chars.append([key_char])

    candidate_key = ''.join(chars[0] for chars in key_chars)
    return [candidate_key]


__all__ = ['beaufort_decrypt', 'beaufort_encrypt', 'recover_beaufort_key']
