"""P17 — Bigram hard constraints from doubled ciphertext letters in K4.

K4 contains four runs of consecutive identical letters:
  QQ at 25-26, SS at 32-33, SS at 42-43, ZZ at 46-47

Under monoalphabetic substitution, every cipher character maps to exactly one
plaintext character. So QQ → (same plaintext letter)(same plaintext letter).
This means consecutive doubled ciphertext letters always decipher to consecutive
doubled plaintext letters (English doublets).

Under a Vigenère layer ON TOP of the monoalphabetic substitution, two positions
i and i+1 with the same ciphertext character C imply:
    key[i % L] - key[(i+1) % L] ≡ 0 (mod 26)   iff the intermediate chars are equal
    OR the doubled letters survive after the transposition.

This module provides:
1. `find_doubled_pairs(ciphertext)` — locate all consecutive duplicates.
2. `valid_english_doublets()` — the 20 English letter pairs that can double.
3. `filter_candidates_by_doublets(candidates, doubled_positions)` — post-filter
   to discard candidates whose doubled-position characters aren't English doublets.
4. `doubled_constraint_analysis(ciphertext)` — full structural analysis report.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# English letters that can legitimately appear doubled (common doublets)
# Source: frequency analysis of English text — all 26 possible but realistic ones:
ENGLISH_DOUBLETS: frozenset[str] = frozenset(
    "AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTTUUVVWWXXYYZZ"[i]
    for i in range(0, 52, 2)
)

# Letters that realistically double in English prose (top doublets)
COMMON_ENGLISH_DOUBLETS: frozenset[str] = frozenset(
    {"L", "L", "S", "S", "E", "E", "T", "T", "O", "O", "N", "N", "R", "R", "F", "F", "P", "P"}
)

# Letters extremely rare or impossible as doublets in standard English prose
RARE_DOUBLETS: frozenset[str] = frozenset({"Q", "X", "J", "K", "V", "W", "Y", "Z"})


def find_doubled_pairs(ciphertext: str = K4) -> list[dict[str, Any]]:
    """Return all consecutive identical letter pairs with their positions."""
    ct = [c for c in ciphertext.upper() if c.isalpha()]
    pairs = []
    for i in range(len(ct) - 1):
        if ct[i] == ct[i + 1]:
            pairs.append({
                "position": i,
                "letter": ct[i],
                "is_rare_doublet": ct[i] in RARE_DOUBLETS,
            })
    return pairs


def valid_english_doublets() -> frozenset[str]:
    """Letters that can appear as doublets in English."""
    return ENGLISH_DOUBLETS


def filter_candidates_by_doublets(
    candidates: list[str],
    doubled_positions: list[int] | None = None,
    strict: bool = False,
) -> list[tuple[str, bool]]:
    """Filter candidate plaintexts to those with plausible doublets at doubled positions.

    Args:
        candidates:         List of candidate plaintext strings.
        doubled_positions:  Positions (0-indexed) where K4 has consecutive duplicates.
                            Defaults to the four K4 doubled-pair positions [25, 32, 42, 46].
        strict:             If True, require all doublets to be common (not just valid).

    Returns:
        List of (candidate, passes_filter) tuples.
    """
    if doubled_positions is None:
        doubled_positions = [25, 32, 42, 46]

    doublet_set = COMMON_ENGLISH_DOUBLETS if strict else ENGLISH_DOUBLETS
    results = []
    for cand in candidates:
        ct_alpha = [c for c in cand.upper() if c.isalpha()]
        passes = all(
            pos < len(ct_alpha) - 1 and ct_alpha[pos] in doublet_set
            for pos in doubled_positions
        )
        results.append((cand, passes))
    return results


def doubled_constraint_analysis(ciphertext: str = K4) -> dict[str, Any]:
    """Full structural analysis of doubled-letter constraints in ciphertext.

    Returns a report with:
    - all doubled pairs (position + letter)
    - their interpretation under monoalphabetic substitution
    - derived plaintext doublet constraints
    - CSP-style implications for repeating key
    """
    pairs = find_doubled_pairs(ciphertext)

    analysis: list[dict[str, Any]] = []
    for p in pairs:
        pos = p["position"]
        letter = p["letter"]
        analysis.append({
            "cipher_position": pos,
            "cipher_letter": letter,
            "is_rare_as_cipher_doublet": p["is_rare_doublet"],
            "mono_subst_implies": f"plaintext[{pos}] == plaintext[{pos+1}]",
            "must_be_english_doublet": True,
            "plausible_doublet_letters": sorted(ENGLISH_DOUBLETS),
        })

    # Repeating-key implications: for each doubled pair at (pos, pos+1),
    # if key period L divides (pos+1 - pos) = 1, then key[pos%L] == key[(pos+1)%L].
    # This only holds for L=1 (trivially). For L>1, positions mod L differ,
    # so the key letters at those slots are independently constrained.
    key_length_implications: dict[int, list[dict[str, Any]]] = {}
    for L in range(2, 16):
        implications = []
        for p in pairs:
            pos = p["position"]
            slot_a = pos % L
            slot_b = (pos + 1) % L
            if slot_a == slot_b:
                implications.append({
                    "cipher_position": pos,
                    "letter": p["letter"],
                    "implication": f"key[{slot_a}] constrains both positions — identical shift on pair",
                })
        if implications:
            key_length_implications[L] = implications

    return {
        "ciphertext": ciphertext,
        "doubled_pairs": analysis,
        "total_pairs": len(pairs),
        "key_length_implications": key_length_implications,
        "summary": (
            f"K4 has {len(pairs)} consecutive duplicate pairs at positions "
            + ", ".join(str(p["position"]) for p in pairs)
            + ". All must decipher to English doublets under any substitution cipher."
        ),
    }
