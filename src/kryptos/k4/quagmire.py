"""Quagmire cipher family (ACA Quagmire I-IV) — keyed-alphabet periodic substitution.

The Quagmire ciphers are Vigenere-style periodic substitutions where the
plaintext and/or ciphertext alphabets are keyword-mixed:

- **Quagmire I**   — keyed plaintext alphabet, straight ciphertext alphabet
- **Quagmire II**  — straight plaintext alphabet, keyed ciphertext alphabet
- **Quagmire III** — the *same* keyed alphabet on both sides
- **Quagmire IV**  — *different* keyed alphabets on each side

All four share one core relation. With plaintext alphabet ``PT``, ciphertext
alphabet ``CT``, indicator key letter ``k`` for the current period, and an
indicator base letter ``b`` (the plaintext-alphabet letter the key letter is
written under):

    C = CT[(PT.index(P) + CT.index(k) - PT.index(b)) % 26]
    P = PT[(CT.index(C) - CT.index(k) + PT.index(b)) % 26]

The ACA convention writes the indicator key under plaintext ``A``. Kryptos
K1/K2 are exactly Quagmire III with the KRYPTOS-keyed alphabet and the
indicator base at the alphabet's *first* letter (``K``), which reduces the
offset to ``PT.index(P) + PT.index(k)`` — the form implemented in
``kryptos.ciphers.vigenere_decrypt``. ``indicator_base=None`` selects that
first-letter convention; pass ``"A"`` for strict ACA behaviour.
"""

from __future__ import annotations

STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyword_alphabet(keyword: str, base: str = STANDARD_ALPHABET) -> str:
    """Build a keyword-mixed alphabet: unique keyword letters, then the rest.

    ``keyword_alphabet("KRYPTOS")`` -> ``"KRYPTOSABCDEFGHIJLMNQUVWXZ"``.
    """
    seen: list[str] = []
    for ch in keyword.upper() + base:
        if ch in base and ch not in seen:
            seen.append(ch)
    return "".join(seen)


def _clean(text: str, alphabet: str) -> str:
    return "".join(c for c in text.upper() if c in alphabet)


def _crypt(
    text: str,
    indicator_key: str,
    pt_alphabet: str,
    ct_alphabet: str,
    indicator_base: str | None,
    decrypt: bool,
) -> str:
    if len(pt_alphabet) != len(ct_alphabet):
        raise ValueError("Plaintext and ciphertext alphabets must be the same length")
    n = len(pt_alphabet)
    base = pt_alphabet[0] if indicator_base is None else indicator_base.upper()
    base_idx = pt_alphabet.index(base)

    key = _clean(indicator_key, ct_alphabet)
    if not key:
        raise ValueError("Indicator key must contain at least one alphabet character")
    key_offsets = [ct_alphabet.index(k) - base_idx for k in key]

    src, dst = (ct_alphabet, pt_alphabet) if decrypt else (pt_alphabet, ct_alphabet)
    sign = -1 if decrypt else 1
    chars = _clean(text, src)
    return "".join(dst[(src.index(c) + sign * key_offsets[i % len(key_offsets)]) % n] for i, c in enumerate(chars))


def quagmire1_encrypt(plaintext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    """Quagmire I: keyed plaintext alphabet, straight ciphertext alphabet."""
    return _crypt(plaintext, key, keyword_alphabet(alphabet_keyword), STANDARD_ALPHABET, indicator_base, False)


def quagmire1_decrypt(ciphertext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    return _crypt(ciphertext, key, keyword_alphabet(alphabet_keyword), STANDARD_ALPHABET, indicator_base, True)


def quagmire2_encrypt(plaintext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    """Quagmire II: straight plaintext alphabet, keyed ciphertext alphabet."""
    return _crypt(plaintext, key, STANDARD_ALPHABET, keyword_alphabet(alphabet_keyword), indicator_base, False)


def quagmire2_decrypt(ciphertext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    return _crypt(ciphertext, key, STANDARD_ALPHABET, keyword_alphabet(alphabet_keyword), indicator_base, True)


def quagmire3_encrypt(plaintext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    """Quagmire III: the same keyed alphabet on both sides (Kryptos K1/K2 form)."""
    keyed = keyword_alphabet(alphabet_keyword)
    return _crypt(plaintext, key, keyed, keyed, indicator_base, False)


def quagmire3_decrypt(ciphertext: str, key: str, alphabet_keyword: str, indicator_base: str | None = None) -> str:
    keyed = keyword_alphabet(alphabet_keyword)
    return _crypt(ciphertext, key, keyed, keyed, indicator_base, True)


def quagmire4_encrypt(
    plaintext: str,
    key: str,
    pt_keyword: str,
    ct_keyword: str,
    indicator_base: str | None = None,
) -> str:
    """Quagmire IV: different keyed alphabets for plaintext and ciphertext."""
    return _crypt(plaintext, key, keyword_alphabet(pt_keyword), keyword_alphabet(ct_keyword), indicator_base, False)


def quagmire4_decrypt(
    ciphertext: str,
    key: str,
    pt_keyword: str,
    ct_keyword: str,
    indicator_base: str | None = None,
) -> str:
    return _crypt(ciphertext, key, keyword_alphabet(pt_keyword), keyword_alphabet(ct_keyword), indicator_base, True)


__all__ = [
    "STANDARD_ALPHABET",
    "keyword_alphabet",
    "quagmire1_encrypt",
    "quagmire1_decrypt",
    "quagmire2_encrypt",
    "quagmire2_decrypt",
    "quagmire3_encrypt",
    "quagmire3_decrypt",
    "quagmire4_encrypt",
    "quagmire4_decrypt",
]
