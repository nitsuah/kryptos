"""Bounded diagnostics for the five still-open K4 hypothesis families.

These helpers deliberately separate *coverage diagnostics* from a cipher solve:
they do not promote candidates, score guessed plaintext as evidence, or claim that
an incomplete search eliminates a family. Every returned scope includes the limits
that prevent over-reading a null result.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def align_crib_with_edits(
    ciphertext: str,
    crib: str,
    start: int,
    max_insertions: int = 2,
    max_deletions: int = 2,
) -> list[dict[str, Any]]:
    """Enumerate monotone alignments of a crib to a ciphertext window with edit gaps.

    "Insertion" means an extra ciphertext symbol not represented in the crib;
    "deletion" means a crib symbol absent from the ciphertext. This convention is
    explicit because cryptanalysis literature often reverses these terms.

    The search is exact for the supplied start and edit bounds. It is not a cipher
    model by itself: callers must provide a justified window and preserve mappings
    to original K4 positions before using the result as a constraint.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    target = "".join(c for c in crib.upper() if c.isalpha())
    if start < 0 or start > len(ct) or max_insertions < 0 or max_deletions < 0:
        raise ValueError("start and edit bounds must be non-negative and start within ciphertext")
    # State records: (cipher index, crib index, inserted, deleted, matched pairs)
    states: list[tuple[int, int, int, int, tuple[tuple[int, int], ...]]] = [(start, 0, 0, 0, ())]
    results: list[dict[str, Any]] = []
    while states:
        ci, pi, ins, dele, pairs = states.pop()
        if pi == len(target):
            results.append({
                "start": start,
                "end": ci,
                "insertions": ins,
                "deletions": dele,
                "matches": len(pairs),
                "alignment": pairs,
            })
            continue
        if ci < len(ct) and ct[ci] == target[pi]:
            states.append((ci + 1, pi + 1, ins, dele, pairs + ((ci, pi),)))
        if ci < len(ct) and ins < max_insertions:
            states.append((ci + 1, pi, ins + 1, dele, pairs))
        if dele < max_deletions:
            states.append((ci, pi + 1, ins, dele + 1, pairs))
    # Multiple edit paths can yield the same mapped pairs; retain unique mappings.
    unique: dict[tuple[tuple[int, int], ...], dict[str, Any]] = {}
    for item in results:
        key = item["alignment"]
        prior = unique.get(key)
        if prior is None or (item["insertions"] + item["deletions"]) < (prior["insertions"] + prior["deletions"]):
            unique[key] = item
    return sorted(unique.values(), key=lambda x: (x["insertions"] + x["deletions"], x["start"], x["end"]))


def hill_partial_block_coverage(
    crib_positions: Mapping[int, str],
    ciphertext_length: int = 97,
    sizes: Iterable[int] = range(6, 11),
) -> dict[int, list[dict[str, Any]]]:
    """Report how much confirmed crib evidence reaches each Hill block alignment.

    For a Hill n×n transform, a known plaintext character at position i constrains
    one output row for the block containing i. This reports per-row equation counts
    for each block offset. It does not pretend those sparse equations determine an
    invertible matrix; that requires modular solving plus a named transposition.
    """
    if ciphertext_length < 1:
        raise ValueError("ciphertext_length must be positive")
    positions = sorted(i for i in crib_positions if 0 <= i < ciphertext_length)
    out: dict[int, list[dict[str, Any]]] = {}
    for n in sizes:
        if n < 2:
            raise ValueError("Hill matrix size must be at least 2")
        alignments = []
        known_positions = set(positions)
        for offset in range(n):
            rows = [0] * n
            blocks: set[int] = set()
            for pos in positions:
                if pos < offset:
                    continue
                block_start = offset + ((pos - offset) // n) * n
                if block_start + n > ciphertext_length:
                    continue
                rows[pos - block_start] += 1
                blocks.add(block_start)
            alignments.append({
                "offset": offset,
                "crib_characters_used": sum(rows),
                "distinct_blocks_touched": len(blocks),
                "equations_per_row": rows,
                "fully_known_plaintext_blocks": sum(
                    1
                    for block_start in blocks
                    if all(block_start + k in known_positions for k in range(n))
                ),
                "status": "partial-block constraints only; no matrix elimination performed",
            })
        out[n] = alignments
    return out


def keyed_lookup_streams(
    labels: Iterable[str],
    length: int,
    transforms: Iterable[str] = ("first", "last", "initials", "length"),
) -> list[dict[str, Any]]:
    """Create explicit per-position streams from an ordered physical lookup list.

    A stream is emitted only when its transformed label yields an A–Z symbol at every
    position. The caller must supply the actual plate order; sorting labels here would
    silently invent physical evidence. This is a candidate enumerator, not a claim that
    any of these transforms is historically supported.
    """
    names = ["".join(c for c in label.upper() if c.isalpha()) for label in labels]
    names = [name for name in names if name]
    if length < 1 or not names:
        return []
    out = []
    for transform in transforms:
        chars = []
        for i in range(length):
            label = names[i % len(names)]
            if transform == "first":
                ch = label[0]
            elif transform == "last":
                ch = label[-1]
            elif transform == "initials":
                ch = label[0]
            elif transform == "length":
                ch = chr(ord("A") + (len(label) - 1) % 26)
            else:
                raise ValueError(f"unknown label transform: {transform}")
            chars.append(ch)
        out.append({
            "transform": transform,
            "stream": "".join(chars),
            "labels_used": min(length, len(names)),
            "repeats_labels": length > len(names),
            "requires_confirmed_physical_order": True,
        })
    return out


def bearing_seed_candidates(
    bearings: Iterable[float],
    moduli: Iterable[int] = (26, 24, 360, 720, 1440),
) -> list[dict[str, Any]]:
    """Enumerate named scalar seeds from supplied bearings, without assuming a route.

    Values are kept as explicit alternatives: rounded degrees, tenths of a degree,
    and hundredths of a degree, reduced modulo each requested modulus. This does not
    test arbitrary cipher constructions; it creates reproducible seeds for a caller
    to combine with an independently specified cipher family.
    """
    out = []
    for bearing in bearings:
        if not 0 <= bearing < 360:
            raise ValueError("bearing must be in [0, 360)")
        for scale_name, scale in (("degrees", 1), ("tenths", 10), ("hundredths", 100)):
            raw = round(bearing * scale)
            for modulus in moduli:
                if modulus < 1:
                    raise ValueError("moduli must be positive")
                out.append({
                    "bearing": bearing,
                    "encoding": scale_name,
                    "raw_value": raw,
                    "modulus": modulus,
                    "seed": raw % modulus,
                    "route_assumption": False,
                })
    return out


__all__ = [
    "align_crib_with_edits",
    "hill_partial_block_coverage",
    "keyed_lookup_streams",
    "bearing_seed_candidates",
]
