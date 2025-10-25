"""Beaufort cipher implementation.

Beaufort cipher is a reciprocal Vigenère variant where:
- Encryption: C[i] = (K[i] - P[i]) mod 26
- Decryption: P[i] = (K[i] - C[i]) mod 26

Note: Since subtraction is reversible, encryption = decryption in Beaufort.
"""

from __future__ import annotations

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def beaufort_decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    """Decrypt Beaufort cipher using Kryptos keyed alphabet.

    Args:
        ciphertext: Encrypted text
        key: Decryption key (repeats cyclically)
        preserve_non_alpha: If True, keep non-alphabetic characters

    Returns:
        Decrypted plaintext

    Raises:
        ValueError: If key is empty or contains invalid characters
    """
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

            # Beaufort: P = (K - C) mod 26
            p_index = (k_index - c_index) % klen
            out.append(KEYED_ALPHABET[p_index])
            ki += 1
        elif preserve_non_alpha:
            out.append(ch)

    return ''.join(out)


def beaufort_encrypt(plaintext: str, key: str, preserve_non_alpha: bool = False) -> str:
    """Encrypt with Beaufort cipher using Kryptos keyed alphabet.

    Args:
        plaintext: Text to encrypt
        key: Encryption key (repeats cyclically)
        preserve_non_alpha: If True, keep non-alphabetic characters

    Returns:
        Encrypted ciphertext

    Raises:
        ValueError: If key is empty or contains invalid characters

    Note:
        Since Beaufort is reciprocal (C = K - P, P = K - C),
        encryption and decryption use the same formula.
    """
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

            # Beaufort: C = (K - P) mod 26
            c_index = (k_index - p_index) % klen
            out.append(KEYED_ALPHABET[c_index])
            ki += 1
        elif preserve_non_alpha:
            out.append(ch)

    return ''.join(out)


def recover_beaufort_key(ciphertext: str, key_length: int, top_n: int = 3) -> list[str]:
    """Recover Beaufort key using frequency analysis.

    Args:
        ciphertext: Ciphertext to analyze
        key_length: Known or suspected key length
        top_n: Return top N candidate keys

    Returns:
        List of candidate keys (most likely first)

    Note:
        Beaufort uses P = (K - C) mod 26, so frequency analysis is similar
        to Vigenère but with reversed subtraction.
    """
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())

    if len(ct) < key_length:
        return []

    # Split into columns by key position
    columns = [[] for _ in range(key_length)]
    for i, char in enumerate(ct):
        columns[i % key_length].append(char)

    # Recover each key character by frequency analysis
    # Most common English letter is 'E' (index in KEYED_ALPHABET)
    try:
        e_index = KEYED_ALPHABET.index('E')
    except ValueError:
        e_index = 4  # Fallback

    key_chars = []
    for column in columns:
        if not column:
            key_chars.append(['K'])  # Default
            continue

        # Count frequencies
        freq: dict[str, int] = {}
        for char in column:
            freq[char] = freq.get(char, 0) + 1

        # Most common ciphertext character likely corresponds to 'E'
        # For Beaufort: C = K - P, so K = C + P
        # If P = E (most common), then K = C_most_common + E
        most_common = max(freq.keys(), key=lambda x, f=freq: f[x])
        c_index = KEYED_ALPHABET.index(most_common)

        # K = (C + E) mod 26 for Beaufort
        k_index = (c_index + e_index) % len(KEYED_ALPHABET)
        key_char = KEYED_ALPHABET[k_index]

        # For top_n > 1, could try multiple candidates
        # For simplicity, just use the most likely one
        key_chars.append([key_char])

    # Generate candidate keys
    # For now, just return the single most likely key
    candidate_key = ''.join(chars[0] for chars in key_chars)
    return [candidate_key]


__all__ = ['beaufort_decrypt', 'beaufort_encrypt', 'recover_beaufort_key']
