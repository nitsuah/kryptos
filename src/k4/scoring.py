"""Scoring utilities for K4 analysis (file-driven frequencies)."""
from __future__ import annotations
import os
import json
from collections import Counter
from typing import Dict, Iterable

# Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'config.json')

# ---------------- Loaders ----------------

def _load_letter_freq(path: str) -> Dict[str, float]:
    """Load letter frequency table from file."""
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
    """Load n-gram frequency table from file."""
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


def _load_config_cribs(path: str) -> list[str]:
    """Load cribs from config file."""
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            return [c.upper() for c in data.get('cribs', [])]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# ---------------- Data ----------------
LETTER_FREQ: Dict[str, float] = _load_letter_freq(os.path.join(DATA_DIR, 'letter_freq.tsv'))
BIGRAMS: Dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'bigrams.tsv'))
TRIGRAMS: Dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'trigrams.tsv'))
CRIBS: list[str] = _load_config_cribs(CONFIG_PATH)

# Fallback minimal frequency if file missing
if not LETTER_FREQ:
    LETTER_FREQ = {
        'E': 12.702,'T': 9.056,'A':8.167,'O':7.507,'N':6.749,'I':6.966,
        'S':6.327,'R':5.987,'H':6.094,'L':4.025,'D':4.253,'C':2.782,
        'U':2.758,'M':2.406,'F':2.228,'Y':1.974,'W':2.360,'G':2.015,
        'P':1.929,'B':1.492,'V':0.978,'K':0.772,'X':0.150,'J':0.153,
        'Q':0.095,'Z':0.074
    }

_UNKNOWN_BIGRAM = -2.0
_UNKNOWN_TRIGRAM = -2.5

# ---------------- Metrics ----------------

def chi_square_stat(text: str) -> float:
    """Chi-square statistic vs English letter frequencies (lower is better)."""
    filtered = [c for c in text.upper() if c.isalpha()]
    n = len(filtered)
    if n == 0:
        return float('inf')
    counts = Counter(filtered)
    chi = 0.0
    for letter, exp in LETTER_FREQ.items():
        obs = counts.get(letter, 0)
        expected = exp * n / 100.0
        if expected > 0:
            chi += (obs - expected) ** 2 / expected
    return chi

def _score_ngrams(text: str, table: Dict[str, float], size: int, unknown: float) -> float:
    """Generic n-gram scoring function."""
    seq = ''.join(c for c in text.upper() if c.isalpha())
    total = 0.0
    for i in range(len(seq) - size + 1):
        gram = seq[i:i+size]
        total += table.get(gram, unknown)
    return total

def bigram_score(text: str) -> float:
    """Score text based on bigram frequencies."""
    return _score_ngrams(text, BIGRAMS, 2, _UNKNOWN_BIGRAM)

def trigram_score(text: str) -> float:
    """Score text based on trigram frequencies."""
    return _score_ngrams(text, TRIGRAMS, 3, _UNKNOWN_TRIGRAM)

def crib_bonus(text: str) -> float:
    """Bonus score for presence of known cribs."""
    upper = ''.join(c for c in text.upper() if c.isalpha())
    bonus = 0.0
    for crib in CRIBS:
        if crib and crib in upper:
            bonus += 5.0 * len(crib)
    return bonus

def combined_plaintext_score(text: str) -> float:
    """Higher is better: n-gram scores minus weighted chi-square plus crib bonus."""
    chi = chi_square_stat(text)
    bi = bigram_score(text)
    tri = trigram_score(text)
    return bi + tri - 0.05 * chi + crib_bonus(text)

def segment_plaintext_scores(segments: Iterable[str]) -> Dict[str, float]:
    """Compute combined plaintext scores for multiple segments."""
    return {seg: combined_plaintext_score(seg) for seg in segments}

__all__ = [
    'LETTER_FREQ','BIGRAMS','TRIGRAMS','CRIBS',
    'chi_square_stat','bigram_score','trigram_score','crib_bonus',
    'combined_plaintext_score','segment_plaintext_scores'
]
