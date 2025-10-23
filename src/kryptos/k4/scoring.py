"""Scoring utilities for K4 analysis (file-driven frequencies)."""

from __future__ import annotations

import json
import math
import os
from collections import Counter
from collections.abc import Iterable, Sequence
from functools import lru_cache
from pathlib import Path

# Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'config.json')

# ---------------- Loaders ----------------


def _load_letter_freq(path: str) -> dict[str, float]:
    """Load letter frequency table from file."""
    freq: dict[str, float] = {}
    try:
        with open(path, encoding='utf-8') as fh:
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


def _load_ngrams(path: str) -> dict[str, float]:
    """Load n-gram frequency table from file."""
    grams: dict[str, float] = {}
    try:
        with open(path, encoding='utf-8') as fh:
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
        # Missing n-gram file: return empty; letter freq fallback handled separately.
        return {}
    return grams


def _load_config_cribs(path: str) -> list[str]:
    """Load cribs from config file (expects top-level 'cribs' list)."""
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
            cribs = data.get('cribs', [])
            return [c.upper() for c in cribs if isinstance(c, str)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _load_wordlist(path: str) -> set[str]:
    """Load wordlist (one word per line) into uppercase set. Only keep length >=3."""
    words: set[str] = set()
    try:
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                w = line.strip().upper()
                if len(w) >= 3 and w.isalpha():
                    words.add(w)
    except FileNotFoundError:
        pass
    return words


# ---------------- Data ----------------
LETTER_FREQ: dict[str, float] = _load_letter_freq(os.path.join(DATA_DIR, 'letter_freq.tsv'))
BIGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'bigrams.tsv'))
TRIGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'trigrams.tsv'))
# Prefer high quality quadgrams file if present
_quad_hi_path = os.path.join(DATA_DIR, 'quadgrams_high_quality.tsv')
if os.path.exists(_quad_hi_path):
    QUADGRAMS: dict[str, float] = _load_ngrams(_quad_hi_path)
else:
    QUADGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'quadgrams.tsv'))

CRIBS: list[str] = _load_config_cribs(CONFIG_PATH)
WORDLIST: set[str] = _load_wordlist(os.path.join(DATA_DIR, 'wordlist.txt'))

# Berlin Clock pattern reference words (stub for pattern validator)
BERLIN_CLOCK_TERMS = {'BERLIN', 'CLOCK'}

if not LETTER_FREQ:
    LETTER_FREQ = {
        'E': 12.702,
        'T': 9.056,
        'A': 8.167,
        'O': 7.507,
        'N': 6.749,
        'I': 6.966,
        'S': 6.327,
        'R': 5.987,
        'H': 6.094,
        'L': 4.025,
        'D': 4.253,
        'C': 2.782,
        'U': 2.758,
        'M': 2.406,
        'F': 2.228,
        'Y': 1.974,
        'W': 2.360,
        'G': 2.015,
        'P': 1.929,
        'B': 1.492,
        'V': 0.978,
        'K': 0.772,
        'X': 0.150,
        'J': 0.153,
        'Q': 0.095,
        'Z': 0.074,
    }

# Minimal fallback wordlist (placeholder)
if not WORDLIST:
    WORDLIST = {
        'THE',
        'AND',
        'YOU',
        'THAT',
        'FOR',
        'WITH',
        'HAVE',
        'THIS',
        'FROM',
        'CLOCK',
        'BERLIN',
        'TIME',
        'CODE',
        'DATA',
        'NEXT',
        'OVER',
        'PART',
        'TEXT',
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


def _score_ngrams(text: str, table: dict[str, float], size: int, unknown: float) -> float:
    """Generic n-gram scoring function."""
    seq = ''.join(c for c in text.upper() if c.isalpha())
    total = 0.0
    for i in range(len(seq) - size + 1):
        gram = seq[i : i + size]
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


def positional_crib_bonus(text: str, positional: dict[str, Sequence[int]], window: int = 5) -> float:
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


# Cached wrapper (memoization for repeated scoring of identical plaintexts)
@lru_cache(maxsize=10000)
def combined_plaintext_score_cached(text: str) -> float:
    """Cached version of combined_plaintext_score."""
    return combined_plaintext_score(text)


def berlin_clock_pattern_validator(text: str) -> dict[str, bool | int]:
    """Stub validator: check presence & ordering of BERLIN before CLOCK; future logic may
    incorporate lamp pattern alignment or temporal sequencing. Returns dict with flags.
    """
    upper = ''.join(c for c in text.upper() if c.isalpha())
    has_berlin = 'BERLIN' in upper
    has_clock = 'CLOCK' in upper
    order_ok = False
    if has_berlin and has_clock:
        order_ok = upper.find('BERLIN') < upper.find('CLOCK')
    return {
        'has_berlin': has_berlin,
        'has_clock': has_clock,
        'berlin_before_clock': order_ok,
        'pattern_bonus': int(has_berlin and has_clock and order_ok),  # simple 1/0 bonus
    }


def combined_plaintext_score_extended(text: str) -> float:
    """Extended combined score including berlin clock pattern bonus (small weight)."""
    base = combined_plaintext_score(text)
    pattern = berlin_clock_pattern_validator(text)
    # weight bonus modestly to avoid overpowering n-gram scoring
    return base + 25.0 * pattern['pattern_bonus']


# --- Advanced linguistic metrics -------------------------------------------


def wordlist_hit_rate(text: str, min_len: int = 3, max_len: int = 8) -> float:
    """Approximate word-likeness: ratio of substring windows that appear in WORDLIST.
    Iterates all windows length in [min_len, max_len]; caps total windows at 5000 for performance.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    n = len(seq)
    if n < min_len:
        return 0.0
    total = 0
    hits = 0
    for L in range(min_len, max_len + 1):
        if L > n:
            break
        for i in range(n - L + 1):
            if total >= 5000:
                break
            total += 1
            if seq[i : i + L] in WORDLIST:
                hits += 1
        if total >= 5000:
            break
    return hits / total if total else 0.0


def trigram_entropy(text: str) -> float:
    """Shannon entropy over trigram distribution (A-Z only)."""
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 3:
        return 0.0
    trigrams = [seq[i : i + 3] for i in range(len(seq) - 3 + 1)]
    counts = Counter(trigrams)
    n = sum(counts.values())
    ent = 0.0
    for v in counts.values():
        p = v / n
        ent -= p * math.log2(p)
    return ent


def bigram_gap_variance(text: str) -> float:
    """Average variance of gaps between repeated bigram occurrences.
    For each bigram occurring >=2 times, compute gaps between each start indices.
    Return average variance across such bigrams (0 if none).
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 4:
        return 0.0
    positions: dict[str, list[int]] = {}
    for i in range(len(seq) - 2 + 1):
        gram = seq[i : i + 2]
        positions.setdefault(gram, []).append(i)
    gap_vars: list[float] = []
    for _gram, pos_list in positions.items():
        if len(pos_list) < 2:
            continue
        gaps = [pos_list[i + 1] - pos_list[i] for i in range(len(pos_list) - 1)]
        if not gaps:
            continue
        mean_gap = sum(gaps) / len(gaps)
        var = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
        gap_vars.append(var)
    if not gap_vars:
        return 0.0
    return sum(gap_vars) / len(gap_vars)


# ---------------- Baseline stats ----------------


def baseline_stats(text: str) -> dict[str, float]:
    """Return dictionary of baseline scoring metrics for a candidate plaintext."""
    stats = {
        'chi_square': chi_square_stat(text),
        'bigram_score': bigram_score(text),
        'trigram_score': trigram_score(text),
        'quadgram_score': quadgram_score(text) if QUADGRAMS else 0.0,
        'crib_bonus': crib_bonus(text),
        'combined_score': combined_plaintext_score(text),
        'index_of_coincidence': index_of_coincidence(text),
        'vowel_ratio': vowel_ratio(text),
        'letter_coverage': letter_coverage(text),
        'letter_entropy': letter_entropy(text),
        'repeating_bigram_fraction': repeating_bigram_fraction(text),
        'wordlist_hit_rate': wordlist_hit_rate(text),
        'trigram_entropy': trigram_entropy(text),
        'bigram_gap_variance': bigram_gap_variance(text),
    }
    pattern = berlin_clock_pattern_validator(text)
    stats.update(
        {
            'berlin_clock_pattern_bonus': float(pattern['pattern_bonus']),
        },
    )
    return stats


def segment_plaintext_scores(segments: Iterable[str]) -> dict[str, float]:
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


def letter_entropy(text: str) -> float:
    """Shannon entropy (bits) of letter distribution (A-Z only)."""
    letters = [c for c in text.upper() if c.isalpha()]
    n = len(letters)
    if n == 0:
        return 0.0
    counts = Counter(letters)
    ent = 0.0
    for v in counts.values():
        p = v / n
        ent -= p * math.log2(p)
    return ent


def repeating_bigram_fraction(text: str) -> float:
    """Fraction of bigrams that are repeats (duplicate occurrences) among all bigrams.
    0 if no bigrams.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0
    bigrams = [seq[i : i + 2] for i in range(len(seq) - 2 + 1)]
    counts = Counter(bigrams)
    repeats = sum(v for v in counts.values() if v > 1)
    return repeats / len(bigrams)


def combined_plaintext_score_with_positions(text: str, positional: dict[str, Sequence[int]], window: int = 5) -> float:
    """Combined plaintext score augmented with positional crib bonuses."""
    base = combined_plaintext_score(text)
    pos_bonus = positional_crib_bonus(text, positional, window)
    return base + pos_bonus


def load_cribs_from_file(path: str | Path) -> list[str]:
    """Load a simple tab-separated crib candidate file (CANDIDATE\tSOURCE\tCONTEXT).

    Returns list of uppercase candidate tokens. Gracefully returns empty list on
    missing file or parse errors.
    """
    try:
        p = Path(path)
    except Exception:
        return []
    if not p.exists():
        return []
    cribs: list[str] = []
    try:
        with p.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                token = parts[0].strip().upper() if parts else ''
                if token.isalpha() and len(token) >= 3:
                    cribs.append(token)
    except Exception:
        return []
    return cribs


def combined_plaintext_score_with_external_cribs(
    text: str,
    external_cribs: Iterable[str],
    crib_weight: float = 1.0,
) -> float:
    """Compute combined score while applying a conservative external crib bonus.

    external_cribs: iterable of uppercase strings. crib_weight scales the bonus so
    higher values increase influence. This function does not mutate module globals.
    """
    base = combined_plaintext_score(text)
    if not external_cribs:
        return base
    upper = ''.join(c for c in text.upper() if c.isalpha())
    bonus = 0.0
    for crib in external_cribs:
        c = crib.upper()
        if c and c in upper:
            bonus += 5.0 * len(c) * float(crib_weight)
    return base + bonus


__all__ = [
    'LETTER_FREQ',
    'BIGRAMS',
    'TRIGRAMS',
    'CRIBS',
    'QUADGRAMS',
    'WORDLIST',
    'chi_square_stat',
    'bigram_score',
    'trigram_score',
    'crib_bonus',
    'quadgram_score',
    'combined_plaintext_score',
    'combined_plaintext_score_cached',
    'segment_plaintext_scores',
    'index_of_coincidence',
    'vowel_ratio',
    'letter_coverage',
    'baseline_stats',
    'positional_crib_bonus',
    'combined_plaintext_score_with_positions',
    'letter_entropy',
    'repeating_bigram_fraction',
    'wordlist_hit_rate',
    'trigram_entropy',
    'bigram_gap_variance',
    'berlin_clock_pattern_validator',
    'combined_plaintext_score_extended',
    'load_cribs_from_file',
    'combined_plaintext_score_with_external_cribs',
]
