"""Strict independent-validation pipeline + external-candidate adversarial benchmarks.

Implements the research brief's Prediction Standard (levels 1-6) and
complexity/overfitting guard as callable checks, and holds an adversarial
benchmark registry of external K4 claims — checked independently, never
accepted on say-so. "Passing" a benchmark here means "survives a strict,
independent positional check"; it is not an endorsement of the source's
methodology.

Two external sources (supplied by the user, both checked by hand as part of
scoping this module — see ``EXTERNAL_CANDIDATES`` and the module-level notes
below):

  * solvekryptos.com/fieldguide claims a full K4 plaintext via an
    undisclosed Quagmire-III-variant mechanism (its f-table/g-table values
    are not published, so its *mechanism* is not independently
    reproducible here — only its *claimed plaintext* is checkable against
    the confirmed crib positions).
  * kryptosbot.com/findings proposes no candidate plaintext at all (it
    reports 13,302 audited candidates, zero surviving verification); it is
    used only as a corroborating negative-result cross-reference and as the
    source of two structural diagnostics (``check_w_delimiter_pattern``,
    ``check_stehle_anomaly``) worth having on hand for future candidates.
    Neither diagnostic asserts a theory is true — they compute an observable
    property of a given ciphertext/candidate and report it.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .keystream_validator import K4_CRIBS
from .physical_grid import K4
from .quagmire_sweep import positional_crib_hits

# ---------------------------------------------------------------------------
# Prediction Standard (brief section 13) + complexity guard (section 14)
# ---------------------------------------------------------------------------


def crib_match_level(candidate: str) -> int:
    """Level 1/2 check: count of confirmed cribs matched at their exact positions (0-4)."""
    return positional_crib_hits(candidate)


def complexity_score(param_count: int, exceptions: int = 0) -> float:
    """Penalty term: more free parameters/special-cases -> lower (more negative) score.

    Exceptions (hardcoded special cases, manually-selected values) are
    weighted twice as heavily as ordinary parameters, per the brief's own
    example contrasting a 3-parameter mechanism against a 17-rotation,
    3-exception one.
    """
    return -(param_count + 2 * exceptions)


CRIB_HIT_WEIGHT = 50


def overfitting_guard(crib_hits: int, param_count: int, exceptions: int = 0) -> float:
    """Combine crib match strength with a complexity penalty into one rankable score.

    Each crib hit is worth 50 points — an exact multi-letter word match at an
    exact position is a strong, low-probability-by-chance signal, so it
    should outweigh plausible complexity penalties (a handful of parameters
    or exceptions); complexity mainly breaks ties between candidates at the
    same crib-match level, as in the brief's own example (a 3-parameter
    mechanism vs. a 17-rotation/3-exception one, both matching all 4 cribs).
    """
    return crib_hits * CRIB_HIT_WEIGHT + complexity_score(param_count, exceptions)


def independent_reproduction_check(
    key_info: dict[str, Any],
    reproduce_fn: Callable[[dict[str, Any]], str],
    expected_text: str,
) -> bool:
    """Level 6 check: re-derive a candidate from its key_info via a fresh call.

    Guards against a result that only "looks right" because of a caching or
    state bug in the sweep that produced it — nothing is promoted to a
    breakthrough snapshot without passing this.
    """
    return reproduce_fn(key_info) == expected_text


def validate_candidate(
    candidate_text: str,
    key_info: dict[str, Any],
    reproduce_fn: Callable[[dict[str, Any]], str],
    param_count: int,
    exceptions: int = 0,
) -> dict[str, Any]:
    """Full gate: crib match + overfitting score + independent reproduction.

    Returns a dict with ``promote`` (bool) — only True if the candidate
    matches all 4 confirmed cribs *and* independently reproduces from its
    own key_info.
    """
    hits = crib_match_level(candidate_text)
    reproduced = independent_reproduction_check(key_info, reproduce_fn, candidate_text)
    return {
        "crib_hits": hits,
        "score": overfitting_guard(hits, param_count, exceptions),
        "reproduced": reproduced,
        "promote": hits >= len(K4_CRIBS) and reproduced,
    }


# ---------------------------------------------------------------------------
# External candidate models as adversarial benchmarks
# ---------------------------------------------------------------------------

EXTERNAL_CANDIDATES: dict[str, dict[str, Any]] = {
    "solvekryptos_field_guide": {
        "source": "https://solvekryptos.com/fieldguide",
        "claimed_plaintext_raw": (
            "THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X "
            "COMMISSION BERLIN CLOCK WHICH IS NORTHEAST OF HERE X"
        ),
        "claimed_mechanism": (
            "Quagmire-III variant: physical tableau keystream, a fixed row-identity "
            "f-table, four pass-specific g-tables, and a one-bit positional gate. "
            "f-table/g-table values are not published, so the mechanism itself is not "
            "independently reproducible from public information; only the claimed "
            "plaintext's positional alignment is checkable here."
        ),
        "mechanism_reproducible": False,
    },
}


def _normalize_keep_x(text: str) -> str:
    """Uppercase, alpha-only normalization that keeps literal 'X' word-separators.

    The Field Guide's claimed plaintext only reaches K4's exact length (97)
    if its 'X' separators are counted as real characters rather than
    stripped as delimiters — stripping them breaks the length match and,
    with it, every downstream positional check. Keeping them is what makes
    the comparison well-posed at all.
    """
    return "".join(c for c in text.upper() if c.isalpha())


def benchmark_external_candidate(name: str) -> dict[str, Any]:
    """Independently check a registered external candidate against K4_CRIBS.

    Does not trust the source's own claim of correctness — recomputes crib
    alignment from scratch, including *where* each crib word actually falls
    in the claimed text (not just whether it's present somewhere), so a
    near-miss (off-by-N) is visible rather than silently failing.
    """
    entry = EXTERNAL_CANDIDATES[name]
    normalized = _normalize_keep_x(entry["claimed_plaintext_raw"])

    per_crib: dict[str, dict[str, Any]] = {}
    for label, (word, expected_pos) in K4_CRIBS.items():
        actual_slice = normalized[expected_pos : expected_pos + len(word)]
        exact_match = actual_slice == word
        found_at = normalized.find(word)
        per_crib[label] = {
            "expected_pos": expected_pos,
            "exact_match": exact_match,
            "found_at": found_at if found_at != -1 else None,
            "offset_from_expected": (found_at - expected_pos) if found_at != -1 else None,
        }

    exact_hits = sum(1 for info in per_crib.values() if info["exact_match"])
    return {
        "name": name,
        "source": entry["source"],
        "claimed_mechanism": entry["claimed_mechanism"],
        "mechanism_reproducible": entry["mechanism_reproducible"],
        "normalized_plaintext": normalized,
        "normalized_length": len(normalized),
        "k4_length": len(K4),
        "per_crib": per_crib,
        "exact_positional_hits": exact_hits,
        "verdict": "passes_strict_validation" if exact_hits >= len(K4_CRIBS) else "fails_strict_validation",
    }


def check_w_delimiter_pattern(text: str = K4) -> dict[str, Any]:
    """Diagnostic: positions of every 'W' in ``text``.

    kryptosbot.com/findings names a "W-delimiter pattern" of five W
    characters at specific positions as a live, unresolved anomaly, without
    publishing the exact indices in the source material fetched here. This
    function computes W-positions directly and reports them as a reusable
    diagnostic; it does not assert they constitute a delimiter pattern.
    """
    positions = [i for i, c in enumerate(text) if c == "W"]
    return {"text_length": len(text), "w_positions": positions, "w_count": len(positions)}


def check_stehle_anomaly(text: str = K4, start: int = 55, end: int = 63) -> dict[str, Any]:
    """Diagnostic: adjacent-letter shift structure in a ciphertext window.

    kryptosbot.com/findings names a "Stehle anomaly (a constant-difference
    pattern at positions 55-63)" without publishing its exact definition in
    the source material fetched here. This computes the most literal reading
    — mod-26 differences between consecutive letters in ``text[start:end]``
    — and reports both whether that sequence is constant and whether it is
    periodic (a weaker, still-notable structural property). This is a
    best-effort reconstruction from a paraphrased description, not a
    verified reproduction of kryptosbot's own methodology.
    """
    window = text[start:end]
    diffs = [(ord(window[i + 1]) - ord(window[i])) % 26 for i in range(len(window) - 1)]
    is_constant = len(set(diffs)) == 1
    period: int | None = None
    for candidate_period in range(1, len(diffs)):
        if all(diffs[i] == diffs[i - candidate_period] for i in range(candidate_period, len(diffs))):
            period = candidate_period
            break
    return {
        "window": window,
        "window_span": (start, end),
        "letter_diffs_mod26": diffs,
        "is_constant_difference": is_constant,
        "shortest_period": period,
    }


__all__ = [
    "CRIB_HIT_WEIGHT",
    "EXTERNAL_CANDIDATES",
    "benchmark_external_candidate",
    "check_stehle_anomaly",
    "check_w_delimiter_pattern",
    "complexity_score",
    "crib_match_level",
    "independent_reproduction_check",
    "overfitting_guard",
    "validate_candidate",
]
