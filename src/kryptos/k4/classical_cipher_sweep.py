"""P21 -- real, crib-gated sweeps for hypotheses.py's orphaned classical-cipher classes.

`hypotheses.py` implements `PlayfairHypothesis`, `FourSquareHypothesis`,
`BifidHypothesis` (the classic 5x5 grid form, distinct from `trifid.py`'s
own 3x3x3 cube extension of it), and `AutokeyHypothesis` -- four cipher
families structurally distinct from anything else this project has ever
run against K4 (Playfair/Four-Square are digraph-substitution ciphers;
classic Bifid is a 5x5 fractionation cipher, not the 27-cell Trifid this
project already tested; Autokey chains the key off the plaintext itself,
unlike the fixed repeating-key Vigenère already exhausted elsewhere).

They were fully implemented and unit-tested (`tests/functional/
test_k4_hypotheses.py`), but that coverage only checks the code runs
without crashing on a truncated ~74-character ciphertext fragment with a
handful of keywords -- never the real 97-character K4, never scored
against this project's own canonical crib-gating (`positional_crib_hits`),
and never logged anywhere in the research docs. Nothing outside
`hypotheses.py` and its own tests references these classes; found while
auditing whether "everything's been implemented" was actually true.

This module closes that gap: runs all four against the real K4 ciphertext
with an expanded keyword list (the union of every keyword this project has
ever tested elsewhere -- P11, advisory names, the reconstructed
plaintext's own vocabulary, the K0 Morse-slab words, plus the K1-K3 key
chain), scored by `positional_crib_hits` rather than each class's own
internal `combined_plaintext_score` (a general English-likeness heuristic
this project doesn't treat as a promotion signal anywhere else).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .advisory_keywords import ADVISORY_KEYWORDS
from .alt_keywords import P11_KEYWORDS
from .eureka import EurekaSignal, write_breakthrough_snapshot
from .hypotheses import AutokeyHypothesis, BifidHypothesis, Candidate, FourSquareHypothesis, PlayfairHypothesis
from .k0_morse_keywords import K0_MORSE_KEYWORDS
from .physical_grid import K4
from .plaintext_evidence import RECONSTRUCTED_PLAINTEXT_KEYWORDS
from .quagmire_sweep import _keyword_hits, positional_crib_hits
from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

# Union of every keyword this project has tested as a substitution seed
# anywhere, minus "STANDARD" (a KNOWN_KEYED_ALPHABETS label for the
# identity alphabet, not an actual candidate word).
ALL_TESTED_KEYWORDS: list[str] = sorted(
    (set(P11_KEYWORDS) | set(ADVISORY_KEYWORDS) | set(RECONSTRUCTED_PLAINTEXT_KEYWORDS) | set(K0_MORSE_KEYWORDS))
    | (set(KNOWN_KEYED_ALPHABETS.keys()) - {"STANDARD"})
)

BIFID_PERIODS: list[int] = list(range(3, 21))

_NULL_ARTIFACT_PATH = "K4_CLASSICAL_CIPHER_NULL.json"


def _evaluate_candidates(
    candidates: list[Candidate],
    source: str,
    ts_start: str,
    eureka_snapshot_path: str | Path,
    positional_eureka_threshold: int,
    keyword_eureka_threshold: int,
) -> tuple[list[dict[str, Any]], int]:
    """Score every candidate by this project's own canonical crib-gating, not the class's own heuristic score.

    Raises EurekaSignal on a real breakthrough. Returns (best_candidates,
    total_tested).
    """
    best: list[dict[str, Any]] = []
    for c in candidates:
        pos_hits = positional_crib_hits(c.plaintext)
        kw_hits = _keyword_hits(c.plaintext)

        if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
            key_info = {"attack": source, "hypothesis_id": c.id, **c.key_info}
            snap = write_breakthrough_snapshot(
                c.plaintext,
                key_info,
                extra={"positional_crib_hits": pos_hits, "keyword_hits": kw_hits, "sweep_ts": ts_start},
                path=eureka_snapshot_path,
            )
            raise EurekaSignal(
                snapshot_path=snap,
                result={
                    "candidate_text": c.plaintext,
                    "key_info": key_info,
                    "snapshot_path": snap,
                    "positional_crib_hits": pos_hits,
                    "keyword_hits": kw_hits,
                },
            )

        if pos_hits > 0 or kw_hits > 0:
            best.append(
                {
                    "candidate_text": c.plaintext,
                    "hypothesis_id": c.id,
                    "positional_crib_hits": pos_hits,
                    "keyword_hits": kw_hits,
                    "key_info": c.key_info,
                }
            )
    return best, len(candidates)


def run_classical_cipher_sweep(
    ciphertext: str = K4,
    keywords: list[str] | None = None,
    bifid_periods: list[int] | None = None,
    eureka_snapshot_path: str | Path = "K4_CLASSICAL_CIPHER_BREAKTHROUGH.md",
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Run Playfair, Four-Square, classic Bifid, and Autokey against real K4 with real crib gating.

    Returns a summary dict (status, run_params, best_candidates) and writes
    it to ``null_artifact_path``. Raises EurekaSignal on a crib breakthrough.
    """
    keywords = keywords if keywords is not None else ALL_TESTED_KEYWORDS
    bifid_periods = bifid_periods if bifid_periods is not None else BIFID_PERIODS
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    all_best: list[dict[str, Any]] = []

    def _run_one(hyp: Any, source: str, limit: int) -> None:
        nonlocal total_tested
        candidates = hyp.generate_candidates(ciphertext, limit=limit)
        best, tested = _evaluate_candidates(
            candidates, source, ts_start, eureka_snapshot_path, positional_eureka_threshold, keyword_eureka_threshold
        )
        total_tested += tested
        all_best.extend(best)

    # Playfair and Four-Square: every keyword returned, not truncated by
    # the class's own internal score-based top-N.
    _run_one(PlayfairHypothesis(keywords=keywords), "classical_playfair", limit=len(keywords))
    _run_one(
        FourSquareHypothesis(keywords=keywords),
        "classical_foursquare",
        limit=len(keywords) * (len(keywords) + 1) // 2,
    )

    # Autokey: same expanded keyword list as primers.
    _run_one(AutokeyHypothesis(primers=keywords), "classical_autokey", limit=len(keywords))

    # Bifid: one keyword at a time (the class only accepts a single
    # keyword + a period list), so instantiate once per keyword.
    for kw in keywords:
        _run_one(BifidHypothesis(keyword=kw, periods=bifid_periods), "classical_bifid", limit=len(bifid_periods))

    all_best.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "P21_classical_cipher_sweep",
        "timestamp": ts_start,
        "run_params": {
            "keywords": keywords,
            "bifid_periods": bifid_periods,
            "total_tested": total_tested,
            "positional_eureka_threshold": positional_eureka_threshold,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": all_best[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


__all__ = [
    "ALL_TESTED_KEYWORDS",
    "BIFID_PERIODS",
    "run_classical_cipher_sweep",
]
