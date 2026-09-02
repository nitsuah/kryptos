"""P18 — Repeating-key CSP from 22 confirmed crib shift values.

The four confirmed K4 cribs yield 24 known (ciphertext_position, Vigenère_shift)
pairs (under standard alphabet, no transposition assumption):

    EAST      @ positions 21-24  → shifts [1, 11, 25, 2]
    NORTHEAST @ positions 25-33  → shifts [3, 2, 24, 24, 6, 2, 10, 0, 25]
    BERLIN    @ positions 63-68  → shifts [12, 20, 24, 10, 11, 6]
    CLOCK     @ positions 69-73  → shifts [10, 14, 17, 13, 0]

2026-09-02: EAST/NORTHEAST were previously one position too high (22-25,
26-34), the same bug fixed in ``keystream_validator.K4_CRIBS`` -- see that
module for the full explanation. BERLIN/CLOCK were already correct.

For a repeating Vigenère key of period L, any two ciphertext positions that are
≡ mod L must share the same key letter (same shift). This CSP is purely structural:
it does NOT require knowledge of the substitution alphabet or transposition grid.

A consistent solution at period L means a key of that length is not contradicted
by the known cribs under a direct (no-transposition) Vigenère hypothesis.

Note: If a transposition layer precedes the Vigenère, the crib positions in K4 do
NOT directly correspond to Vigenère input positions — so consistency here implies
the Vigenère is applied directly to K4 (or the transposition is an identity perm).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CRIB_SHIFTS: list[tuple[int, int]] = [
    # (ciphertext_position_0indexed, vigenere_shift_mod_26)
    # EAST @ 21-24   ciphertext FLRV  plaintext EAST
    (21, 1),
    (22, 11),
    (23, 25),
    (24, 2),
    # NORTHEAST @ 25-33   ciphertext QQPRNGKSS  plaintext NORTHEAST
    (25, 3),
    (26, 2),
    (27, 24),
    (28, 24),
    (29, 6),
    (30, 2),
    (31, 10),
    (32, 0),
    (33, 25),
    # BERLIN @ 63-68   ciphertext NYPVTT  plaintext BERLIN
    (63, 12),
    (64, 20),
    (65, 24),
    (66, 10),
    (67, 11),
    (68, 6),
    # CLOCK @ 69-73   ciphertext MZFPK  plaintext CLOCK
    (69, 10),
    (70, 14),
    (71, 17),
    (72, 13),
    (73, 0),
]


def _shifts_for_text(cipher: str, plain: str, start: int) -> list[tuple[int, int]]:
    """Compute (position, shift) pairs for a single crib window."""
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pairs = []
    for i, (c, p) in enumerate(zip(cipher.upper(), plain.upper())):
        if c.isalpha() and p.isalpha():
            shift = (alpha.index(c) - alpha.index(p)) % 26
            pairs.append((start + i, shift))
    return pairs


def solve_key_csp(
    key_lengths: range | list[int] = range(2, 21),
    crib_shifts: list[tuple[int, int]] = CRIB_SHIFTS,
) -> dict[int, list[int | None]]:
    """Find key lengths consistent with all 22 known (position, shift) constraints.

    Args:
        key_lengths:    Periods to test (inclusive range or list).
        crib_shifts:    List of (ciphertext_position, shift_mod_26) pairs.

    Returns:
        Dict mapping each consistent key length to its partial key vector.
        Slots without a constraint remain None; fully filled slots are integers 0-25.
    """
    consistent: dict[int, list[int | None]] = {}

    for L in key_lengths:
        key: list[int | None] = [None] * L
        ok = True

        for pos, shift in crib_shifts:
            slot = pos % L
            if key[slot] is None:
                key[slot] = shift
            elif key[slot] != shift:
                ok = False
                break

        if ok:
            consistent[L] = key

    return consistent


def partial_key_to_alphabet(partial_key: list[int | None]) -> list[str]:
    """Convert partial int key to letter representation (? for unknown slots)."""
    return [STANDARD[s] if s is not None else "?" for s in partial_key]


def complete_partial_key(partial_key: list[int | None], ciphertext: str = K4) -> list[dict[str, Any]]:
    """Attempt Vigenère decryption using known key slots; enumerate unknown slots.

    Returns top candidates (keyword_hits > 0) with their filled key.
    """
    from .scoring_instructional import combined_instructional_score

    unknown_slots = [i for i, s in enumerate(partial_key) if s is None]
    L = len(partial_key)
    ct = [c for c in ciphertext.upper() if c.isalpha()]
    eureka_words = {"EAST", "NORTHEAST", "BERLIN", "CLOCK"}

    # If all slots known, decrypt directly
    if not unknown_slots:
        full_key: list[int] = [s for s in partial_key if s is not None]
        candidate = "".join(STANDARD[(STANDARD.index(c) - full_key[i % L]) % 26] for i, c in enumerate(ct))
        hits = sum(1 for w in eureka_words if w in candidate)
        return [{"candidate_text": candidate, "key": partial_key[:], "keyword_hits": hits}]

    # Enumerate unknown slots (limit to prevent combinatorial explosion)
    if len(unknown_slots) > 3:
        logger.warning("P18: %d unknown slots — too many to enumerate exhaustively", len(unknown_slots))
        return []

    results: list[dict[str, Any]] = []
    from itertools import product

    for vals in product(range(26), repeat=len(unknown_slots)):
        key: list[int] = [s if s is not None else 0 for s in partial_key]
        for slot, val in zip(unknown_slots, vals):
            key[slot] = val
        candidate = "".join(STANDARD[(STANDARD.index(c) - key[i % L]) % 26] for i, c in enumerate(ct))
        hits = sum(1 for w in eureka_words if w in candidate)
        if hits > 0:
            score = combined_instructional_score(candidate)
            results.append(
                {
                    "candidate_text": candidate,
                    "keyword_hits": hits,
                    "instructional_score": score,
                    "key": key,
                    "key_str": "".join(STANDARD[s] for s in key),
                }
            )

    results.sort(key=lambda r: (-r["keyword_hits"], -r["instructional_score"]))
    return results[:50]


def run_key_csp_attack(
    key_lengths: range = range(2, 21),
    null_artifact_path: str = "K4_P18_KEY_CSP_NULL.json",
) -> dict[str, Any]:
    """Run P18 CSP solver: enumerate consistent key lengths, try to complete each.

    Returns summary dict with consistent_lengths, partial_keys, and any
    completed-key candidates with keyword hits.
    """
    import json
    from datetime import datetime, timezone

    consistent = solve_key_csp(key_lengths=key_lengths)

    logger.info("P18 CSP: tested L=%s, %d consistent lengths found", list(key_lengths), len(consistent))

    all_candidates: list[dict[str, Any]] = []
    csp_results: list[dict[str, Any]] = []

    for L, partial_key in consistent.items():
        letter_key = partial_key_to_alphabet(partial_key)
        filled = sum(1 for s in partial_key if s is not None)
        logger.info("  L=%d: %d/%d slots constrained — partial key %s", L, filled, L, "".join(letter_key))

        candidates = complete_partial_key(partial_key)
        csp_results.append(
            {
                "key_length": L,
                "partial_key": letter_key,
                "constrained_slots": filled,
                "total_slots": L,
                "candidates_with_hits": len(candidates),
            }
        )
        all_candidates.extend(candidates)

    all_candidates.sort(key=lambda r: (-r["keyword_hits"], -r.get("instructional_score", 0)))
    top = all_candidates[:10]

    summary: dict[str, Any] = {
        "status": "null_result" if not any(c["keyword_hits"] >= 4 for c in all_candidates) else "eureka",
        "attack": "P18_key_csp",
        "key_lengths_tested": list(key_lengths),
        "consistent_lengths": list(consistent.keys()),
        "csp_results": csp_results,
        "best_candidates": top,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    try:
        from pathlib import Path

        Path(null_artifact_path).write_text(json.dumps(summary, indent=2))
        logger.info("P18: null artifact written to %s", null_artifact_path)
    except Exception:  # noqa: BLE001
        pass

    return summary
