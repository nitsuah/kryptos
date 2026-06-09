"""Systematic Beaufort cipher sweep against K4.

Beaufort is a reciprocal Vigenère variant: P[i] = (K[i] - C[i]) mod 26.
Since encryption and decryption are the same operation, one pass suffices.

Key candidates: KRYPTOS, PALIMPSEST, BERLIN, CLOCK, ABSCISSA, BERLINCLOCK,
NORTHEAST plus several combinations.  Both standard (A-Z) and Kryptos-keyed
(KRYPTOSABCDEFGHIJLMNQUVWXZ) alphabets are tested.  A null-result artifact is
always written so the run is fully provenance-tracked.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .keystream_validator import crib_hit_count

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

BEAUFORT_KEY_CANDIDATES = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "BERLIN",
    "CLOCK",
    "BERLINCLOCK",
    "NORTHEAST",
    "EAST",
    "BERLINCLOCKEAST",
    "KRYPTOSPALIMPSEST",
]

_EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


def beaufort_decrypt_alphabet(ciphertext: str, key: str, alphabet: str) -> str:
    """Beaufort decryption using an arbitrary alphabet: P[i] = (K[i] - C[i]) mod n.

    Characters in ciphertext not present in alphabet are silently dropped.
    """
    ct = [c for c in ciphertext.upper() if c in alphabet]
    key_chars = [k for k in key.upper() if k in alphabet]
    if not key_chars:
        return ""
    n = len(alphabet)
    ki = len(key_chars)
    return "".join(
        alphabet[(alphabet.index(key_chars[i % ki]) - alphabet.index(c)) % n]
        for i, c in enumerate(ct)
    )


def run_beaufort_sweep(
    ciphertext: str = K4,
    key_candidates: list[str] | None = None,
    alphabets: dict[str, str] | None = None,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_BEAUFORT_NULL.json",
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Systematic Beaufort sweep against K4 with known key candidates.

    Tests each (key, alphabet) pair; validates EAST/NORTHEAST/BERLIN/CLOCK
    cribs and raises EurekaSignal on a 4-crib simultaneous match.

    Args:
        ciphertext:              K4 ciphertext (default: canonical 97-char string).
        key_candidates:          Keys to test (default: BEAUFORT_KEY_CANDIDATES).
        alphabets:               Dict of name→alphabet string.
        eureka_snapshot_path:    Breakthrough snapshot destination.
        null_artifact_path:      Null-result provenance artifact destination.
        keyword_eureka_threshold: Keywords required in plaintext to trigger Eureka.

    Returns:
        Summary dict with status, run_params, and best_candidates.
    """
    if key_candidates is None:
        key_candidates = BEAUFORT_KEY_CANDIDATES
    if alphabets is None:
        alphabets = {
            "standard": STANDARD_ALPHABET,
            "keyed_kryptos": KEYED_ALPHABET,
        }

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    for alpha_name, alphabet in alphabets.items():
        ct_filtered = "".join(c for c in ct if c in alphabet)

        for key in key_candidates:
            key_clean = "".join(c for c in key.upper() if c in alphabet)
            if not key_clean:
                continue
            total_tested += 1

            candidate = beaufort_decrypt_alphabet(ct_filtered, key_clean, alphabet)
            kw_hits = _keyword_hits(candidate)
            crib_hits = crib_hit_count(candidate)

            if kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "beaufort_sweep",
                    "key": key,
                    "alphabet_name": alpha_name,
                }
                snap = write_breakthrough_snapshot(
                    candidate,
                    key_info,
                    extra={"keyword_hits": kw_hits, "sweep_ts": ts_start},
                    path=eureka_snapshot_path,
                )
                raise EurekaSignal(
                    snapshot_path=snap,
                    result={
                        "candidate_text": candidate,
                        "key_info": key_info,
                        "snapshot_path": snap,
                        "keyword_hits": kw_hits,
                    },
                )

            if kw_hits > 0 or crib_hits > 0:
                best_candidates.append(
                    {
                        "candidate_text": candidate,
                        "keyword_hits": kw_hits,
                        "crib_hits": crib_hits,
                        "key": key,
                        "alphabet_name": alpha_name,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["crib_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "beaufort_sweep",
        "timestamp": ts_start,
        "run_params": {
            "key_candidates": key_candidates,
            "alphabets": list(alphabets.keys()),
            "total_tested": total_tested,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    return summary


__all__ = [
    "K4",
    "BEAUFORT_KEY_CANDIDATES",
    "STANDARD_ALPHABET",
    "KEYED_ALPHABET",
    "beaufort_decrypt_alphabet",
    "run_beaufort_sweep",
]
