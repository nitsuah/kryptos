"""K4 plaintext evidence, confidence-tiered.

The project's own mental model needs to distinguish two genuinely different
things that are easy to conflate (see docs/analysis/K4_ACTIVE_RESEARCH.md's
"External Developments" section for the full sourcing):

1. **Sanborn's actual archival plaintext**, recovered by researchers Kobek
   and Byrne from his working papers at the Smithsonian (September 2025).
   This is real and authenticated by Sanborn himself -- but it has never
   been publicly released. This repo does not have it and cannot claim to.
2. **solvekryptos.com/fieldguide's public reconstruction** of what that
   plaintext probably says. This is a *third party's own back-solved
   guess*, not item 1 -- it is independently checkable only at the 24
   positions Sanborn has separately, publicly confirmed as crib words
   (EAST, NORTHEAST, BERLIN, CLOCK). It matches those exactly (see
   `kryptos.k4.validation.benchmark_external_candidate`), which is real,
   positive evidence for it -- but the other 73 characters carry no
   independent confirmation and are not the same evidentiary class as
   item 1, let alone the 24 Sanborn-confirmed characters.

Conflating these (treating the full reconstruction as if it were
Sanborn's authenticated text) is exactly the "circular confirmation
loop" this project's own strict-validation discipline exists to avoid.
This module keeps them apart explicitly rather than silently upgrading
one into the other.
"""

from __future__ import annotations

from typing import Any

from .keystream_validator import K4_CRIBS
from .physical_grid import K4
from .validation import EXTERNAL_CANDIDATES, _normalize_keep_x

STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CONFIRMED = "confirmed"  # Sanborn's own public clue, exact position, high confidence
RECONSTRUCTED = "reconstructed"  # solvekryptos.com's back-solved guess -- not Sanborn's text
UNKNOWN = "unknown"  # no data at this position


def confirmed_plaintext() -> dict[int, str]:
    """0-indexed position -> plaintext letter, for the 24 Sanborn-confirmed characters only.

    Derived from `keystream_validator.K4_CRIBS` -- the single canonical
    crib-position source this whole project already uses -- rather than a
    second hardcoded copy.
    """
    result: dict[int, str] = {}
    for word, start in K4_CRIBS.values():
        for i, ch in enumerate(word):
            result[start + i] = ch
    return result


def reconstructed_plaintext(candidate_name: str = "solvekryptos_field_guide") -> str | None:
    """The named external candidate's full 97-char reconstruction, normalized.

    Returns None if the candidate isn't registered. This is explicitly
    *not* Sanborn's authenticated archival plaintext -- see module
    docstring.
    """
    entry = EXTERNAL_CANDIDATES.get(candidate_name)
    if entry is None:
        return None
    normalized = _normalize_keep_x(entry["claimed_plaintext_raw"])
    return normalized if len(normalized) == len(K4) else None


def evidence_map(candidate_name: str = "solvekryptos_field_guide") -> dict[int, dict[str, Any]]:
    """Full 97-position evidence map, each position tagged with its confidence level.

    - CONFIRMED: Sanborn's own public clue (24 positions).
    - RECONSTRUCTED: a third party's back-solved guess -- agrees with the
      confirmed anchors, independently unverified everywhere else.
    - UNKNOWN: no data.
    """
    confirmed = confirmed_plaintext()
    recon = reconstructed_plaintext(candidate_name)
    result: dict[int, dict[str, Any]] = {}
    for pos in range(len(K4)):
        if pos in confirmed:
            result[pos] = {
                "char": confirmed[pos],
                "confidence": CONFIRMED,
                "source": "Sanborn public clue (artist-confirmed)",
            }
        elif recon is not None:
            result[pos] = {
                "char": recon[pos],
                "confidence": RECONSTRUCTED,
                "source": f"{candidate_name} (third-party reconstruction, unverified at this position)",
            }
        else:
            result[pos] = {"char": None, "confidence": UNKNOWN, "source": None}
    return result


def confidence_counts(candidate_name: str = "solvekryptos_field_guide") -> dict[str, int]:
    """Tally of positions per confidence level -- a quick sanity check on the map above."""
    counts = {CONFIRMED: 0, RECONSTRUCTED: 0, UNKNOWN: 0}
    for entry in evidence_map(candidate_name).values():
        counts[entry["confidence"]] += 1
    return counts


def derived_shifts(
    candidate_name: str = "solvekryptos_field_guide",
    alphabet: str = STANDARD_ALPHABET,
) -> dict[str, Any]:
    """Vigenère-equivalent shift at every position, split by confidence level.

    Exploratory only. The CONFIRMED-position shifts are exactly
    `keystream_validator.K4_EXPECTED_KEYSTREAMS` restated per-position; the
    RECONSTRUCTED-position shifts rest on the unverified 73 characters and
    must never be used to gate or promote a candidate the way the confirmed
    cribs do -- that would be exactly the circular-confirmation trap this
    project's validation discipline exists to avoid. Their only legitimate
    use is generating hypotheses to test independently (e.g. period
    detection below), never as ground truth.
    """
    evidence = evidence_map(candidate_name)
    n = len(alphabet)
    confirmed_shifts: dict[int, int] = {}
    reconstructed_shifts: dict[int, int] = {}
    for pos, entry in evidence.items():
        p_char = entry["char"]
        if p_char is None or p_char not in alphabet:
            continue
        c_char = K4[pos]
        if c_char not in alphabet:
            continue
        shift = (alphabet.index(c_char) - alphabet.index(p_char)) % n
        if entry["confidence"] == CONFIRMED:
            confirmed_shifts[pos] = shift
        elif entry["confidence"] == RECONSTRUCTED:
            reconstructed_shifts[pos] = shift
    return {
        "confirmed_shifts": confirmed_shifts,
        "reconstructed_shifts": reconstructed_shifts,
        "candidate_name": candidate_name,
    }


def candidate_repeating_periods(
    candidate_name: str = "solvekryptos_field_guide",
    period_range: range = range(2, 21),
) -> dict[int, bool]:
    """For each candidate period L, is the RECONSTRUCTED-derived shift sequence

    consistent with a repeating key of length L (same shift at every
    position congruent mod L)? Exploratory diagnostic only -- see
    `derived_shifts`'s docstring on why this cannot be used to promote a
    candidate. A period passing here is a hypothesis to test against real
    K4 independently (e.g. via `key_csp.solve_key_csp`), not a result.
    """
    shifts = derived_shifts(candidate_name)["reconstructed_shifts"]
    if not shifts:
        return {}
    result: dict[int, bool] = {}
    for period in period_range:
        by_slot: dict[int, set[int]] = {}
        for pos, shift in shifts.items():
            slot = pos % period
            by_slot.setdefault(slot, set()).add(shift)
        result[period] = all(len(vals) == 1 for vals in by_slot.values())
    return result


# Words from the reconstructed plaintext not already covered by this
# project's existing keyword sweeps (P11's SANBORN/LANGLEY/SCHEIDT/WENDELL/
# NORTHEAST/BERLIN/CLOCK/SHADOW/BETWEEN/COMPASS/DIGETAL -- EAST, NORTHEAST,
# BERLIN, CLOCK, COMPASS already tested there; excluded here). If the
# reconstruction is right, these are the sculpture's own words, not a
# guess -- a natural, well-motivated keyword source that hasn't existed
# until now. THE/IS/HERE/THIS/YOUR/OF are excluded as function words too
# short/common to be a meaningful keyed-alphabet seed.
RECONSTRUCTED_PLAINTEXT_KEYWORDS: list[str] = [
    "ROSE",
    "POSITION",
    "COMMISSION",
    "WHICH",
]


def reconstructed_plaintext_keyed_alphabets() -> dict[str, str]:
    """Keyed alphabets built from `RECONSTRUCTED_PLAINTEXT_KEYWORDS`, same convention as advisory_keywords.py."""
    from .advisory_keywords import build_keyed_alphabet

    return {kw: build_keyed_alphabet(kw) for kw in RECONSTRUCTED_PLAINTEXT_KEYWORDS}


def run_reconstructed_plaintext_keyword_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str = "K4_RECONSTRUCTED_KEYWORD_NULL.json",
) -> dict[str, Any]:
    """Run the 3-layer composite with reconstructed-plaintext-derived keyed alphabets.

    Mirrors `advisory_keywords.run_advisory_keyword_sweep` and
    `world_clock_cities.run_world_clock_city_sweep` exactly -- same
    composite pipeline, only the keyword source differs.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds
    return run_three_layer_composite(
        subst_alphabets=reconstructed_plaintext_keyed_alphabets(),
        grid_sizes=grid_sizes or [7, 8, 10],
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        progress_cb=progress_cb,
        null_artifact_path=null_artifact_path,
        eureka_snapshot_path="K4_RECONSTRUCTED_KEYWORD_EUREKA.md",
    )


__all__ = [
    "CONFIRMED",
    "RECONSTRUCTED",
    "UNKNOWN",
    "RECONSTRUCTED_PLAINTEXT_KEYWORDS",
    "confirmed_plaintext",
    "reconstructed_plaintext",
    "reconstructed_plaintext_keyed_alphabets",
    "run_reconstructed_plaintext_keyword_sweep",
    "evidence_map",
    "confidence_counts",
    "derived_shifts",
    "candidate_repeating_periods",
]
