"""Trifid cipher — P9.

A 27-cell (3x3x3) cube fractionation cipher extending Bifid (5x5, pairs) to
triples. Each of the 26 letters plus one filler symbol occupies a unique
cell of the cube, addressed by a coordinate triple ``(layer, row, col)``
each in ``{0, 1, 2}``. The cube's fill order comes from a keyword-mixed
alphabet (reusing :func:`kryptos.k4.quagmire.keyword_alphabet`, the same
keyed-mixing convention used for the Quagmire tableau) with a filler symbol
appended as the 27th slot.

Encryption processes plaintext in blocks of a fixed ``period`` (the last
block may be shorter). For a block of length ``L``:

1. Look up each letter's coordinate triple; write the ``L`` triples as
   three rows of length ``L`` (row 0 = every letter's first coordinate,
   row 1 = second, row 2 = third).
2. Flatten those three rows end to end into one length-``3L`` digit
   sequence.
3. Regroup the flat sequence into ``L`` new triples (three consecutive
   digits each) and map each new triple back through the cube to produce
   one ciphertext letter.

Decryption is the exact inverse: a ciphertext block's ``L`` coordinate
triples, concatenated in order, reconstruct the same length-``3L`` flat
sequence step 2 produced (concatenation and de-interleaving-into-thirds are
inverses of each other), which is then split back into three rows of
length ``L`` and read off as the original per-letter triples.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .eureka import EurekaSignal, write_breakthrough_snapshot
from .physical_grid import K4
from .quagmire import keyword_alphabet
from .quagmire_sweep import _keyword_hits, positional_crib_hits
from .validation import validate_candidate

# 27th cube symbol — never appears in alpha-only plaintext/ciphertext, so it
# only ever shows up (harmlessly) as a byproduct of decrypting an
# incorrect key/period combination, where it simply fails crib scoring.
FILLER = "#"

CANDIDATE_KEYWORDS: list[str] = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "KRYPTOSPALIMPSEST",
    "KRYPTOSABSCISSA",
    "PALIMPSESTABSCISSA",
]

CANDIDATE_PERIODS: list[int] = [3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 24, 97]

_NULL_ARTIFACT_PATH = "K4_TRIFID_NULL.json"


def build_cube_order(keyword: str) -> str:
    """27-symbol cube fill order: keyword-mixed 26-letter alphabet + filler."""
    return keyword_alphabet(keyword) + FILLER


def _coord(cube_order: str, ch: str) -> tuple[int, int, int]:
    i = cube_order.index(ch)
    return (i // 9, (i % 9) // 3, i % 3)


def _letter(cube_order: str, triple: tuple[int, int, int]) -> str:
    a, b, c = triple
    return cube_order[a * 9 + b * 3 + c]


def _clean(text: str) -> str:
    """Uppercase, keep only real letters and the cube's own filler symbol.

    Plain ``isalpha()`` filtering would silently strip ``FILLER`` out of a
    ciphertext that legitimately contains it (any block whose regrouped
    coordinate triple lands on cube index 26), corrupting block boundaries
    on decrypt. Real K4 is alpha-only and never contains ``FILLER``, so this
    only matters for self-consistency (encrypt -> decrypt round-trips) and
    is a no-op against the actual K4 constant.
    """
    return "".join(c for c in text.upper() if c.isalpha() or c == FILLER)


def _encrypt_block(block: str, cube_order: str) -> str:
    coords = [_coord(cube_order, ch) for ch in block]
    length = len(block)
    flat: list[int] = [c[0] for c in coords] + [c[1] for c in coords] + [c[2] for c in coords]
    out = []
    for i in range(length):
        triple = (flat[3 * i], flat[3 * i + 1], flat[3 * i + 2])
        out.append(_letter(cube_order, triple))
    return "".join(out)


def _decrypt_block(block: str, cube_order: str) -> str:
    coords = [_coord(cube_order, ch) for ch in block]
    length = len(block)
    flat: list[int] = []
    for c in coords:
        flat.extend(c)
    row0 = flat[0:length]
    row1 = flat[length : 2 * length]
    row2 = flat[2 * length : 3 * length]
    out = []
    for i in range(length):
        triple = (row0[i], row1[i], row2[i])
        out.append(_letter(cube_order, triple))
    return "".join(out)


def trifid_encrypt(plaintext: str, keyword: str, period: int) -> str:
    """Encrypt ``plaintext`` with a keyword-derived cube, in blocks of ``period``."""
    text = _clean(plaintext)
    if period <= 0:
        raise ValueError("period must be positive")
    cube_order = build_cube_order(keyword)
    out = []
    for start in range(0, len(text), period):
        out.append(_encrypt_block(text[start : start + period], cube_order))
    return "".join(out)


def trifid_decrypt(ciphertext: str, keyword: str, period: int) -> str:
    """Invert :func:`trifid_encrypt`."""
    text = _clean(ciphertext)
    if period <= 0:
        raise ValueError("period must be positive")
    cube_order = build_cube_order(keyword)
    out = []
    for start in range(0, len(text), period):
        out.append(_decrypt_block(text[start : start + period], cube_order))
    return "".join(out)


def run_trifid_attack(
    ciphertext: str = K4,
    candidate_keywords: list[str] | None = None,
    candidate_periods: list[int] | None = None,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
    eureka_snapshot_path: str | Path = "K4_TRIFID_BREAKTHROUGH.md",
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """P9 — Trifid cube-fractionation sweep against K4.

    Tries every (keyword, period) combination as a decrypt (the natural
    attack direction, assuming K4 is Trifid-encrypted plaintext). Every
    candidate crossing the eureka threshold is run through
    :func:`kryptos.k4.validation.validate_candidate`; only a
    ``promote``-passing candidate raises
    :class:`~kryptos.k4.eureka.EurekaSignal`. A null-result artifact is
    always written.
    """
    if candidate_keywords is None:
        candidate_keywords = CANDIDATE_KEYWORDS
    if candidate_periods is None:
        candidate_periods = CANDIDATE_PERIODS

    # Use _clean (not a bare isalpha() filter) so a ciphertext that
    # legitimately contains FILLER round-trips correctly -- see _clean's
    # docstring. Real K4 is alpha-only, so this is a no-op against it.
    ct = _clean(ciphertext)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _reproduce(key_info: dict[str, Any], _ct: str = ct) -> str:
        return trifid_decrypt(_ct, key_info["keyword"], key_info["period"])

    for keyword in candidate_keywords:
        for period in candidate_periods:
            candidate = trifid_decrypt(ct, keyword, period)
            total_tested += 1

            pos_hits = positional_crib_hits(candidate)
            kw_hits = _keyword_hits(candidate)

            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "trifid",
                    "keyword": keyword,
                    "period": period,
                }
                check = validate_candidate(candidate, key_info, _reproduce, param_count=2, exceptions=0)

                if check["promote"]:
                    snap = write_breakthrough_snapshot(
                        candidate,
                        key_info,
                        extra={
                            "positional_crib_hits": pos_hits,
                            "keyword_hits": kw_hits,
                            "validation": check,
                            "sweep_ts": ts_start,
                        },
                        path=eureka_snapshot_path,
                    )
                    raise EurekaSignal(
                        snapshot_path=snap,
                        result={
                            "candidate_text": candidate,
                            "key_info": key_info,
                            "snapshot_path": snap,
                            "positional_crib_hits": pos_hits,
                            "keyword_hits": kw_hits,
                            "validation": check,
                        },
                    )

            if pos_hits > 0 or kw_hits > 0:
                best_candidates.append(
                    {
                        "candidate_text": candidate,
                        "positional_crib_hits": pos_hits,
                        "keyword_hits": kw_hits,
                        "keyword": keyword,
                        "period": period,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "P9_trifid",
        "timestamp": ts_start,
        "run_params": {
            "candidate_keywords": candidate_keywords,
            "candidate_periods": candidate_periods,
            "total_tested": total_tested,
            "positional_eureka_threshold": positional_eureka_threshold,
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
    "FILLER",
    "CANDIDATE_KEYWORDS",
    "CANDIDATE_PERIODS",
    "build_cube_order",
    "trifid_encrypt",
    "trifid_decrypt",
    "run_trifid_attack",
]
