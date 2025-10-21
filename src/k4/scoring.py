"""Scoring utilities for K4 analysis (file-driven frequencies)."""
from __future__ import annotations
import os
import json
from collections import Counter
from typing import Dict, Iterable, Sequence

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
# Prefer high quality quadgrams file if present
_quad_hi_path = os.path.join(DATA_DIR, 'quadgrams_high_quality.tsv')
if os.path.exists(_quad_hi_path):
    QUADGRAMS: Dict[str, float] = _load_ngrams(_quad_hi_path)
else:
    QUADGRAMS: Dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'quadgrams.tsv'))
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
_UNKNOWN_QUADGRAM = -4.0  # slightly harsher unknown penalty with higher quality table

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

def quadgram_score(text: str) -> float:
    """Score text based on quadgram frequencies."""
    return _score_ngrams(text, QUADGRAMS, 4, _UNKNOWN_QUADGRAM)

def crib_bonus(text: str) -> float:
    """Bonus score for presence of known cribs."""
    upper = ''.join(c for c in text.upper() if c.isalpha())
    bonus = 0.0
    for crib in CRIBS:
        if crib and crib in upper:
            bonus += 5.0 * len(crib)
    return bonus

def positional_crib_bonus(text: str, positional: Dict[str, Sequence[int]], window: int = 5) -> float:
    """Compute bonus for cribs appearing near expected positional indices.
    positional: mapping crib -> iterable of expected start indices (0-based).
    For each occurrence of crib in text, if distance to any expected index <= window,
    award (8 * len(crib) - distance). Multiple positions can contribute; occurrences outside
    window give no bonus. Cribs not found yield zero.
    """
    if not positional:
        return 0.0
    upper = ''.join(c for c in text.upper() if c.isalpha())
    total = 0.0
    for crib, expected_positions in positional.items():
        c = crib.upper()
        if not c or c not in upper:
            continue
        # Find all occurrences
        starts = []
        idx = upper.find(c)
        while idx != -1:
            starts.append(idx)
            idx = upper.find(c, idx + 1)
        for occ in starts:
            # Compute closest expected index
            if expected_positions:
                dist = min(abs(occ - ep) for ep in expected_positions)
                if dist <= window:
                    total += max(0.0, (8 * len(c) - dist))
    return total

def combined_plaintext_score(text: str) -> float:
    """Higher is better: n-gram scores minus weighted chi-square plus crib bonus."""
    chi = chi_square_stat(text)
    bi = bigram_score(text)
    tri = trigram_score(text)
    quad = quadgram_score(text) if QUADGRAMS else 0.0
    return bi + tri + quad - 0.05 * chi + crib_bonus(text)

def combined_plaintext_score_with_positions(text: str, positional: Dict[str, Sequence[int]], window: int = 5) -> float:
    """Extended combined score including positional crib bonus."""
    base = combined_plaintext_score(text)
    pos_bonus = positional_crib_bonus(text, positional, window)
    return base + pos_bonus

def segment_plaintext_scores(segments: Iterable[str]) -> Dict[str, float]:
    """Compute combined plaintext scores for multiple segments."""
    return {seg: combined_plaintext_score(seg) for seg in segments}

def index_of_coincidence(text: str) -> float:
    """Compute index of coincidence (IC)."""
    letters = [c for c in text.upper() if c.isalpha()]
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    num = sum(v * (v - 1) for v in counts.values())
    den = n * (n - 1)
    return num / den if den else 0.0

def vowel_ratio(text: str) -> float:
    """Return proportion of letters that are vowels (AEIOUY)."""
    letters = [c for c in text.upper() if c.isalpha()]
    if not letters:
        return 0.0
    vowels = set('AEIOUY')
    vcount = sum(1 for c in letters if c in vowels)
    return vcount / len(letters)

def letter_coverage(text: str) -> float:
    """Return fraction of alphabet present in text."""
    letters = {c for c in text.upper() if c.isalpha()}
    return len(letters) / 26.0

def baseline_stats(text: str) -> Dict[str, float]:
    """Return dictionary of baseline scoring metrics for a candidate plaintext."""
    return {
        'chi_square': chi_square_stat(text),
        'bigram_score': bigram_score(text),
        'trigram_score': trigram_score(text),
        'crib_bonus': crib_bonus(text),
        'combined_score': combined_plaintext_score(text),
        'index_of_coincidence': index_of_coincidence(text),
        'vowel_ratio': vowel_ratio(text),
        'letter_coverage': letter_coverage(text),
    }

__all__ = [
    'LETTER_FREQ','BIGRAMS','TRIGRAMS','CRIBS','QUADGRAMS',
    'chi_square_stat','bigram_score','trigram_score','crib_bonus','quadgram_score',
    'combined_plaintext_score','segment_plaintext_scores',
    'index_of_coincidence','vowel_ratio','letter_coverage','baseline_stats',
    'positional_crib_bonus','combined_plaintext_score_with_positions'
]
