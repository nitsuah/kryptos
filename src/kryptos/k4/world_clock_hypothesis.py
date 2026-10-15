"""Deterministic diagnostic for the community six-segment World Clock hypothesis.

This is an executable record of one specified transformation, not a decryption claim:
map each K4 ciphertext letter through the inverse KRYPTOS keyed alphabet, then
treat resulting X symbols as delimiters. The fixed transformation and source are
kept explicit so backend, execution artifacts, tests, and the dashboard agree.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
EXPECTED_SEGMENT_LENGTHS = [20, 15, 11, 9, 15, 22]
HISTORICAL_CITY_COUNT = 80
EXPECTED_DELIMITER = "X"


def transform_through_keyed_alphabet(ciphertext: str = CIPHERTEXT) -> str:
    """Relabel each ciphertext letter by its index in the KRYPTOS keyed alphabet."""
    clean = "".join(ch for ch in ciphertext.upper() if ch.isalpha())
    if not clean:
        raise ValueError("ciphertext must contain at least one letter")
    return "".join(ALPHABET[KEYED_ALPHABET.index(ch)] for ch in clean)


def split_on_delimiter(stream: str, delimiter: str = EXPECTED_DELIMITER) -> list[str]:
    """Split a stream on a single A–Z delimiter, retaining empty edge segments."""
    if len(delimiter) != 1 or delimiter not in ALPHABET:
        raise ValueError("delimiter must be one uppercase A–Z letter")
    return stream.split(delimiter)


def shuffled_delimiter_control(
    stream: str,
    sample_size: int = 5000,
    seed: int = 20261015,
) -> dict[str, Any]:
    """Compare the fixed segment-length target against shuffled-character controls.

    Each permutation preserves the exact stream character multiset (including the
    delimiter count), while randomizing positions. This is a descriptive conditional
    control, not a p-value: the target signature was noticed after inspecting the
    stream, and the broader search over transformations/delimiters is unaccounted for.
    """
    if sample_size < 1:
        raise ValueError("sample_size must be at least 1")
    if not stream or any(ch not in ALPHABET for ch in stream):
        raise ValueError("stream must contain uppercase A-Z letters only")

    rng = random.Random(seed)
    characters = list(stream)
    hits = 0
    for _ in range(sample_size):
        shuffled = characters.copy()
        rng.shuffle(shuffled)
        lengths = [len(part) for part in "".join(shuffled).split(EXPECTED_DELIMITER)]
        if lengths == EXPECTED_SEGMENT_LENGTHS:
            hits += 1

    return {
        "method": "uniform random permutation of stream characters; exact character multiset preserved",
        "sample_size": sample_size,
        "seed": seed,
        "target_segment_lengths": EXPECTED_SEGMENT_LENGTHS,
        "exact_signature_hits": hits,
        "observed_hit_rate": hits / sample_size,
        "interpretation": (
            "Descriptive conditional control only, not a p-value or independent evidence. "
            "The target signature was observed after inspecting this stream, and selection "
            "across delimiters, alphabets, transformations, orientations, and other patterns "
            "is not accounted for."
        ),
    }


def analyze_world_clock_hypothesis(ciphertext: str = CIPHERTEXT) -> dict[str, Any]:
    """Return a deterministic, serializable report for the six-segment hypothesis."""
    stream = transform_through_keyed_alphabet(ciphertext)
    positions = [i for i, ch in enumerate(stream) if ch == EXPECTED_DELIMITER]
    segments = split_on_delimiter(stream)
    lengths = [len(segment) for segment in segments]
    mismatch = sum(lengths) - HISTORICAL_CITY_COUNT
    rotation_signatures = [
        [len(part) for part in (stream[offset:] + stream[:offset]).split(EXPECTED_DELIMITER)]
        for offset in range(len(stream))
    ]
    matching_rotations = [
        offset for offset, signature in enumerate(rotation_signatures)
        if signature == EXPECTED_SEGMENT_LENGTHS
    ]
    return {
        "hypothesis_id": "world_clock_keyed_relabel_x_delimiters_v1",
        "status": "diagnostic_only",
        "ciphertext_length": len("".join(ch for ch in ciphertext.upper() if ch.isalpha())),
        "keyed_alphabet": KEYED_ALPHABET,
        "transformation": "inverse keyed-alphabet index relabeling: keyed alphabet letter -> A-Z at same index",
        "delimiter": EXPECTED_DELIMITER,
        "delimiter_positions_zero_based": positions,
        "delimiter_count": len(positions),
        "transformed_stream": stream,
        "segments": [
            {"index": i, "text": segment, "length": len(segment)}
            for i, segment in enumerate(segments)
        ],
        "segment_lengths": lengths,
        "matches_recorded_segment_lengths": lengths == EXPECTED_SEGMENT_LENGTHS,
        "shuffled_control": shuffled_delimiter_control(stream),
        "rotation_control": {
            "tested_circular_offsets": len(stream),
            "offsets_matching_recorded_segment_lengths": matching_rotations,
            "unique_segment_length_signatures": len({tuple(signature) for signature in rotation_signatures}),
            "interpretation": (
                "Circular-alignment sensitivity check only. The target segment lengths were observed "
                "from this same stream, so this is not an independent significance test."
            ),
        },
        "historical_baseline": {
            "original_city_names": HISTORICAL_CITY_COUNT,
            "source": (
                "Official Urania World Clock history page; original display described as 80 city names "
                "across 24 time zones."
            ),
            "source_url": "https://www.weltzeituhr-berlin.de/en/urania-worldtimeclock",
            "segment_letters_total": sum(lengths),
            "difference_letters_minus_city_names": mismatch,
            "interpretation": (
                "The 92 non-delimiter letters do not map one-to-one to the documented 80 original city "
                "names without an additional, independently justified rule."
            ),
        },
        "limitations": [
            "The inverse keyed-alphabet relabeling and X delimiter choice are a specified candidate, "
            "not an established K4 mechanism.",
            "The segment lengths are not a match to the documented 80-city original display.",
            "No physical plate order, UTC assignment, clock orientation, or plaintext is inferred.",
            "A crib-conditioned fit is not independent validation; rotation and shuffled controls are "
            "descriptive only and do not account for hypothesis-selection bias.",
        ],
    }


def write_world_clock_diagnostic(path: str | Path, ciphertext: str = CIPHERTEXT) -> dict[str, Any]:
    """Write the exact diagnostic report used by the API and overnight runs."""
    report = analyze_world_clock_hypothesis(ciphertext)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


__all__ = [
    "CIPHERTEXT",
    "KEYED_ALPHABET",
    "EXPECTED_SEGMENT_LENGTHS",
    "transform_through_keyed_alphabet",
    "split_on_delimiter",
    "shuffled_delimiter_control",
    "analyze_world_clock_hypothesis",
    "write_world_clock_diagnostic",
]
