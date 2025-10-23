"""Kryptos K1 section helpers.

Provides a stable ``decrypt`` convenience that uses the Kryptos keyed Vigenère
alphabet implementation from ``kryptos.ciphers``. Additional analysis helpers
should live in higher-level modules (reporting, scoring) rather than here.
"""

from __future__ import annotations

from kryptos.ciphers import vigenere_decrypt

__all__ = ["decrypt"]


def decrypt(ciphertext: str, key: str, preserve_non_alpha: bool = False) -> str:
    """Decrypt Kryptos K1 (Vigenère with keyed alphabet).

    Parameters
    ----------
    ciphertext: The raw K1 ciphertext (whitespace preserved; non-alpha ignored by algorithm).
    key: The Vigenère keyword (case-insensitive; non-alpha stripped).
    preserve_non_alpha: If True, non-alpha characters from ciphertext are passed through.
    """

    # Trim whitespace newlines typical in block renderings but leave internal spacing if requested.
    text = ciphertext.replace("\n", "").strip()
    return vigenere_decrypt(text, key, preserve_non_alpha=preserve_non_alpha)
