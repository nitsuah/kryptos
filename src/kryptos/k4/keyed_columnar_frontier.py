"""Exact crib-gated frontier for long, clue-derived columnar keys.

The existing columnar searches enumerate all column orders for widths 2–14
within their documented period ranges; some high-period cases remain
underconstrained. Larger widths are too expensive to enumerate over every
permutation. This module tests
a narrower, falsifiable family instead: column orders induced by longer
Weltzeituhr city labels and by those labels concatenated with the already-known
K1/K2 key words.

This is deliberately not a plaintext scorer. A candidate survives only when a
single, precisely specified columnar permutation and one tested periodic cipher
family satisfy every confirmed K4 crib. A null result rejects only this finite
candidate set, not all irregular transpositions or all possible clock keys.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any

import numpy as np

from .crib_constraints import STANDARD, _columnar_pt_to_ct, _scan_mappings, crib_letters
from .world_clock_cities import CONFIRMED_CITIES

MIN_WIDTH = 15
MAX_WIDTH = 26
ALPHABET_SEEDS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")
KNOWN_KEYWORDS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")
PERIODS = tuple(range(1, 23))


def _letters(value: str) -> str:
    """Keep A–Z only, matching the project's other cipher modules."""
    return "".join(ch for ch in value.upper() if ch in STANDARD)


def keyed_columnar_order(keyword: str) -> tuple[int, ...]:
    """Return the conventional stable alphabetical column order for a keyword.

    Equal letters retain their left-to-right order. The returned tuple contains
    original column indexes in the order the columns are read.
    """
    key = _letters(keyword)
    if not key:
        raise ValueError("keyword must contain at least one ASCII A-Z letter")
    return tuple(sorted(range(len(key)), key=lambda index: (key[index], index)))


def candidate_keywords(
    city_names: Iterable[str] | None = None,
    min_width: int = MIN_WIDTH,
    max_width: int = MAX_WIDTH,
) -> list[str]:
    """Build the finite, provenance-labelled keyword set for this experiment.

    Sources are the city labels actually transcribed in CONFIRMED_CITIES, plus
    those labels concatenated in both orders with KRYPTOS, PALIMPSEST, or
    ABSCISSA. The latter tests the explicit clock-key + earlier-panel-key
    variant. It does not invent country names or assume the partial city list
    is complete.
    """
    if min_width < 1 or max_width < min_width:
        raise ValueError("expected 1 <= min_width <= max_width")

    cities = CONFIRMED_CITIES if city_names is None else city_names
    normalized_cities = sorted({_letters(city) for city in cities} - {""})
    candidates = set(normalized_cities)
    for city in normalized_cities:
        for key in KNOWN_KEYWORDS:
            candidates.add(city + key)
            candidates.add(key + city)

    return sorted(
        keyword for keyword in candidates
        if min_width <= len(keyword) <= max_width and keyword.isalpha()
    )


def candidate_keywords_for_scan(
    keywords: Iterable[str],
    *,
    min_width: int = MIN_WIDTH,
    max_width: int = MAX_WIDTH,
) -> list[str]:
    """Normalize and width-filter an explicitly supplied candidate set."""
    if min_width < 1 or max_width < min_width:
        raise ValueError("expected 1 <= min_width <= max_width")
    return sorted(
        {
            _letters(keyword)
            for keyword in keywords
            if min_width <= len(_letters(keyword)) <= max_width
        }
    )


def run_keyed_columnar_frontier(
    ciphertext: str,
    plain: dict[int, str] | None = None,
    *,
    keywords: Sequence[str] | None = None,
    alphabet_keywords: Sequence[str] = ALPHABET_SEEDS,
    periods: Iterable[int] = PERIODS,
    min_width: int = MIN_WIDTH,
    max_width: int = MAX_WIDTH,
    min_key_slot_collisions: int = 8,
) -> dict[str, Any]:
    """Test clue-derived column orders against all confirmed crib constraints.

    For each distinct column permutation induced by a candidate keyword, test
    both layer orders, five cipher-family variants, each requested period, and
    each requested keyed-alphabet seed. Repeated keyword anagrams share a
    permutation and are tested only once, while all spellings are retained in
    result metadata.

    Ciphertext and plain are injectable so tests can plant a known solution.
    This function never labels the full family eliminated.
    """
    ct = _letters(ciphertext)
    if not ct:
        raise ValueError("ciphertext must contain at least one A-Z letter")
    if min_width < 1 or max_width < min_width:
        raise ValueError("expected 1 <= min_width <= max_width")

    normalized_plain = plain if plain is not None else crib_letters()
    if any(pos < 0 or pos >= len(ct) for pos in normalized_plain):
        raise ValueError("every crib position must fall inside the normalized ciphertext")
    if any(ch not in STANDARD for ch in normalized_plain.values()):
        raise ValueError("crib values must be A-Z letters")

    selected_keywords = candidate_keywords(min_width=min_width, max_width=max_width) if keywords is None else (
        candidate_keywords_for_scan(keywords, min_width=min_width, max_width=max_width)
    )
    period_values = sorted({int(p) for p in periods})
    if any(p < 1 or p > len(ct) for p in period_values):
        raise ValueError("periods must be between 1 and the ciphertext length")
    if not alphabet_keywords:
        raise ValueError("at least one alphabet keyword is required")

    # A transposition permutation is determined by the stable alphabetical
    # rank order, not by the literal keyword. Group equivalent orders so that
    # anagrams do not inflate the apparent search coverage.
    grouped: dict[int, dict[tuple[int, ...], list[str]]] = defaultdict(lambda: defaultdict(list))
    for keyword in selected_keywords:
        order = keyed_columnar_order(keyword)
        grouped[len(keyword)][order].append(keyword)

    if min_key_slot_collisions < 0 or min_key_slot_collisions > len(normalized_plain):
        raise ValueError("min_key_slot_collisions must be between zero and the crib-letter count")

    crib_positions = np.array(sorted(normalized_plain), dtype=np.int64)
    hits: list[dict[str, Any]] = []
    underconstrained_examples: list[dict[str, Any]] = []
    raw_survivors = 0
    orders_tested = 0
    checks_run = 0
    for width in sorted(grouped):
        orders = sorted(grouped[width])
        permutations = np.asarray(orders, dtype=np.int16)
        starts = _columnar_pt_to_ct(width, permutations, len(ct))
        cpos = starts[:, crib_positions % width] + crib_positions // width
        labels = [
            {"width": width, "order": list(order), "keywords": sorted(grouped[width][order])}
            for order in orders
        ]
        positions_by_order = {order: cpos[i] for i, order in enumerate(orders)}
        orders_tested += len(orders)

        for alphabet_keyword in alphabet_keywords:
            scan = _scan_mappings(
                cpos,
                labels,
                ct,
                normalized_plain,
                period_values,
                alphabet_keyword,
                max_examples=len(labels),
            )
            checks_run += len(labels) * len(period_values) * 5 * 2
            for layer_order, families in scan.items():
                for family, by_period in families.items():
                    for period, result in by_period.items():
                        if not result["survivors"]:
                            continue
                        raw_survivors += result["survivors"]
                        robust_examples = []
                        for example in result["examples"]:
                            order = tuple(example["order"])
                            slots = (
                                crib_positions % period
                                if layer_order == "sub_then_trans"
                                else positions_by_order[order] % period
                            )
                            collisions = len(crib_positions) - len(np.unique(slots))
                            enriched = {**example, "repeated_key_slot_constraints": int(collisions)}
                            if collisions >= min_key_slot_collisions:
                                robust_examples.append(enriched)
                            elif len(underconstrained_examples) < 25:
                                underconstrained_examples.append(
                                    {
                                        "alphabet_keyword": alphabet_keyword,
                                        "layer_order": layer_order,
                                        "family": family,
                                        "period": period,
                                        **enriched,
                                    }
                                )
                        if robust_examples:
                            hits.append(
                                {
                                    "alphabet_keyword": alphabet_keyword,
                                    "layer_order": layer_order,
                                    "family": family,
                                    "period": period,
                                    "survivors": len(robust_examples),
                                    "examples": robust_examples,
                                }
                            )

    return {
        "status": "hits" if hits else "null_result",
        "ciphertext_length": len(ct),
        "crib_letters": len(normalized_plain),
        "keyword_candidates": len(selected_keywords),
        "unique_column_orders": orders_tested,
        "alphabet_keywords": list(alphabet_keywords),
        "periods": period_values,
        "minimum_repeated_key_slot_constraints": min_key_slot_collisions,
        "checks_run": checks_run,
        "raw_crib_consistent_survivors": raw_survivors,
        "underconstrained_examples_sample": underconstrained_examples,
        "widths": sorted(grouped),
        "hits": hits,
        "scope_note": (
            "A null result covers only these clue-derived conventional column orders, "
            "alphabet seeds, layer orders, and periods. It does not rule out arbitrary "
            "wide columnar orders, disrupted transposition, country names absent from "
            "the sourced city list, or per-character World Clock lookups."
        ),
    }


__all__ = [
    "ALPHABET_SEEDS",
    "MAX_WIDTH",
    "MIN_WIDTH",
    "candidate_keywords",
    "candidate_keywords_for_scan",
    "keyed_columnar_order",
    "run_keyed_columnar_frontier",
]
