"""Multi-layer constraint-chain evaluator for K4 candidates.

Every scoring function elsewhere in this project measures one thing at a
time: `validation.crib_match_level` counts confirmed cribs,
`scoring_instructional.combined_instructional_score` measures English-ness,
`quagmire_sweep._keyword_hits` counts Sanborn-hint substrings. A candidate
that scores well on exactly one of those axes is still just a hypothesis --
the ones worth real attention are the ones that satisfy *several
independent* layers at once, since each layer is a different, unrelated
way to be wrong by chance.

This module doesn't replace any of those scorers or introduce a new
promotion gate -- `validation.validate_candidate`'s strict promote gate
(all 4 confirmed cribs + independent reproduction) remains the only thing
that raises a candidate's status. This is a *reporting* layer: given a
candidate, show how many independent evidence layers it satisfies and
which ones, so a genuinely multi-layer hit is visible instead of buried at
the same rank as a candidate that only got lucky on one axis.
"""

from __future__ import annotations

from typing import Any

from . import physical_geometry
from .alt_keywords import P11_KEYWORDS
from .quagmire_sweep import _EUREKA_WORDS, positional_crib_hits
from .scoring_instructional import combined_instructional_score

LAYER_NAMES = (
    "confirmed_cribs",
    "sanborn_hint_keywords",
    "reconstructed_plaintext_alignment",
    "language_score",
    "physical_geometry",
)


def _crib_layer(candidate_text: str) -> dict[str, Any]:
    hits = positional_crib_hits(candidate_text)
    return {"satisfied": hits >= 4, "detail": f"{hits}/4 confirmed cribs at their exact positions"}


def _keyword_layer(candidate_text: str) -> dict[str, Any]:
    """Sanborn-hint keyword evidence, independent of the confirmed-crib layer.

    Excludes the four confirmed crib words (EAST/NORTHEAST/BERLIN/CLOCK):
    the crib layer already covers them, and NORTHEAST/BERLIN/CLOCK are also
    literally in `P11_KEYWORDS`, so without this exclusion any candidate
    that satisfies the crib layer would trivially satisfy this one too --
    not actually independent evidence, defeating the point of a multi-layer
    evaluator (found via CodeRabbit review on PR #203, verified against
    current code before fixing).
    """
    upper = candidate_text.upper()
    independent_hints = [w for w in P11_KEYWORDS if w not in _EUREKA_WORDS]
    hint_hits = [w for w in independent_hints if w in upper]
    satisfied = len(hint_hits) >= 3
    return {
        "satisfied": satisfied,
        "detail": f"independent hint keywords present (excludes confirmed cribs): {hint_hits}",
    }


def _reconstruction_alignment_layer(candidate_text: str, candidate_name: str) -> dict[str, Any]:
    """How much the candidate agrees with solvekryptos.com's reconstruction, position by position.

    This is deliberately a *soft* layer, never conflated with the hard
    confirmed-crib layer above -- the reconstruction's own 73 non-anchor
    characters are independently unverified (see `plaintext_evidence.py`).
    Agreement here is corroborating at best, never gating.
    """
    from .plaintext_evidence import reconstructed_plaintext

    recon = reconstructed_plaintext(candidate_name)
    if recon is None or len(candidate_text) != len(recon):
        return {"satisfied": False, "detail": "reconstruction unavailable or length mismatch"}
    matches = sum(1 for a, b in zip(candidate_text.upper(), recon, strict=True) if a == b)
    pct = round(100 * matches / len(recon), 1)
    return {
        "satisfied": pct >= 50.0,
        "detail": f"{matches}/{len(recon)} positions ({pct}%) agree with the reconstruction",
    }


def _language_layer(candidate_text: str) -> dict[str, Any]:
    """Is this candidate's language score clearly better than raw K4 ciphertext's own?

    `combined_instructional_score`'s scale is negative-shifted at this
    text length (a 97-char sample scores well below zero even for real
    English), so an absolute ">0" threshold would silently mark every
    real candidate unsatisfied. Comparing against the untouched
    ciphertext's own score is a self-calibrating baseline instead of a
    guessed constant.
    """
    from .physical_grid import K4

    score = combined_instructional_score(candidate_text, gate_entropy=False)
    baseline = combined_instructional_score(K4, gate_entropy=False)
    return {
        "satisfied": score > baseline,
        "detail": f"instructional score {score:.2f} (raw-ciphertext baseline: {baseline:.2f})",
    }


def _geometry_layer(key_info: dict[str, Any] | None) -> dict[str, Any]:
    """Does this candidate's key_info use a rotation/bearing that matches a real, sourced measurement?

    Currently always inapplicable -- see `physical_geometry.py`: the only
    confirmed physical fact (tableau reading direction) isn't a numeric
    parameter a candidate's key_info would carry, and the compass bearing
    this layer would actually gate on remains unmeasured (Phase 8). This
    stays wired up and ready rather than omitted, so the day a bearing is
    sourced this layer starts contributing without further code changes.
    """
    bearing = physical_geometry.CURRENT.compass_rose.true_bearing
    if not bearing.is_known or key_info is None:
        return {"satisfied": False, "detail": "not yet applicable -- no measured compass bearing sourced (Phase 8)"}
    candidate_bearing = key_info.get("rotation_offset")
    if candidate_bearing is None:
        candidate_bearing = key_info.get("bearing")
    satisfied = (
        candidate_bearing is not None and bearing.value is not None and abs(candidate_bearing - bearing.value) < 1.0
    )
    return {"satisfied": satisfied, "detail": f"candidate bearing {candidate_bearing} vs. measured {bearing}"}


def evaluate_candidate(
    candidate_text: str,
    key_info: dict[str, Any] | None = None,
    candidate_name: str = "solvekryptos_field_guide",
) -> dict[str, Any]:
    """Score a candidate against every independent evidence layer this project has.

    Returns each layer's verdict plus a count of how many were satisfied.
    Does not gate or promote anything -- see module docstring.
    """
    layers = {
        "confirmed_cribs": _crib_layer(candidate_text),
        "sanborn_hint_keywords": _keyword_layer(candidate_text),
        "reconstructed_plaintext_alignment": _reconstruction_alignment_layer(candidate_text, candidate_name),
        "language_score": _language_layer(candidate_text),
        "physical_geometry": _geometry_layer(key_info),
    }
    satisfied_count = sum(1 for layer in layers.values() if layer["satisfied"])
    return {
        "candidate_text": candidate_text,
        "layers": layers,
        "layers_satisfied": satisfied_count,
        "layers_total": len(layers),
    }


__all__ = ["LAYER_NAMES", "evaluate_candidate"]
