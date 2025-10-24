"""Kryptos K2 section helpers.

K2 uses the same keyed Vigenère alphabet as K1 with a different key.
This thin wrapper maintains symmetry with other section packages.
"""

from __future__ import annotations

from kryptos.ciphers import vigenere_decrypt

__all__ = ["decrypt"]


def decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    """Decrypt Kryptos K2 (keyed Vigenère).

    Parameters mirror :func:`kryptos.k1.decrypt` for consistency.
    """

    text = ciphertext.replace("\n", "").strip()
    return vigenere_decrypt(text, key, preserve_non_alpha=preserve_non_alpha)
