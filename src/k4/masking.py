"""Masking / null-removal heuristics for K4 analysis.

Generates candidate plaintext variants by removing or substituting suspected null/padding characters
and evaluating resulting texts.
"""
from __future__ import annotations
from typing import Any

from collections.abc import Iterable
from .scoring import combined_plaintext_score

DEFAULT_NULLS = {'X', 'Y'}


def remove_chars(text: str, chars: Iterable[str]) -> str:
    """Return text with all occurrences of chars removed (case-insensitive for alpha)."""
    remove = {c.upper() for c in chars}
    return ''.join(ch for ch in text if ch.upper() not in remove)


def collapse_runs(text: str, char: str, max_run: int = 2) -> str:
    """Collapse runs of a given char longer than max_run down to max_run length."""
    out: list[str] = []
    run = 0
    for ch in text:
        if ch.upper() == char.upper():
            run += 1
            if run <= max_run:
                out.append(ch)
        else:
            run = 0
            out.append(ch)
    return ''.join(out)


def mask_variants(text: str, null_chars: Iterable[str] | None = None) -> list[str]:
    """Generate simple masking variants: full removal and run-collapsed versions for each null char."""
    if null_chars is None:
        null_chars = DEFAULT_NULLS
    variants: list[str] = []
    base = text
    for n in null_chars:
        removed = remove_chars(base, [n])
        variants.append(removed)
        collapsed = collapse_runs(base, n, max_run=1)
        variants.append(collapsed)
    # Combined removal of all
    variants.append(remove_chars(base, null_chars))
    # Deduplicate while preserving order
    seen = set()
    uniq: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def score_mask_variants(text: str, null_chars: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """Produce scored variant list sorted by score desc."""
    vars_ = mask_variants(text, null_chars)
    scored: list[dict[str, Any]] = []
    for v in vars_:
        scored.append({'text': v, 'score': combined_plaintext_score(v), 'variant': 'mask'})
    scored.sort(key=lambda r: r['score'], reverse=True)
    return scored


__all__ = ['DEFAULT_NULLS', 'remove_chars', 'collapse_runs', 'mask_variants', 'score_mask_variants']
