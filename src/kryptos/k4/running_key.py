"""Running-key attack for K4 — Frontier P6.

Uses the first 97 characters of K3's confirmed plaintext as a Vigenère
running key for K4.  Sanborn said the sections "build on each other."

K3 confirmed plaintext (336 chars, double-rotation transposition of K3 cipher):
  SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED
  THELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTHEFINDINGOFTHISCHAMBER
  POINTINGTOABOVEWHATTURNEDOUTTOBEACLOSEDLOWERPASSAGECONNECTING
  THEHIEROGLYPHICENCRYPTED...  (first 97 chars used)
"""

from __future__ import annotations

from .physical_grid import K4
from .scoring_instructional import combined_instructional_score

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# K3 confirmed plaintext — first 97 alpha chars as running key
K3_PLAINTEXT_FULL = (
    "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBERED"
    "THELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTHEFINDINGOFTHISCHAMBER"
    "POINTINGTOABOVEWHATTURNEDOUTTOBEACLOSEDLOWERPASSAGECONNECTING"
)
K3_KEY_97 = "".join(c for c in K3_PLAINTEXT_FULL.upper() if c.isalpha())[:97]


def running_key_decrypt(ciphertext: str, key: str, alphabet: str = STANDARD) -> str:
    """Vigenère decrypt using a running key (key length ≥ ciphertext length).

    Unlike a repeating Vigenère, each key character is used only once.
    """
    ct_letters = [c for c in ciphertext.upper() if c.isalpha()]
    key_letters = [c for c in key.upper() if c in alphabet]
    n_alpha = len(alphabet)
    out: list[str] = []
    for i, c in enumerate(ct_letters):
        if i >= len(key_letters):
            out.append(c)  # key exhausted — pass through
            continue
        ci = alphabet.index(c) if c in alphabet else -1
        ki = alphabet.index(key_letters[i])
        if ci >= 0:
            out.append(alphabet[(ci - ki) % n_alpha])
        else:
            out.append(c)
    return "".join(out)


def run_k3_running_key_attack(
    ciphertext: str = K4,
    keyword_eureka_threshold: int = 4,
) -> dict:
    """Test K3 plaintext (first 97 chars) as running Vigenère key for K4.

    Variants tested:
      1. Standard alphabet, K3 key direct
      2. Standard alphabet, K3 key reversed
      3. KRYPTOS keyed alphabet, K3 key direct
      4. KRYPTOS keyed alphabet, K3 key reversed
    """
    from .eureka import EurekaSignal, write_breakthrough_snapshot
    from .vigenere_key_recovery import KEYED_ALPHABET

    _EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())

    variants = [
        ("standard_direct", STANDARD, K3_KEY_97),
        ("standard_reversed", STANDARD, K3_KEY_97[::-1]),
        ("kryptos_direct", KEYED_ALPHABET, K3_KEY_97),
        ("kryptos_reversed", KEYED_ALPHABET, K3_KEY_97[::-1]),
    ]

    best: list[dict] = []
    try:
        for label, alphabet, key in variants:
            candidate = running_key_decrypt(ct, key, alphabet)
            hits = sum(1 for w in _EUREKA_WORDS if w in candidate.upper())
            score = combined_instructional_score(candidate, gate_entropy=False)
            if hits >= keyword_eureka_threshold:
                key_info = {"variant": label, "key_preview": key[:20]}
                snap = write_breakthrough_snapshot(candidate, key_info)
                raise EurekaSignal(
                    snapshot_path=snap, result={"candidate_text": candidate, "key_info": key_info, "keyword_hits": hits}
                )
            best.append(
                {
                    "variant": label,
                    "candidate_text": candidate,
                    "keyword_hits": hits,
                    "instructional_score": score,
                }
            )
    except EurekaSignal:
        raise

    best.sort(key=lambda r: (-r["keyword_hits"], -r["instructional_score"]))
    return {
        "status": "null_result",
        "attack": "P6_k3_running_key",
        "k3_key_preview": K3_KEY_97[:20] + "…",
        "variants_tested": [v[0] for v in variants],
        "best_candidates": best,
    }


__all__ = [
    "running_key_decrypt",
    "run_k3_running_key_attack",
    "K3_KEY_97",
    "K3_PLAINTEXT_FULL",
]
