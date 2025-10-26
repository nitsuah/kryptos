"""Scoring utilities for K4 analysis (file-driven frequencies)."""

from __future__ import annotations

import json
import math
import os
from collections import Counter
from collections.abc import Iterable, Sequence
from functools import lru_cache
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'config.json')


def _load_letter_freq(path: str) -> dict[str, float]:
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
        return {}
    return grams


def _load_config_cribs(path: str) -> list[str]:
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
            cribs = data.get('cribs', [])
            return [c.upper() for c in cribs if isinstance(c, str)]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _load_wordlist(path: str) -> set[str]:
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


LETTER_FREQ: dict[str, float] = _load_letter_freq(os.path.join(DATA_DIR, 'letter_freq.tsv'))
BIGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'bigrams.tsv'))
TRIGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'trigrams.tsv'))
_quad_hi_path = os.path.join(DATA_DIR, 'quadgrams_high_quality.tsv')
if os.path.exists(_quad_hi_path):
    QUADGRAMS: dict[str, float] = _load_ngrams(_quad_hi_path)
else:
    QUADGRAMS: dict[str, float] = _load_ngrams(os.path.join(DATA_DIR, 'quadgrams.tsv'))

CRIBS: list[str] = _load_config_cribs(CONFIG_PATH)
WORDLIST: set[str] = _load_wordlist(os.path.join(DATA_DIR, 'wordlist.txt'))

_promoted_cribs_cache: dict[str, tuple[float, set[str]]] = {}

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
_UNKNOWN_QUADGRAM = -4.0


def chi_square_stat(text: str) -> float:
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
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < size:
        return 0.0

    total = 0.0
    table_get = table.get
    for i in range(len(seq) - size + 1):
        total += table_get(seq[i : i + size], unknown)
    return total


def bigram_score(text: str) -> float:
    return _score_ngrams(text, BIGRAMS, 2, _UNKNOWN_BIGRAM)


def trigram_score(text: str) -> float:
    return _score_ngrams(text, TRIGRAMS, 3, _UNKNOWN_TRIGRAM)


def quadgram_score(text: str) -> float:
    return _score_ngrams(text, QUADGRAMS, 4, _UNKNOWN_QUADGRAM)


def _get_all_cribs() -> list[str]:
    from kryptos.spy.crib_store import PROMOTED_CRIBS_PATH, load_promoted_cribs

    all_cribs = list(CRIBS)
    config_set = set(CRIBS)

    if PROMOTED_CRIBS_PATH.exists():
        mtime = PROMOTED_CRIBS_PATH.stat().st_mtime
        cache_key = "promoted"
        cached = _promoted_cribs_cache.get(cache_key)
        if cached is None or cached[0] != mtime:
            promoted = load_promoted_cribs()
            _promoted_cribs_cache[cache_key] = (mtime, promoted)
        else:
            promoted = cached[1]
        all_cribs.extend([c for c in promoted if c not in config_set])
    return all_cribs


def crib_bonus(text: str) -> float:
    upper = ''.join(c for c in text.upper() if c.isalpha())
    bonus = 0.0
    for crib in _get_all_cribs():
        if crib and crib in upper:
            bonus += 5.0 * len(crib)
    return bonus


def rarity_weighted_crib_bonus(text: str) -> float:
    all_cribs = _get_all_cribs()
    if not all_cribs:
        return 0.0
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if not seq:
        return 0.0
    rarities: dict[str, float] = {}
    max_rarity = 0.0
    for letter, pct in LETTER_FREQ.items():
        p = pct / 100.0 if pct > 0 else 0.0001
        r = 1.0 / p
        rarities[letter] = r
        if r > max_rarity:
            max_rarity = r

    def _crib_occurrences(crib: str) -> list[int]:
        starts = []
        idx = seq.find(crib)
        while idx != -1:
            starts.append(idx)
            idx = seq.find(crib, idx + 1)
        return starts

    total = 0.0
    for crib in all_cribs:
        c = crib.upper()
        if not c or c not in seq:
            continue
        occs = _crib_occurrences(c)
        factors = []
        for letter in c:
            r = rarities.get(letter, 1.0)
            if max_rarity > 0:
                r /= max_rarity
            factors.append(r)
        rarity_factor = sum(factors) / len(factors) if factors else 0.0
        base = len(c)
        per_bonus = 4.0 * base * rarity_factor
        total += per_bonus * len(occs)
    return total


def positional_crib_bonus(text: str, positional: dict[str, Sequence[int]], window: int = 5) -> float:
    if not positional:
        return 0.0
    upper = ''.join(c for c in text.upper() if c.isalpha())
    total = 0.0
    for crib, expected_positions in positional.items():
        c = crib.upper()
        if not c or c not in upper:
            continue
        starts = []
        idx = upper.find(c)
        while idx != -1:
            starts.append(idx)
            idx = upper.find(c, idx + 1)
        for occ in starts:
            if expected_positions:
                dist = min(abs(occ - ep) for ep in expected_positions)
                if dist <= window:
                    total += max(0.0, (8 * len(c) - dist))
    return total


def combined_plaintext_score(text: str) -> float:
    chi = chi_square_stat(text)
    bi = bigram_score(text)
    tri = trigram_score(text)
    quad = quadgram_score(text) if QUADGRAMS else 0.0
    return bi + tri + quad - 0.05 * chi + crib_bonus(text)


@lru_cache(maxsize=10000)
def combined_plaintext_score_cached(text: str) -> float:
    return combined_plaintext_score(text)


def berlin_clock_pattern_validator(text: str) -> dict[str, bool | int]:
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
        'pattern_bonus': int(has_berlin and has_clock and order_ok),
    }


def combined_plaintext_score_extended(text: str) -> float:
    base = combined_plaintext_score(text)
    pattern = berlin_clock_pattern_validator(text)
    pos_score = positional_letter_deviation_score(text)
    return base + 25.0 * pattern['pattern_bonus'] + 30.0 * pos_score


def wordlist_hit_rate(text: str, min_len: int = 3, max_len: int = 8) -> float:
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


def baseline_stats(text: str) -> dict[str, float]:
    stats = {
        'chi_square': chi_square_stat(text),
        'bigram_score': bigram_score(text),
        'trigram_score': trigram_score(text),
        'quadgram_score': quadgram_score(text) if QUADGRAMS else 0.0,
        'crib_bonus': crib_bonus(text),
        'rarity_weighted_crib_bonus': rarity_weighted_crib_bonus(text),
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
    return {seg: combined_plaintext_score(seg) for seg in segments}


def index_of_coincidence(text: str) -> float:
    letters = [c for c in text.upper() if c.isalpha()]
    n = len(letters)
    if n < 2:
        return 0.0
    counts = Counter(letters)
    num = sum(v * (v - 1) for v in counts.values())
    den = n * (n - 1)
    return num / den if den else 0.0


def vowel_ratio(text: str) -> float:
    letters = [c for c in text.upper() if c.isalpha()]
    if not letters:
        return 0.0
    vowels = set('AEIOUY')
    vcount = sum(1 for c in letters if c in vowels)
    return vcount / len(letters)


def letter_coverage(text: str) -> float:
    letters = {c for c in text.upper() if c.isalpha()}
    return len(letters) / 26.0


def letter_entropy(text: str) -> float:
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
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0
    bigrams = [seq[i : i + 2] for i in range(len(seq) - 2 + 1)]
    counts = Counter(bigrams)
    repeats = sum(v for v in counts.values() if v > 1)
    return repeats / len(bigrams)


def positional_letter_deviation_score(text: str, period: int = 5) -> float:
    letters = [c for c in text.upper() if c.isalpha()]
    n = len(letters)
    if n < period * 2:
        return 0.0
    buckets: list[list[str]] = [[] for _ in range(period)]
    for i, c in enumerate(letters):
        buckets[i % period].append(c)
    partials: list[float] = []
    for bucket in buckets:
        bn = len(bucket)
        if bn == 0:
            continue
        counts = Counter(bucket)
        chi = 0.0
        for letter, exp_pct in LETTER_FREQ.items():
            expected = exp_pct * bn / 100.0
            if expected <= 0:
                continue
            obs = counts.get(letter, 0)
            chi += (obs - expected) ** 2 / expected
        partials.append(1.0 / (1.0 + chi))
    if not partials:
        return 0.0
    return sum(partials) / len(partials)


def combined_plaintext_score_with_positions(text: str, positional: dict[str, Sequence[int]], window: int = 5) -> float:
    base = combined_plaintext_score(text)
    pos_bonus = positional_crib_bonus(text, positional, window)
    return base + pos_bonus


def load_cribs_from_file(path: str | Path) -> list[str]:
    try:
        p = Path(path)
    except (TypeError, ValueError):
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
    except (OSError, UnicodeDecodeError):
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


def composite_score_with_stage_analysis(
    stage1_plaintext: str,
    stage2_plaintext: str,
    stage1_score: float,
    stage2_score: float,
    stage1_weight: float = 0.3,
    stage2_weight: float = 0.7,
) -> dict:
    """Analyze composite hypothesis results with stage-aware bonuses.

    Awards bonuses for signs of partial decryption progress in intermediate
    results (stage1). This helps identify promising composite cipher approaches
    even when neither stage alone produces readable text.

    Args:
        stage1_plaintext: Intermediate plaintext after first decryption stage
        stage2_plaintext: Final plaintext after second decryption stage
        stage1_score: Score of stage1 plaintext
        stage2_score: Score of stage2 plaintext
        stage1_weight: Weight for stage1 in final score (default: 0.3)
        stage2_weight: Weight for stage2 in final score (default: 0.7)

    Returns:
        Dictionary with:
            - final_score: Weighted combination of stage scores + bonuses
            - stage1_ioc: Index of coincidence for stage1
            - stage2_ioc: Index of coincidence for stage2
            - ioc_improvement: Change in IOC from stage1 to stage2
            - stage1_partial_words: Count of 3+ letter word fragments in stage1
            - stage2_partial_words: Count of 3+ letter word fragments in stage2
            - english_freq_convergence: How much closer stage2 is to English
            - total_bonus: Sum of all bonuses applied
    """
    import re

    stage1_ioc = index_of_coincidence(stage1_plaintext)
    stage2_ioc = index_of_coincidence(stage2_plaintext)

    english_ioc = 0.067
    stage1_ioc_distance = abs(stage1_ioc - english_ioc)
    stage2_ioc_distance = abs(stage2_ioc - english_ioc)
    ioc_improvement = stage1_ioc_distance - stage2_ioc_distance

    ioc_bonus = min(10.0, max(0.0, ioc_improvement * 150))

    def count_partial_words(text: str, min_length: int = 3) -> int:
        words = re.findall(r'[A-Z]{' + str(min_length) + r',}', text.upper())
        return len(words)

    stage1_words = count_partial_words(stage1_plaintext)
    stage2_words = count_partial_words(stage2_plaintext)

    word_improvement = stage2_words - stage1_words
    word_bonus = min(5.0, max(0.0, word_improvement * 0.5))

    stage1_freq_dist = chi_square_stat(stage1_plaintext)
    stage2_freq_dist = chi_square_stat(stage2_plaintext)
    freq_convergence = stage1_freq_dist - stage2_freq_dist

    freq_bonus = min(8.0, max(0.0, freq_convergence * 0.01))

    total_bonus = ioc_bonus + word_bonus + freq_bonus

    base_score = (stage1_weight * stage1_score) + (stage2_weight * stage2_score)
    final_score = base_score + total_bonus

    return {
        'final_score': final_score,
        'base_score': base_score,
        'stage1_score': stage1_score,
        'stage2_score': stage2_score,
        'stage1_ioc': stage1_ioc,
        'stage2_ioc': stage2_ioc,
        'ioc_improvement': ioc_improvement,
        'ioc_bonus': ioc_bonus,
        'stage1_partial_words': stage1_words,
        'stage2_partial_words': stage2_words,
        'word_improvement': word_improvement,
        'word_bonus': word_bonus,
        'english_freq_convergence': freq_convergence,
        'freq_bonus': freq_bonus,
        'total_bonus': total_bonus,
        'stage1_weight': stage1_weight,
        'stage2_weight': stage2_weight,
    }


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
    'rarity_weighted_crib_bonus',
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
    'positional_letter_deviation_score',
    'load_cribs_from_file',
    'combined_plaintext_score_with_external_cribs',
    'composite_score_with_stage_analysis',
]
