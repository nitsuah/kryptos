"""Scoring utilities for candidate plaintexts and segment hypotheses."""
from collections import Counter
from typing import Dict, Iterable
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load letter frequencies
def _load_letter_freq(path: str) -> Dict[str, float]:
    """Load letter frequency from TSV file."""
    freq: Dict[str, float] = {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                letter, val = line.split('\t')
                freq[letter.upper()] = float(val)
    except FileNotFoundError:
        pass
    return freq

# Replace partial fallback with complete frequencies if file not found
ENGLISH_FREQ = _load_letter_freq(os.path.join(DATA_DIR, 'letter_freq.tsv')) or {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
    }

def chi_square_stat(text: str) -> float:
    """Compute chi-square statistic for letter frequency in text vs English."""
    upper = ''.join(c for c in text.upper() if c.isalpha())
    total = len(upper)
    if total == 0:
        return float('inf')
    counts = Counter(upper)
    chi = 0.0
    for letter, expected_freq in ENGLISH_FREQ.items():
        observed = counts.get(letter, 0)
        expected = expected_freq * total / 100.0
        chi += (observed - expected) ** 2 / expected if expected > 0 else 0
    return chi

# Placeholder trigram log probabilities; real values should be loaded from file.
TRIGRAMS: Dict[str, float] = {
    'THE': -1.0, 'AND': -1.2, 'ING': -1.3, 'TION': -1.5  # example (TION is 4 letters)
}


def trigram_score(text: str) -> float:
    """Calculate trigram score for text using log probabilities."""
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
    """Score multiple plaintext segments."""
    return {seg: combined_plaintext_score(seg) for seg in segments}
