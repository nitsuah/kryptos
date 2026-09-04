"""P14 — CIA→Berlin great-circle bearing as cipher parameter.

The great-circle bearing from CIA HQ (38.957°N, 77.145°W) to
Berlin (52.520°N, 13.405°E) is approximately 44.4° (NNE).

Three interpretations tested against the 4-crib gate:
  1. Caesar shift: 44 mod 26 = 18 (letter S) applied to K4
  2. Clock-offset: bearing degrees scaled to clock minutes (~88 min) → new CIA timestamps
  3. Vigenère key position offset: key cycle starts at position bearing_int (44)
"""

from __future__ import annotations

import logging
from typing import Any

from .physical_grid import K4  # single source of truth, see physical_grid.py

logger = logging.getLogger(__name__)

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})

CIA_LAT, CIA_LON = 38.957, -77.145
BERLIN_LAT, BERLIN_LON = 52.520, 13.405


def great_circle_bearing(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> float:
    """Initial great-circle bearing from point 1 to point 2 (degrees, 0–360)."""
    import math

    lat1 = math.radians(lat1_deg)
    lat2 = math.radians(lat2_deg)
    dlon = math.radians(lon2_deg - lon1_deg)

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


CIA_BERLIN_BEARING_DEG: float = great_circle_bearing(CIA_LAT, CIA_LON, BERLIN_LAT, BERLIN_LON)
CIA_BERLIN_BEARING_INT: int = round(CIA_BERLIN_BEARING_DEG)  # 44


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in EUREKA_WORDS if w in upper)


def run_bearing_attack(null_artifact_path: str = "K4_P14_BEARING_NULL.json") -> dict[str, Any]:
    """Run all 4 bearing-derived interpretations against K4 and score candidates.

    Returns:
        Summary dict with attack results and best candidates.
    """
    from .k2_clock_states import CIA_TIMESTAMP_TIMES, clock_state_for_time, offset_time_minutes
    from .scoring_instructional import combined_instructional_score
    from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

    bearing = CIA_BERLIN_BEARING_DEG
    bearing_int = CIA_BERLIN_BEARING_INT
    ct = [c for c in K4.upper() if c.isalpha()]

    results: list[dict[str, Any]] = []

    # ── Test 1: Caesar shift bearing_int mod 26 = 18 (S) ──────────────────────
    logger.info("P14 Test 1: Caesar shift %d mod 26 = %d", bearing_int, bearing_int % 26)
    shift = bearing_int % 26
    for alpha_name, alpha in KNOWN_KEYED_ALPHABETS.items():
        candidate = "".join(alpha[(alpha.index(c) - shift) % 26] if c in alpha else c for c in ct)
        hits = _keyword_hits(candidate)
        if hits > 0:
            results.append(
                {
                    "test": "caesar_shift",
                    "shift": shift,
                    "alpha": alpha_name,
                    "keyword_hits": hits,
                    "candidate_text": candidate,
                    "instructional_score": combined_instructional_score(candidate),
                }
            )

    # ── Test 2: Clock-offset timestamps ────────────────────────────────────────
    # bearing_int degrees of a 12-hour clock = bearing_int / 360 * 720 ≈ 102 min
    clock_offset_min = round(bearing_int / 360 * 720)
    logger.info("P14 Test 2: clock offset %d min (from bearing %d°)", clock_offset_min, bearing_int)

    bearing_clock_times = []
    for hhmm, label in CIA_TIMESTAMP_TIMES:
        for sign in (+1, -1):
            new_time = offset_time_minutes(hhmm, sign * clock_offset_min)
            state = clock_state_for_time(new_time)
            bearing_clock_times.append((state, f"{label} ±{clock_offset_min}min bearing"))

    from itertools import permutations

    from .composite_sweep import _keyword_hits as _kh
    from .composite_sweep import _vigenere_decrypt
    from .transposition_analysis import apply_columnar_permutation_reverse

    for state, label in bearing_clock_times:
        for alpha_name, alpha in KNOWN_KEYED_ALPHABETS.items():
            stripped = _vigenere_decrypt("".join(ct), state["shifts"], alpha)
            for n_cols in [7, 8, 10]:
                for perm in list(permutations(range(n_cols)))[:60]:
                    candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                    hits = _kh(candidate)
                    if hits > 0:
                        results.append(
                            {
                                "test": "bearing_clock_offset",
                                "clock_time": state["time"],
                                "alpha": alpha_name,
                                "keyword_hits": hits,
                                "candidate_text": candidate,
                                "instructional_score": combined_instructional_score(candidate),
                                "source": label,
                            }
                        )

    # ── Test 3: Vigenère key index offset by bearing ───────────────────────────
    # Shift the key cycle start to position bearing_int, so key[i] = repeating_key[(i+44)%L]
    logger.info("P14 Test 3: Vigenère key offset by %d positions", bearing_int)
    from datetime import time as dtime

    from .berlin_clock import full_berlin_clock_shifts

    for hhmm, label in CIA_TIMESTAMP_TIMES:
        h, m = int(hhmm[:2]), int(hhmm[3:5])
        shifts = full_berlin_clock_shifts(dtime(h, m, 0))
        n = len(shifts)
        offset_shifts = [shifts[(i + bearing_int) % n] for i in range(n)]
        for alpha_name, alpha in KNOWN_KEYED_ALPHABETS.items():
            stripped = _vigenere_decrypt("".join(ct), offset_shifts, alpha)
            for n_cols in [7, 8, 10]:
                for perm in list(permutations(range(n_cols)))[:60]:
                    candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                    hits = _kh(candidate)
                    if hits > 0:
                        results.append(
                            {
                                "test": "vigenere_key_offset",
                                "clock_time": hhmm,
                                "alpha": alpha_name,
                                "keyword_hits": hits,
                                "candidate_text": candidate,
                                "instructional_score": combined_instructional_score(candidate),
                                "bearing_offset": bearing_int,
                            }
                        )

    results.sort(key=lambda r: (-r["keyword_hits"], -r.get("instructional_score", 0)))

    summary: dict[str, Any] = {
        "status": "null_result" if not any(r["keyword_hits"] >= 4 for r in results) else "eureka",
        "attack": "P14_bearing",
        "cia_berlin_bearing_deg": round(bearing, 2),
        "bearing_int": bearing_int,
        "tests_run": ["caesar_shift", "bearing_clock_offset", "vigenere_key_offset"],
        "best_candidates": results[:10],
        "total_candidates_with_hits": len(results),
    }

    try:
        import json
        from pathlib import Path

        Path(null_artifact_path).write_text(json.dumps(summary, indent=2))
    except Exception:  # noqa: BLE001
        pass

    return summary
