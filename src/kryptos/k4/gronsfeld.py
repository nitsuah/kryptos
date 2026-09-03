"""Gronsfeld cipher for K4 — Frontier P7.

Gronsfeld is a Vigenère variant where the key is a sequence of decimal
digits (0–9), each digit acting as a shift of 0–9.  This makes it
hand-encryptable and drastically reduces the key space compared with
a full Vigenère.

Candidate keys are derived from the K2 coordinate digits:
  38°57'6.5"N  →  3, 8, 5, 7, 6, 5
  77°8'44"W    →  7, 7, 8, 4, 4
"""

from __future__ import annotations

from .physical_grid import K4
from .scoring_instructional import combined_instructional_score

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# K2 coordinate digit keys (decimal only, per the landscape doc)
K2_COORDINATE_KEYS: list[str] = [
    "385765",  # 38°57'6.5"N truncated to 6 digits
    "770844",  # 77°8'44"W
    "385706577",  # full N coordinate string
    "3857",  # hour + minute from one K2 reading
    "3857065770844",  # all K2 digits concatenated
]


def gronsfeld_decrypt(ciphertext: str, digit_key: str, alphabet: str = STANDARD) -> str:
    """Decrypt a Gronsfeld cipher: each digit shift is subtracted mod len(alphabet).

    Args:
        ciphertext: Text to decrypt (alpha chars only are shifted).
        digit_key:  String of decimal digits (non-digit chars ignored).
        alphabet:   26-char substitution alphabet (default: A-Z).

    Returns:
        Decrypted string, same length as ciphertext.
    """
    key = [int(d) for d in digit_key if d.isdigit()]
    if not key:
        return ciphertext
    n_alpha = len(alphabet)
    n_key = len(key)
    out: list[str] = []
    pos = 0
    for c in ciphertext.upper():
        if c.isalpha() and c in alphabet:
            idx = alphabet.index(c)
            out.append(alphabet[(idx - key[pos % n_key]) % n_alpha])
            pos += 1
        else:
            out.append(c)
    return "".join(out)


def gronsfeld_encrypt(plaintext: str, digit_key: str, alphabet: str = STANDARD) -> str:
    """Encrypt a Gronsfeld cipher (reverse of decrypt)."""
    key = [int(d) for d in digit_key if d.isdigit()]
    if not key:
        return plaintext
    n_alpha = len(alphabet)
    n_key = len(key)
    out: list[str] = []
    pos = 0
    for c in plaintext.upper():
        if c.isalpha() and c in alphabet:
            idx = alphabet.index(c)
            out.append(alphabet[(idx + key[pos % n_key]) % n_alpha])
            pos += 1
        else:
            out.append(c)
    return "".join(out)


def run_gronsfeld_sweep(
    ciphertext: str = K4,
    keys: list[str] | None = None,
    alphabets: dict[str, str] | None = None,
    keyword_eureka_threshold: int = 4,
) -> dict:
    """Run Gronsfeld sweep across K2 coordinate keys and candidate alphabets.

    Args:
        ciphertext:   K4 ciphertext.
        keys:         Digit key candidates (default: K2_COORDINATE_KEYS).
        alphabets:    Name→alphabet dict (default: standard + KRYPTOS).
        keyword_eureka_threshold: Cribs needed to fire Eureka.

    Returns:
        Summary dict with status, best_candidates, run_params.
    """
    from .eureka import EurekaSignal, write_breakthrough_snapshot
    from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

    if keys is None:
        keys = K2_COORDINATE_KEYS
    if alphabets is None:
        alphabets = KNOWN_KEYED_ALPHABETS

    _EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    best: list[dict] = []
    total = 0

    try:
        for key_str in keys:
            for alpha_name, alphabet in alphabets.items():
                candidate = gronsfeld_decrypt(ct, key_str, alphabet)
                total += 1
                hits = sum(1 for w in _EUREKA_WORDS if w in candidate.upper())
                score = combined_instructional_score(candidate, gate_entropy=False)
                if hits >= keyword_eureka_threshold:
                    key_info = {"key": key_str, "alpha_name": alpha_name}
                    snap = write_breakthrough_snapshot(candidate, key_info)
                    raise EurekaSignal(
                        snapshot_path=snap,
                        result={"candidate_text": candidate, "key_info": key_info, "keyword_hits": hits},
                    )
                if hits > 0 or score > 0.5:
                    best.append(
                        {
                            "candidate_text": candidate,
                            "key": key_str,
                            "alpha_name": alpha_name,
                            "keyword_hits": hits,
                            "instructional_score": score,
                        }
                    )
    except EurekaSignal:
        raise

    best.sort(key=lambda r: (-r["keyword_hits"], -r["instructional_score"]))
    return {
        "status": "null_result",
        "attack": "P7_gronsfeld",
        "keys_tested": keys,
        "alphabets": list(alphabets.keys()),
        "total_candidates": total,
        "best_candidates": best[:10],
    }


__all__ = [
    "gronsfeld_decrypt",
    "gronsfeld_encrypt",
    "run_gronsfeld_sweep",
    "K2_COORDINATE_KEYS",
]
