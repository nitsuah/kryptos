"""Myszkowski transposition cipher — P8.

A repeated-letter-keyword columnar transposition. Unlike ordinary columnar
transposition (one column per key letter, columns read independently in key
order), Myszkowski numbers key letters by their *alphabetical rank among
distinct letters* — so repeated letters in the keyword share the same
column-group number. Columns within a shared group are not read one at a
time; they are read together, row by row, left to right across the tied
columns, before moving on to the next group.

``KRYPTOS`` itself has no repeated letters (its group numbering degenerates
to plain columnar transposition, already covered by
:mod:`kryptos.k4.transposition`), so it does not exercise Myszkowski's
distinguishing behaviour. The two Kryptos-relevant keywords that *do* have
repeats are the K1 and K2 keys:

- ``ABSCISSA``  — A appears twice, S appears twice (groups: A,B,S,C,I,S,S,A)
- ``PALIMPSEST`` — P appears twice, S appears twice, T appears... actually
  only S repeats twice and P repeats twice in PALIMPSEST; kept as a
  candidate regardless since it is K2's key and demonstrably has repeats.

No new primitives were needed beyond a from-scratch encrypt/decrypt pair —
the grouped-row read pattern is fundamentally different from the
column-permutation approach in :mod:`kryptos.k4.transposition`
(``apply_columnar_permutation`` reads whole columns sequentially; Myszkowski
interleaves tied columns row-by-row), so it is not reducible to a call into
that module. ``keyword_alphabet``-style key handling is reused from
:mod:`kryptos.k4.quagmire` conventions but the ordering here is purely
numeric (alphabetical rank), not an alphabet substitution.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .eureka import EurekaSignal, write_breakthrough_snapshot
from .quagmire_sweep import _keyword_hits, positional_crib_hits
from .validation import validate_candidate

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# K1 and K2's own keys are the only Kryptos-relevant keywords with repeated
# letters (KRYPTOS has none, so it can't demonstrate Myszkowski behaviour).
CANDIDATE_KEYWORDS: list[str] = ["ABSCISSA", "PALIMPSEST"]

_NULL_ARTIFACT_PATH = "K4_MYSZKOWSKI_NULL.json"


def keyword_to_myszkowski_groups(keyword: str) -> list[int]:
    """Map each keyword letter to its alphabetical-rank group (1-indexed).

    Repeated letters share the same group number, e.g. ``ABSCISSA`` (A, B,
    S, C, I, S, S, A) has distinct sorted letters A,B,C,I,S -> ranks
    1,2,3,4,5, so the per-position groups are ``[1, 2, 5, 3, 4, 5, 5, 1]``.
    """
    upper = "".join(c for c in keyword.upper() if c.isalpha())
    distinct_sorted = sorted(set(upper))
    rank = {ch: i + 1 for i, ch in enumerate(distinct_sorted)}
    return [rank[ch] for ch in upper]


def _column_lengths(n_chars: int, n_cols: int) -> list[int]:
    """Row-major grid fill: first ``full_cols`` columns get the extra row.

    Mirrors the exact convention used by
    :func:`kryptos.k4.transposition.apply_columnar_permutation`.
    """
    n_rows = -(-n_chars // n_cols)  # ceil division
    remainder = n_chars % n_cols
    full_cols = remainder if remainder != 0 else n_cols
    return [n_rows if c < full_cols else n_rows - 1 for c in range(n_cols)]


def myszkowski_encrypt(plaintext: str, keyword: str) -> str:
    """Encrypt via Myszkowski transposition keyed by ``keyword``.

    Plaintext is written into a grid row by row under the keyword's
    columns; ciphertext is read off group by group (ascending rank), and
    within a multi-column group, row by row across the tied columns.
    """
    text = "".join(c for c in plaintext.upper() if c.isalpha())
    groups = keyword_to_myszkowski_groups(keyword)
    n_cols = len(groups)
    if n_cols == 0 or not text:
        return text

    n_rows = -(-len(text) // n_cols)
    grid: list[list[str]] = [["" for _ in range(n_cols)] for _ in range(n_rows)]
    idx = 0
    for r in range(n_rows):
        for c in range(n_cols):
            if idx < len(text):
                grid[r][c] = text[idx]
                idx += 1

    out: list[str] = []
    for group_num in sorted(set(groups)):
        cols = [c for c, g in enumerate(groups) if g == group_num]
        for r in range(n_rows):
            for c in cols:
                if grid[r][c]:
                    out.append(grid[r][c])
    return "".join(out)


def myszkowski_decrypt(ciphertext: str, keyword: str) -> str:
    """Invert :func:`myszkowski_encrypt`."""
    text = "".join(c for c in ciphertext.upper() if c.isalpha())
    groups = keyword_to_myszkowski_groups(keyword)
    n_cols = len(groups)
    if n_cols == 0 or not text:
        return text

    n_rows = -(-len(text) // n_cols)
    col_lengths = _column_lengths(len(text), n_cols)

    grid: list[list[str]] = [["" for _ in range(n_cols)] for _ in range(n_rows)]
    idx = 0
    for group_num in sorted(set(groups)):
        cols = [c for c, g in enumerate(groups) if g == group_num]
        for r in range(n_rows):
            for c in cols:
                if r < col_lengths[c] and idx < len(text):
                    grid[r][c] = text[idx]
                    idx += 1

    out: list[str] = []
    for r in range(n_rows):
        for c in range(n_cols):
            if grid[r][c]:
                out.append(grid[r][c])
    return "".join(out)


def run_myszkowski_attack(
    ciphertext: str = K4,
    candidate_keywords: list[str] | None = None,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
    eureka_snapshot_path: str | Path = "K4_MYSZKOWSKI_BREAKTHROUGH.md",
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """P8 — Myszkowski transposition sweep against K4.

    Tries each candidate keyword in both directions (``decrypt`` — the
    natural attack direction, assuming K4 is the Myszkowski-encrypted
    ciphertext — and ``encrypt``, kept only in case of a read/write
    convention ambiguity). Every candidate crossing the eureka threshold is
    run through :func:`kryptos.k4.validation.validate_candidate`; only a
    ``promote``-passing candidate (all 4 cribs + independent reproduction)
    raises :class:`~kryptos.k4.eureka.EurekaSignal`. A null-result artifact
    is always written.
    """
    if candidate_keywords is None:
        candidate_keywords = CANDIDATE_KEYWORDS

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _reproduce(key_info: dict[str, Any], _ct: str = ct) -> str:
        fn = myszkowski_decrypt if key_info["direction"] == "decrypt" else myszkowski_encrypt
        return fn(_ct, key_info["keyword"])

    for keyword in candidate_keywords:
        for direction in ("decrypt", "encrypt"):
            fn = myszkowski_decrypt if direction == "decrypt" else myszkowski_encrypt
            candidate = fn(ct, keyword)
            total_tested += 1

            pos_hits = positional_crib_hits(candidate)
            kw_hits = _keyword_hits(candidate)

            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "myszkowski",
                    "keyword": keyword,
                    "direction": direction,
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
                        "direction": direction,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "P8_myszkowski",
        "timestamp": ts_start,
        "run_params": {
            "candidate_keywords": candidate_keywords,
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
    "CANDIDATE_KEYWORDS",
    "keyword_to_myszkowski_groups",
    "myszkowski_encrypt",
    "myszkowski_decrypt",
    "run_myszkowski_attack",
]
