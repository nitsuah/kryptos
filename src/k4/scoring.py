"""Scoring utilities for candidate plaintexts and segment hypotheses."""
from collections import Counter
from typing import Dict, Iterable
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# ---------------- Loaders ----------------

def _load_letter_freq(path: str) -> Dict[str, float]:
    """Load letter frequency data from a tab-separated values file."""
    freq: Dict[str, float] = {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) != 2:
                    continue
                letter, val = parts
                if len(letter) == 1 and letter.isalpha():
                    freq[letter.upper()] = float(val)
    except FileNotFoundError:
        pass
    return freq


def _load_ngrams(path: str) -> Dict[str, float]:
    """Load n-gram frequency data from a tab-separated values file."""
    grams: Dict[str, float] = {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) != 2:
                    continue
                gram, val = parts
                gram = gram.upper()
                if gram.isalpha():
                    grams[gram] = float(val)
    except FileNotFoundError:
        pass
    return grams

# ---------------- Data ----------------
ENGLISH_FREQ = _load_letter_freq(os.path.join(DATA_DIR, 'letter_freq.tsv')) or {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
}

def chi_square_stat(text: str) -> float:
    """Compute chi-square statistic for letter frequency in text."""
    upper = ''.join(c for c in text.upper() if c.isalpha())
    n = len(upper)
    if n == 0:
        return float('inf')
    counts = Counter(upper)
    chi = 0.0
    for letter, exp in ENGLISH_FREQ.items():
        obs = counts.get(letter, 0)
        expected = exp * n / 100.0
        if expected > 0:
            chi += (obs - expected) ** 2 / expected
    return chi

TRIGRAMS: Dict[str, float] = {
    'THE': -1.0, 'AND': -1.2, 'ING': -1.3, 'ION': -1.4,
}
_UNKNOWN_TRIGRAM = -8.0

def trigram_score(text: str) -> float:
    """Score text based on trigram frequencies."""
    upper = ''.join(c for c in text.upper() if c.isalpha())
    score = 0.0
    for i in range(len(upper) - 2):
        tri = upper[i:i+3]
        score += TRIGRAMS.get(tri, _UNKNOWN_TRIGRAM)
    return score

def combined_plaintext_score(text: str) -> float:
    """Combine chi-square (lower better) and trigram (higher better)."""
    chi = chi_square_stat(text)
    tri = trigram_score(text)
    # Normalize roughly: invert chi component
    return tri - 0.05 * chi


def segment_plaintext_scores(segments: Iterable[str]) -> Dict[str, float]:
    """Score multiple plaintext segments."""
    return {seg: combined_plaintext_score(seg) for seg in segments}

__all__ = [
    'ENGLISH_FREQ',
    'TRIGRAMS',
    'chi_square_stat',
    'trigram_score',
    'combined_plaintext_score',
    'segment_plaintext_scores'
]
