"""Clock-to-Hill 2x2 and 4-char clock Vigenère attacks on K4.

Attack 1 — Clock → Hill 2×2 Invertibility Pre-filter:
  For each Berlin Clock state, form a 2×2 Hill matrix from the first 4 lamp
  values, keep only those invertible mod 26 (~15%), apply Hill 2×2 decryption
  to K4, validate EAST/NORTHEAST/BERLIN/CLOCK cribs.

Attack 2 — 4-char Clock Key → Vigenère with NORTHEAST Anchor:
  Derive a 4-char Vigenère key from each clock state via several encoding
  schemes (not the full 24-element shift sequence), test against K4 with
  positional NORTHEAST gating at position 26.
"""

from __future__ import annotations

import json
from datetime import datetime
from datetime import time as _dt_time
from datetime import timezone
from pathlib import Path
from typing import Any

from .berlin_clock import enumerate_clock_shift_sequences, full_clock_state
from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .hill_cipher import hill_decrypt, matrix_inv_mod
from .keystream_validator import crib_hit_count
from .physical_grid import K4

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


# ---------------------------------------------------------------------------
# Attack 1: Clock → Hill 2×2 invertibility pre-filter
# ---------------------------------------------------------------------------


def clock_state_to_2x2_matrix(shifts: list[int]) -> list[list[int]]:
    """Form a 2×2 Hill matrix from the first 4 values of a clock shift sequence."""
    a, b, c, d = shifts[0] % 26, shifts[1] % 26, shifts[2] % 26, shifts[3] % 26
    return [[a, b], [c, d]]


def run_clock_hill_attack(
    ciphertext: str = K4,
    clock_step_seconds: int = 120,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_CLOCK_HILL_NULL.json",
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Clock → Hill 2×2 invertibility pre-filter attack on K4.

    For each Berlin Clock state:
    1. Form a 2×2 Hill matrix from the first 4 lamp values.
    2. Skip non-invertible matrices mod 26.
    3. Apply Hill 2×2 decryption to K4.
    4. Check EAST/NORTHEAST/BERLIN/CLOCK cribs.
    5. Raise EurekaSignal if all 4 keywords appear simultaneously.

    Returns summary dict. Writes null-result artifact to null_artifact_path
    when no breakthrough is found.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    clock_states = enumerate_clock_shift_sequences(step_seconds=clock_step_seconds)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_states = 0
    invertible_count = 0
    best_candidates: list[dict[str, Any]] = []

    for clock in clock_states:
        shifts = clock["shifts"]
        clock_time = clock["time"]
        total_states += 1

        matrix = clock_state_to_2x2_matrix(shifts)
        if matrix_inv_mod(matrix) is None:
            continue
        invertible_count += 1

        candidate = hill_decrypt(ct, matrix)
        if candidate is None:
            continue

        kw_hits = _keyword_hits(candidate)
        crib_hits = crib_hit_count(candidate)

        if kw_hits >= keyword_eureka_threshold:
            key_info = {
                "attack": "clock_hill_2x2",
                "clock_time": clock_time,
                "clock_shifts_prefix": list(shifts[:4]),
                "hill_matrix": matrix,
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
                    "clock_time": clock_time,
                    "hill_matrix": matrix,
                }
            )

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["crib_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "clock_hill_2x2",
        "timestamp": ts_start,
        "run_params": {
            "clock_step_seconds": clock_step_seconds,
            "total_clock_states": total_states,
            "invertible_states": invertible_count,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


# ---------------------------------------------------------------------------
# Attack 2: 4-char clock key → Vigenère with NORTHEAST anchor
# ---------------------------------------------------------------------------


def _encode_row_sums(cs: dict) -> list[int]:
    return [
        sum(cs["top_hours"]),
        sum(cs["bottom_hours"]),
        sum(1 for v in cs["top_minutes"] if v > 0),
        sum(cs["bottom_minutes"]),
    ]


def _encode_first_4_lamps(cs: dict) -> list[int]:
    combined = cs["top_hours"] + cs["bottom_hours"]
    return [v % 26 for v in combined[:4]]


def _encode_hour_minute_sums(cs: dict) -> list[int]:
    h_total = sum(cs["top_hours"]) * 5 + sum(cs["bottom_hours"])
    m_total = sum(1 for v in cs["top_minutes"] if v > 0) * 5 + sum(cs["bottom_minutes"])
    return [h_total % 26, (h_total // 7) % 26, m_total % 26, (m_total // 7) % 26]


def _encode_row_xor(cs: dict) -> list[int]:
    top_h = sum(cs["top_hours"])
    bot_h = sum(cs["bottom_hours"])
    top_m = sum(1 for v in cs["top_minutes"] if v > 0)
    bot_m = sum(cs["bottom_minutes"])
    return [
        (top_h ^ bot_h) % 26,
        (top_m ^ bot_m) % 26,
        (top_h + top_m) % 26,
        (bot_h + bot_m) % 26,
    ]


CLOCK_KEY_ENCODING_SCHEMES: dict[str, Any] = {
    "row_sums": _encode_row_sums,
    "first_4_lamps": _encode_first_4_lamps,
    "hour_minute_sums": _encode_hour_minute_sums,
    "row_xor": _encode_row_xor,
}


def vigenere_decrypt_ints(text: str, key_ints: list[int]) -> str:
    """Vigenère decrypt using a list of integer shifts (mod 26), standard alphabet."""
    ct = "".join(c for c in text.upper() if c.isalpha())
    n = len(key_ints)
    if n == 0:
        return ct
    return "".join(ALPHABET[(ALPHABET.index(c) - key_ints[i % n]) % 26] for i, c in enumerate(ct))


def run_clock_vigenere_attack(
    ciphertext: str = K4,
    clock_step_seconds: int = 120,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_CLOCK_VIGENERE_NULL.json",
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """4-char clock key → Vigenère with NORTHEAST positional anchor attack.

    For each Berlin Clock state × encoding scheme:
    1. Derive a 4-char Vigenère key (not the full 24-element shift sequence).
    2. Apply Vigenère decryption to K4.
    3. Check NORTHEAST at position 25 and EAST at position 21.
    4. Record candidates with positional matches or crib hits.

    Returns summary dict. Writes null-result artifact when no breakthrough found.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    clock_states = enumerate_clock_shift_sequences(step_seconds=clock_step_seconds)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    for clock in clock_states:
        clock_time = clock["time"]
        h, m, s = (int(x) for x in clock_time.split(":"))
        cs = full_clock_state(_dt_time(h, m, s))

        for scheme_name, encoder in CLOCK_KEY_ENCODING_SCHEMES.items():
            key_ints = [v % 26 for v in encoder(cs)]
            if len(key_ints) != 4:
                continue
            total_tested += 1

            candidate = vigenere_decrypt_ints(ct, key_ints)

            # 2026-09-02: positions were previously one too high (26, 22) --
            # same bug fixed in keystream_validator.K4_CRIBS; see that module.
            northeast_at_25 = len(candidate) >= 34 and candidate[25:34] == "NORTHEAST"
            east_at_21 = len(candidate) >= 25 and candidate[21:25] == "EAST"
            positional_match = int(northeast_at_25) + int(east_at_21)

            kw_hits = _keyword_hits(candidate)
            crib_hits = crib_hit_count(candidate)

            if kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "clock_vigenere_4char",
                    "clock_time": clock_time,
                    "encoding_scheme": scheme_name,
                    "key_ints": key_ints,
                    "key_letters": "".join(ALPHABET[v] for v in key_ints),
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

            if positional_match > 0 or kw_hits > 0 or crib_hits > 0:
                best_candidates.append(
                    {
                        "candidate_text": candidate,
                        "keyword_hits": kw_hits,
                        "crib_hits": crib_hits,
                        "positional_match": positional_match,
                        "clock_time": clock_time,
                        "encoding_scheme": scheme_name,
                        "key_letters": "".join(ALPHABET[v] for v in key_ints),
                    }
                )

    best_candidates.sort(key=lambda r: (-r["positional_match"], -r["keyword_hits"], -r["crib_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "clock_vigenere_4char",
        "timestamp": ts_start,
        "run_params": {
            "clock_step_seconds": clock_step_seconds,
            "encoding_schemes": list(CLOCK_KEY_ENCODING_SCHEMES.keys()),
            "total_tested": total_tested,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


__all__ = [
    "K4",
    "clock_state_to_2x2_matrix",
    "vigenere_decrypt_ints",
    "run_clock_hill_attack",
    "run_clock_vigenere_attack",
    "CLOCK_KEY_ENCODING_SCHEMES",
]
