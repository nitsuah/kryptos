"""Scoring utilities for candidate plaintexts and segment hypotheses."""
from collections import Counter
from typing import Dict, Iterable

# Basic English letter frequency (approximate) cleaned (no duplicates)
ENGLISH_FREQ = {
    'E': 12.0, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7, 'S': 6.3,
    'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4,
    'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5, 'V': 1.0,
    'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
}
TOTAL_FREQ = sum(ENGLISH_FREQ.values())


def chi_square_stat(text: str) -> float:
    counts = Counter(c for c in text if c.isalpha())
    length = sum(counts.values())
    if length == 0:
        return float('inf')
    chi = 0.0
    for letter, expected_pct in ENGLISH_FREQ.items():
        observed = counts.get(letter, 0)
        expected = length * (expected_pct / TOTAL_FREQ)
        chi += (observed - expected) ** 2 / expected if expected > 0 else 0
    return chi

# Placeholder trigram log probabilities; real values should be loaded from file.
TRIGRAMS: Dict[str, float] = {
    'THE': -1.0, 'AND': -1.2, 'ING': -1.3, 'TION': -1.5  # example (TION is 4 letters)
}


def trigram_score(text: str) -> float:
    score = 0.0
    upper = ''.join(c for c in text.upper() if c.isalpha())
    for i in range(len(upper) - 2):
        tri = upper[i:i+3]
        score += TRIGRAMS.get(tri, -5.0)  # unknown trigrams get heavy penalty
    return score


def combined_plaintext_score(text: str) -> float:
    """Combine chi-square (lower better) and trigram (higher better)."""
    chi = chi_square_stat(text)
    tri = trigram_score(text)
    # Normalize roughly: invert chi component
    return tri - 0.05 * chi


def segment_plaintext_scores(segments: Iterable[str]) -> Dict[str, float]:
    return {seg: combined_plaintext_score(seg) for seg in segments}
