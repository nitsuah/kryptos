"""Physical-grid keystream generator for K4.

The right-hand copper screen of the Kryptos sculpture is a 26x26 Vigenere
tableau built from the KRYPTOS-keyed alphabet: row 0 is the keyed alphabet
``KRYPTOSABCDEFGHIJLMNQUVWXZ`` and each subsequent row is that alphabet
rotated one position left. The "physical keystream" hypothesis is that the
intended K4 key is read off this physical tableau along some geometric path
rather than being a dictionary word.

This module builds the tableau and walks it along several geometric routes
(rows, columns, main/anti diagonals, and boustrophedon/serpentine variants)
to produce candidate keystreams, then feeds each into the Quagmire III solver
(KRYPTOS tableau) against K4 with the four confirmed positional cribs as a
gate. A null-result artifact is always written; >=3 positional cribs or >=4
keywords raises EurekaSignal.

Note on diagonals: because the tableau is cyclic (``grid[i][j] =
keyed[(i + j) % 26]``), its diagonals are mathematically degenerate — each
anti-diagonal (``i + j`` constant) is a single repeated letter (equivalent to
a Caesar shift) and each main diagonal (``j - i`` constant) cycles through
only 13 distinct letters. They are cheap to test and kept for completeness,
but the rows, columns, and serpentine reads are the substantive keystreams.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .quagmire import keyword_alphabet, quagmire3_decrypt
from .quagmire_sweep import _keyword_hits, positional_crib_hits

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

SIZE = 26


def build_tableau(alphabet_keyword: str = "KRYPTOS") -> list[list[str]]:
    """Build the 26x26 keyed Vigenere tableau.

    Row 0 is the keyed alphabet; row i is that alphabet rotated i places left.
    """
    keyed = keyword_alphabet(alphabet_keyword)
    return [[keyed[(i + j) % SIZE] for j in range(SIZE)] for i in range(SIZE)]


def _rows(grid: list[list[str]]) -> list[str]:
    return ["".join(row) for row in grid]


def _columns(grid: list[list[str]]) -> list[str]:
    return ["".join(grid[r][c] for r in range(SIZE)) for c in range(SIZE)]


def _main_diagonals(grid: list[list[str]]) -> list[str]:
    """Wrapped main diagonals (down-right): one per starting offset."""
    return ["".join(grid[i][(i + d) % SIZE] for i in range(SIZE)) for d in range(SIZE)]


def _anti_diagonals(grid: list[list[str]]) -> list[str]:
    """Wrapped anti-diagonals (down-left): one per starting offset."""
    return ["".join(grid[i][(d - i) % SIZE] for i in range(SIZE)) for d in range(SIZE)]


def _boustrophedon(lines: list[str]) -> str:
    """Serpentine concatenation: reverse every other line, then join."""
    return "".join(line if i % 2 == 0 else line[::-1] for i, line in enumerate(lines))


def candidate_keystreams(alphabet_keyword: str = "KRYPTOS") -> dict[str, str]:
    """Generate named candidate keystreams by walking the tableau.

    Returns a dict of route-name -> keystream string. Routes include each of
    the 26 rows/columns/diagonals individually plus full-grid serpentine reads
    in row, column, and diagonal order.
    """
    grid = build_tableau(alphabet_keyword)
    rows = _rows(grid)
    cols = _columns(grid)
    main_diags = _main_diagonals(grid)
    anti_diags = _anti_diagonals(grid)

    streams: dict[str, str] = {}
    for i, row in enumerate(rows):
        streams[f"row_{i:02d}"] = row
    for i, col in enumerate(cols):
        streams[f"col_{i:02d}"] = col
    for i, diag in enumerate(main_diags):
        streams[f"maindiag_{i:02d}"] = diag
    for i, diag in enumerate(anti_diags):
        streams[f"antidiag_{i:02d}"] = diag

    # Full-grid serpentine reads (length 676) — long aperiodic keystreams
    streams["serpentine_rows"] = _boustrophedon(rows)
    streams["serpentine_cols"] = _boustrophedon(cols)
    streams["serpentine_maindiag"] = _boustrophedon(main_diags)
    streams["serpentine_antidiag"] = _boustrophedon(anti_diags)
    return streams


def run_physical_grid_attack(
    ciphertext: str = K4,
    alphabet_keyword: str = "KRYPTOS",
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_PHYSICAL_GRID_NULL.json",
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Walk the Kryptos tableau for keystreams and Quagmire-III-decrypt K4.

    Returns a summary dict (status, run_params, best_candidates) and writes it
    to ``null_artifact_path``. Raises EurekaSignal on a crib breakthrough.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    streams = candidate_keystreams(alphabet_keyword)
    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    for route, keystream in streams.items():
        for base in (None, "A"):
            total_tested += 1
            candidate = quagmire3_decrypt(ct, keystream, alphabet_keyword, base)
            pos_hits = positional_crib_hits(candidate)
            kw_hits = _keyword_hits(candidate)

            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "physical_grid",
                    "route": route,
                    "keystream": keystream,
                    "alphabet_keyword": alphabet_keyword,
                    "indicator_base": base,
                }
                snap = write_breakthrough_snapshot(
                    candidate,
                    key_info,
                    extra={"positional_crib_hits": pos_hits, "keyword_hits": kw_hits, "sweep_ts": ts_start},
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
                    },
                )

            if pos_hits > 0 or kw_hits > 0:
                best_candidates.append(
                    {
                        "candidate_text": candidate,
                        "positional_crib_hits": pos_hits,
                        "keyword_hits": kw_hits,
                        "route": route,
                        "indicator_base": base,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "physical_grid",
        "timestamp": ts_start,
        "run_params": {
            "alphabet_keyword": alphabet_keyword,
            "routes": list(streams.keys()),
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
    "SIZE",
    "build_tableau",
    "candidate_keystreams",
    "run_physical_grid_attack",
]
