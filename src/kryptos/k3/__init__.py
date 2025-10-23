"""Kryptos K3 section helpers.

K3 is solved by a published double rotational transposition. We expose a
``decrypt`` convenience which validates ciphertext length and delegates to
``kryptos.ciphers.kryptos_k3_decrypt``.
"""

from __future__ import annotations

from kryptos.ciphers import kryptos_k3_decrypt

__all__ = ["decrypt"]


def decrypt(ciphertext: str) -> str:
    """Decrypt Kryptos K3.

    Whitespace (including newlines) is stripped prior to processing. A leading
    question mark sometimes included in reproductions is ignored.
    """

    text = ''.join(ciphertext.split())
    if text.startswith('?'):
        text = text[1:]
    return kryptos_k3_decrypt(text)
