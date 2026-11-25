"""Pure hypothesis checking for K4 keyed Vigenère and Beaufort families."""

from __future__ import annotations

from kryptos.ciphers import beaufort_decrypt, vigenere_decrypt

from .keystream_validator import K4_CRIBS
from .physical_grid import K4


def crib_verdict(plaintext: str) -> dict[str, bool]:
    normalized = "".join(char for char in plaintext.upper() if char.isalpha())
    return {
        label: normalized[start : start + len(word)] == word
        for label, (word, start) in K4_CRIBS.items()
    }


def check_hypothesis(family: str, key: str) -> dict[str, object]:
    normalized_family = family.lower()
    if normalized_family not in {"vigenere", "beaufort"}:
        raise ValueError(f"Unknown family: {normalized_family}")

    normalized_key = "".join(char for char in key.upper() if char.isalpha())
    decrypt = vigenere_decrypt if normalized_family == "vigenere" else beaufort_decrypt
    plaintext = decrypt(K4, normalized_key)
    verdict = crib_verdict(plaintext)
    hit_count = sum(verdict.values())

    return {
        "family": normalized_family,
        "key": normalized_key,
        "plaintext": plaintext,
        "crib_verdict": verdict,
        "hit_count": hit_count,
        "all_cribs_match": hit_count == len(K4_CRIBS),
    }
