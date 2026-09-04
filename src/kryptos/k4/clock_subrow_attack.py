"""Non-standard Berlin Clock sub-row encoding and lamp-count transposition attacks.

Attack 3 — Non-standard Berlin Clock sub-row encodings:
  Tests short Vigenère keys derived from individual Berlin Clock lamp rows
  (not the full 24-element concatenated sequence used in all prior sweeps).
  Schemes: 5-hour row only, top-2 rows, minute rows only, row-sum keyed offset.

Attack 4 — Berlin Clock lamp counts as transposition column widths:
  Uses lamp row values [h5, h1, m5, m1] as column counts for columnar
  transposition attempts, not as Vigenère shifts.  Both multi-round (sequential
  application of each width) and single-round (each width independently) are
  tested with identity and reverse column orderings.
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
from .keystream_validator import crib_hit_count
from .physical_grid import K4
from .transposition import apply_columnar_permutation

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


def _vigenere_decrypt_shifts(text: str, shifts: list[int]) -> str:
    """Apply integer shifts cyclically as Vigenère decryption (standard alphabet)."""
    ct = "".join(c for c in text.upper() if c.isalpha())
    n = len(shifts)
    if n == 0:
        return ct
    return "".join(ALPHABET[(ALPHABET.index(c) - shifts[i % n]) % 26] for i, c in enumerate(ct))


# ---------------------------------------------------------------------------
# Attack 3: Non-standard Berlin Clock sub-row encoding schemes
# ---------------------------------------------------------------------------


def _subrow_5hour(cs: dict) -> list[int]:
    """5-hour row only: count of lit top_hours lamps (0-4)."""
    return [sum(cs["top_hours"])]


def _subrow_top2(cs: dict) -> list[int]:
    """Top 2 rows: h5 count (0-4) and h1 count (0-4)."""
    return [sum(cs["top_hours"]), sum(cs["bottom_hours"])]


def _subrow_minutes_only(cs: dict) -> list[int]:
    """Minute rows only: m5 active count (0-11) and m1 count (0-4)."""
    m5_count = sum(1 for v in cs["top_minutes"] if v > 0)
    m1_count = sum(cs["bottom_minutes"])
    return [m5_count, m1_count]


def _subrow_keyed_offset(cs: dict) -> list[int]:
    """All four rows as keyed-alphabet offsets: each row sum mod 26."""
    return [
        sum(cs["top_hours"]) % 26,
        sum(cs["bottom_hours"]) % 26,
        sum(1 for v in cs["top_minutes"] if v > 0) % 26,
        sum(cs["bottom_minutes"]) % 26,
    ]


SUBROW_ENCODING_SCHEMES: dict[str, Any] = {
    "5hour_row": _subrow_5hour,
    "top_2_rows": _subrow_top2,
    "minutes_only": _subrow_minutes_only,
    "row_sum_keyed_offset": _subrow_keyed_offset,
}


def run_clock_subrow_attack(
    ciphertext: str = K4,
    clock_step_seconds: int = 120,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_CLOCK_SUBROW_NULL.json",
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Non-standard Berlin Clock sub-row Vigenère attack on K4.

    Tests period-1 to period-4 keys derived from individual Berlin Clock lamp
    rows, rather than the full 24-element shift sequence used in all prior
    sweeps.  Each clock state is tested with all four encoding schemes.

    Returns summary dict. Writes null-result artifact on completion without hit.
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

        for scheme_name, encoder in SUBROW_ENCODING_SCHEMES.items():
            shifts = encoder(cs)
            if not shifts:
                continue
            total_tested += 1

            candidate = _vigenere_decrypt_shifts(ct, shifts)
            kw_hits = _keyword_hits(candidate)
            crib_hits = crib_hit_count(candidate)

            if kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "clock_subrow_vigenere",
                    "clock_time": clock_time,
                    "encoding_scheme": scheme_name,
                    "shifts": shifts,
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
                        "encoding_scheme": scheme_name,
                        "shifts": shifts,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["crib_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "clock_subrow_vigenere",
        "timestamp": ts_start,
        "run_params": {
            "clock_step_seconds": clock_step_seconds,
            "encoding_schemes": list(SUBROW_ENCODING_SCHEMES.keys()),
            "total_tested": total_tested,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


# ---------------------------------------------------------------------------
# Attack 4: Berlin Clock lamp counts as transposition column widths
# ---------------------------------------------------------------------------


def lamp_row_widths(cs: dict) -> list[int]:
    """Extract [h5, h1, m5, m1] lamp row counts as column-width candidates."""
    h5 = sum(cs["top_hours"])
    h1 = sum(cs["bottom_hours"])
    m5 = sum(1 for v in cs["top_minutes"] if v > 0)
    m1 = sum(cs["bottom_minutes"])
    return [h5, h1, m5, m1]


def _apply_columnar_with_perm(text: str, n_cols: int, reverse_order: bool = False) -> str:
    """Single columnar transposition pass; identity or reverse column ordering."""
    ct = "".join(c for c in text.upper() if c.isalpha())
    if n_cols < 2 or n_cols > len(ct):
        return ct
    perm = tuple(range(n_cols - 1, -1, -1)) if reverse_order else tuple(range(n_cols))
    return apply_columnar_permutation(ct, n_cols, perm)


def run_clock_transposition_attack(
    ciphertext: str = K4,
    clock_step_seconds: int = 120,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_CLOCK_TRANSPOS_NULL.json",
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Berlin Clock lamp counts as transposition column widths attack on K4.

    For each clock state, uses [h5, h1, m5, m1] lamp counts as column widths:
    - Multi-round: apply each valid width sequentially (identity ordering).
    - Single-round: apply each valid width independently (identity + reverse).

    This is the first systematic test of the lamp-counts-as-widths hypothesis;
    previously all clock sweeps used shifts as Vigenère keys only.

    Returns summary dict. Writes null-result artifact on completion without hit.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    clock_states = enumerate_clock_shift_sequences(step_seconds=clock_step_seconds)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _check_and_record(candidate: str, meta: dict) -> None:
        nonlocal total_tested
        total_tested += 1
        kw_hits = _keyword_hits(candidate)
        crib_hits = crib_hit_count(candidate)

        if kw_hits >= keyword_eureka_threshold:
            snap = write_breakthrough_snapshot(
                candidate,
                meta,
                extra={"keyword_hits": kw_hits, "sweep_ts": ts_start},
                path=eureka_snapshot_path,
            )
            raise EurekaSignal(
                snapshot_path=snap,
                result={
                    "candidate_text": candidate,
                    "key_info": meta,
                    "snapshot_path": snap,
                    "keyword_hits": kw_hits,
                },
            )
        if kw_hits > 0 or crib_hits > 0:
            best_candidates.append(
                {
                    **meta,
                    "candidate_text": candidate,
                    "keyword_hits": kw_hits,
                    "crib_hits": crib_hits,
                }
            )

    for clock in clock_states:
        clock_time = clock["time"]
        h, m, s = (int(x) for x in clock_time.split(":"))
        cs = full_clock_state(_dt_time(h, m, s))
        widths = lamp_row_widths(cs)
        valid_widths = [w for w in widths if 2 <= w <= len(ct)]
        if not valid_widths:
            continue

        # Multi-round: apply each valid width in sequence (identity ordering)
        multi = ct
        for w in valid_widths:
            multi = _apply_columnar_with_perm(multi, w, reverse_order=False)
        _check_and_record(
            multi,
            {
                "attack": "clock_lamp_transposition",
                "variant": "multi_round_identity",
                "clock_time": clock_time,
                "widths": widths,
                "valid_widths": valid_widths,
            },
        )

        # Multi-round: reverse ordering
        multi_rev = ct
        for w in valid_widths:
            multi_rev = _apply_columnar_with_perm(multi_rev, w, reverse_order=True)
        _check_and_record(
            multi_rev,
            {
                "attack": "clock_lamp_transposition",
                "variant": "multi_round_reverse",
                "clock_time": clock_time,
                "widths": widths,
                "valid_widths": valid_widths,
            },
        )

        # Single-round: each valid width with identity and reverse
        for w in valid_widths:
            for reverse in (False, True):
                cand = _apply_columnar_with_perm(ct, w, reverse_order=reverse)
                _check_and_record(
                    cand,
                    {
                        "attack": "clock_lamp_transposition",
                        "variant": f"single_{'reverse' if reverse else 'identity'}",
                        "clock_time": clock_time,
                        "width": w,
                        "widths": widths,
                    },
                )

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["crib_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "clock_lamp_transposition",
        "timestamp": ts_start,
        "run_params": {
            "clock_step_seconds": clock_step_seconds,
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
    "lamp_row_widths",
    "run_clock_subrow_attack",
    "run_clock_transposition_attack",
    "SUBROW_ENCODING_SCHEMES",
]
