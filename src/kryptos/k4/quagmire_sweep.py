"""Systematic Quagmire I-IV sweep against K4.

The leading K4 hypothesis is a product cipher whose substitution layer is a
Quagmire III (the same KRYPTOS-keyed tableau Sanborn used for K1/K2). This
sweep tests all four Quagmire variants against K4 directly with:

- word indicator keys (KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, CLOCK, ...)
- Berlin Clock derived indicator keys (one per minute-of-day state, mapping
  the lamp-row values [5h, 1h, 5m, 1m, sec] to tableau letters)
- both indicator-base conventions (Kryptos first-letter and ACA ``A``)

Candidates are gated on the four confirmed positional cribs (EAST@22,
NORTHEAST@26, BERLIN@63, CLOCK@69). A null-result artifact is always written
so the run is fully provenance-tracked; >=3 positional cribs or >=4 keywords
anywhere raises EurekaSignal with a breakthrough snapshot.
"""

from __future__ import annotations

import json
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any, Callable

from .berlin_clock import berlin_clock_shifts
from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .keystream_validator import K4_CRIBS
from .quagmire import keyword_alphabet, quagmire1_decrypt, quagmire2_decrypt, quagmire3_decrypt, quagmire4_decrypt

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

WORD_KEYS = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "BERLIN",
    "CLOCK",
    "BERLINCLOCK",
    "NORTHEAST",
    "EAST",
    "SANBORN",
    "LANGLEY",
]

ALPHABET_KEYWORDS = ["KRYPTOS", "BERLIN", "CLOCK", "BERLINCLOCK"]

_EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


def positional_crib_hits(candidate: str) -> int:
    """Count confirmed K4 cribs matched at their exact positions."""
    hits = 0
    for word, start in K4_CRIBS.values():
        if candidate[start : start + len(word)] == word:  # noqa: E203
            hits += 1
    return hits


def clock_indicator_keys(alphabet: str, include_seconds: bool = False) -> dict[str, str]:
    """Berlin Clock indicator keys: one per minute-of-day state.

    Maps each lamp-row count [5h, 1h, 5m, 1m(, sec)] to the letter at that
    index in ``alphabet``, giving a 4- or 5-letter periodic indicator key.

    Returns:
        Dict of "HH:MM" -> key string (deduplicated by key downstream).
    """
    keys: dict[str, str] = {}
    for hour in range(24):
        for minute in range(60):
            shifts = berlin_clock_shifts(time(hour, minute, 0))
            values = shifts if include_seconds else shifts[:4]
            keys[f"{hour:02d}:{minute:02d}"] = "".join(alphabet[v] for v in values)
    return keys


def _variant_decryptors() -> dict[str, Callable[[str, str, str, str | None], str]]:
    return {
        "quagmire1": quagmire1_decrypt,
        "quagmire2": quagmire2_decrypt,
        "quagmire3": quagmire3_decrypt,
    }


def run_quagmire_sweep(
    ciphertext: str = K4,
    word_keys: list[str] | None = None,
    alphabet_keywords: list[str] | None = None,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_QUAGMIRE_NULL.json",
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Sweep Quagmire I-IV against K4 with word and Berlin Clock indicator keys.

    Returns a summary dict (status, run_params, best_candidates) and writes it
    to ``null_artifact_path``. Raises EurekaSignal on a crib breakthrough.
    """
    if word_keys is None:
        word_keys = WORD_KEYS
    if alphabet_keywords is None:
        alphabet_keywords = ALPHABET_KEYWORDS

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _evaluate(candidate: str, info: dict[str, Any]) -> None:
        nonlocal total_tested
        total_tested += 1
        pos_hits = positional_crib_hits(candidate)
        kw_hits = _keyword_hits(candidate)

        if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
            key_info = {"attack": "quagmire_sweep", **info}
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
                    **info,
                }
            )

    bases: list[str | None] = [None, "A"]  # Kryptos first-letter and ACA conventions

    # --- Quagmire I-III: word keys x alphabet keywords x indicator bases ---
    for variant, decryptor in _variant_decryptors().items():
        for alpha_kw in alphabet_keywords:
            for key in word_keys:
                for base in bases:
                    candidate = decryptor(ct, key, alpha_kw, base)
                    _evaluate(
                        candidate,
                        {"variant": variant, "key": key, "alphabet_keyword": alpha_kw, "indicator_base": base},
                    )

    # --- Quagmire IV: ordered pairs of distinct alphabet keywords ---
    for pt_kw in alphabet_keywords:
        for ct_kw in alphabet_keywords:
            if pt_kw == ct_kw:
                continue
            for key in word_keys:
                for base in bases:
                    candidate = quagmire4_decrypt(ct, key, pt_kw, ct_kw, base)
                    _evaluate(
                        candidate,
                        {
                            "variant": "quagmire4",
                            "key": key,
                            "pt_keyword": pt_kw,
                            "ct_keyword": ct_kw,
                            "indicator_base": base,
                        },
                    )

    # --- Quagmire III with Berlin Clock indicator keys (KRYPTOS tableau) ---
    clock_alphabet = keyword_alphabet("KRYPTOS")
    for include_seconds in (False, True):
        seen_keys: set[str] = set()
        for clock_time, key in clock_indicator_keys(clock_alphabet, include_seconds).items():
            if key in seen_keys:
                continue
            seen_keys.add(key)
            for base in bases:
                candidate = quagmire3_decrypt(ct, key, "KRYPTOS", base)
                _evaluate(
                    candidate,
                    {
                        "variant": "quagmire3_clock",
                        "key": key,
                        "clock_time": clock_time,
                        "include_seconds": include_seconds,
                        "alphabet_keyword": "KRYPTOS",
                        "indicator_base": base,
                    },
                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "quagmire_sweep",
        "timestamp": ts_start,
        "run_params": {
            "word_keys": word_keys,
            "alphabet_keywords": alphabet_keywords,
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
    "WORD_KEYS",
    "ALPHABET_KEYWORDS",
    "positional_crib_hits",
    "clock_indicator_keys",
    "run_quagmire_sweep",
]
