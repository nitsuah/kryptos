"""Enhanced scoring functions with linguistic analysis.

Adds syllable structure, word boundary detection, and phonetic rules
to improve plaintext quality assessment. These features help distinguish
real English text from high-scoring gibberish.
"""

from __future__ import annotations

# Minimum text length for reliable syllable pattern analysis
# Shorter texts lack sufficient context for meaningful syllable structure assessment
MIN_TEXT_LENGTH_FOR_SYLLABLE_ANALYSIS = 3

# Common English 2-3 letter words
COMMON_WORDS = {
    # 2-letter
    'AM',
    'AN',
    'AS',
    'AT',
    'BE',
    'BY',
    'DO',
    'GO',
    'HE',
    'IF',
    'IN',
    'IS',
    'IT',
    'ME',
    'MY',
    'NO',
    'OF',
    'ON',
    'OR',
    'SO',
    'TO',
    'UP',
    'US',
    'WE',
    # 3-letter
    'THE',
    'AND',
    'FOR',
    'ARE',
    'BUT',
    'NOT',
    'YOU',
    'ALL',
    'CAN',
    'HAD',
    'HER',
    'WAS',
    'ONE',
    'OUR',
    'OUT',
    'DAY',
    'GET',
    'HAS',
    'HIM',
    'HIS',
    'HOW',
    'ITS',
    'MAY',
    'NEW',
    'NOW',
    'OLD',
    'SEE',
    'TWO',
    'WAY',
    'WHO',
    'BOY',
    'DID',
    'LET',
    'PUT',
    'SAY',
    'SHE',
    'TOO',
    'USE',
}

# Vowels and consonants
VOWELS = set('AEIOUY')
CONSONANTS = set('BCDFGHJKLMNPQRSTVWXZ')

# Impossible/rare English consonant clusters
BAD_CLUSTERS = {
    'BK',
    'BX',
    'CJ',
    'CQ',
    'CX',
    'DX',
    'FQ',
    'FX',
    'FZ',
    'GQ',
    'GX',
    'HX',
    'JB',
    'JD',
    'JF',
    'JG',
    'JK',
    'JL',
    'JM',
    'JN',
    'JP',
    'JQ',
    'JR',
    'JS',
    'JT',
    'JV',
    'JW',
    'JX',
    'JZ',
    'KQ',
    'KX',
    'KZ',
    'MX',
    'PX',
    'PZ',
    'QB',
    'QC',
    'QD',
    'QF',
    'QG',
    'QH',
    'QJ',
    'QK',
    'QL',
    'QM',
    'QN',
    'QP',
    'QQ',
    'QR',
    'QS',
    'QT',
    'QV',
    'QW',
    'QX',
    'QY',
    'QZ',
    'VB',
    'VF',
    'VH',
    'VJ',
    'VK',
    'VM',
    'VP',
    'VQ',
    'VT',
    'VV',
    'VW',
    'VX',
    'WQ',
    'WX',
    'XB',
    'XC',
    'XD',
    'XF',
    'XG',
    'XJ',
    'XK',
    'XQ',
    'XV',
    'XZ',
    'ZB',
    'ZC',
    'ZD',
    'ZF',
    'ZG',
    'ZH',
    'ZJ',
    'ZK',
    'ZM',
    'ZN',
    'ZP',
    'ZQ',
    'ZR',
    'ZS',
    'ZV',
    'ZW',
    'ZX',
}

# Common English digraphs (bonus for having these)
GOOD_DIGRAPHS = {
    'TH': 3.0,
    'HE': 2.5,
    'IN': 2.0,
    'ER': 2.0,
    'AN': 2.0,
    'RE': 1.8,
    'ON': 1.8,
    'AT': 1.5,
    'EN': 1.5,
    'ND': 1.5,
    'TI': 1.3,
    'ES': 1.3,
    'OR': 1.3,
    'TE': 1.3,
    'OF': 1.2,
    'ED': 1.2,
    'IS': 1.2,
    'IT': 1.2,
    'AL': 1.2,
    'AR': 1.2,
    'ST': 1.2,
}


def syllable_structure_score(text: str) -> float:
    """Score based on valid English syllable patterns (CV, CVC, CVCC, etc.).

    Returns:
        Score bonus (0-100) based on prevalence of valid syllable patterns.
        Higher score means more English-like syllable structure.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < MIN_TEXT_LENGTH_FOR_SYLLABLE_ANALYSIS:
        return 0.0

    # Pattern matching for syllable structures
    # C = consonant, V = vowel
    # Common patterns: CV, CVC, VC, CCV, CCVC, CVCC, etc.

    valid_patterns = 0
    total_windows = 0

    # Sliding window analysis
    for length in [2, 3, 4, 5]:  # Check 2-5 char windows
        if length > len(seq):
            break

        for i in range(len(seq) - length + 1):
            window = seq[i : i + length]
            total_windows += 1

            # Convert to C/V pattern
            pattern = ''.join('V' if c in VOWELS else 'C' for c in window)

            # Valid patterns (not exhaustive, but common ones)
            if pattern in {
                'CV',
                'VC',
                'CVC',
                'VCV',
                'CVCV',
                'CCV',
                'VCC',
                'CCVC',
                'CVCC',
                'CCVCC',
                'CCCVC',  # like 'stra-'
            }:
                valid_patterns += 1

    if total_windows == 0:
        return 0.0

    ratio = valid_patterns / total_windows
    return ratio * 100.0  # Scale to 0-100


def word_boundary_score(text: str) -> float:
    """Score based on detection of common 2-3 letter words.

    Scans for common short words that indicate word boundaries.
    Returns bonus based on density of recognized words.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0

    found_words = 0
    total_positions = len(seq)

    # Check for 2-letter words
    for i in range(len(seq) - 1):
        if seq[i : i + 2] in COMMON_WORDS:
            found_words += 1

    # Check for 3-letter words
    for i in range(len(seq) - 2):
        if seq[i : i + 3] in COMMON_WORDS:
            found_words += 2  # Weight 3-letter words more

    density = found_words / total_positions if total_positions > 0 else 0.0
    return density * 100.0  # Scale to 0-100


def phonetic_rules_score(text: str) -> float:
    """Score based on English phonotactic rules (valid sound combinations).

    Penalizes impossible consonant clusters and rewards good digraphs.
    Returns score adjustment (-50 to +50).
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0

    penalty = 0.0
    bonus = 0.0
    total_bigrams = len(seq) - 1

    for i in range(len(seq) - 1):
        bigram = seq[i : i + 2]

        # Penalize bad clusters
        if bigram in BAD_CLUSTERS:
            penalty += 5.0

        # Q must be followed by U
        if seq[i] == 'Q' and (i + 1 >= len(seq) or seq[i + 1] != 'U'):
            penalty += 10.0

        # Reward good digraphs
        if bigram in GOOD_DIGRAPHS:
            bonus += GOOD_DIGRAPHS[bigram]

    # Normalize
    penalty_normalized = (penalty / total_bigrams) * 50.0 if total_bigrams > 0 else 0.0
    bonus_normalized = (bonus / total_bigrams) * 50.0 if total_bigrams > 0 else 0.0

    return min(50.0, bonus_normalized) - min(50.0, penalty_normalized)


def vowel_consonant_alternation_score(text: str) -> float:
    """Score based on natural vowel-consonant alternation patterns.

    English words typically alternate between vowels and consonants.
    Long runs of all-vowels or all-consonants are rare.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 3:
        return 0.0

    # Count runs of same type (V or C)
    runs = []
    current_run = 1
    prev_type = 'V' if seq[0] in VOWELS else 'C'

    for i in range(1, len(seq)):
        curr_type = 'V' if seq[i] in VOWELS else 'C'
        if curr_type == prev_type:
            current_run += 1
        else:
            runs.append(current_run)
            current_run = 1
            prev_type = curr_type

    runs.append(current_run)

    # Penalize long runs (>4 is very unusual)
    penalty = sum(max(0, run - 4) * 5.0 for run in runs)

    # Average run length (ideal is ~1.5-2.5)
    avg_run = sum(runs) / len(runs) if runs else 0.0
    ideal_deviation = abs(avg_run - 2.0)

    score = 50.0 - penalty - (ideal_deviation * 10.0)
    return max(0.0, min(50.0, score))


def position_specific_frequency_score(text: str) -> float:
    """Score based on position-specific letter frequencies.

    English has position-dependent letter distributions:
    - E more common at word ends
    - S more common at word starts and ends
    - Q rare overall, only appears with U
    - X, Z more common at word ends
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 5:
        return 0.0

    # Simple heuristic: check first/last chars of 3-5 letter windows
    score = 0.0
    total = 0

    for length in [3, 4, 5]:
        if length > len(seq):
            break

        for i in range(len(seq) - length + 1):
            window = seq[i : i + length]
            first = window[0]
            last = window[-1]
            total += 1

            # Common word-initial letters: T, A, O, S, W
            if first in 'TAOSW':
                score += 1.0

            # Common word-final letters: E, S, T, D, N
            if last in 'ESTDN':
                score += 1.0

            # Rare word-initial: X, Q, Z
            if first in 'XQZ':
                score -= 2.0

    return (score / total) * 50.0 if total > 0 else 0.0


def combined_linguistic_score(text: str) -> float:
    """Combine all linguistic scoring features into a single bonus.

    Returns:
        Score adjustment to add to base plaintext score (-100 to +200).
        Positive values indicate high linguistic quality.
    """
    syllable = syllable_structure_score(text)  # 0-100
    word_boundary = word_boundary_score(text)  # 0-100
    phonetic = phonetic_rules_score(text)  # -50 to +50
    vc_alternation = vowel_consonant_alternation_score(text)  # 0-50
    position_freq = position_specific_frequency_score(text)  # 0-50

    # Weighted combination
    total = syllable * 0.5 + word_boundary * 0.8 + phonetic * 0.6 + vc_alternation * 0.4 + position_freq * 0.3

    return total


def enhanced_combined_score(text: str) -> float:
    """Enhanced scoring combining base metrics + linguistic analysis.

    This is the new recommended scoring function for hypothesis testing.
    Imports from base scoring module and adds linguistic bonuses.
    """
    from .scoring import combined_plaintext_score

    base_score = combined_plaintext_score(text)
    linguistic_bonus = combined_linguistic_score(text)

    return base_score + linguistic_bonus


# --- Diagnostic functions ---


def linguistic_diagnostics(text: str) -> dict[str, float]:
    """Return all linguistic scores for analysis/debugging."""
    return {
        'syllable_structure': syllable_structure_score(text),
        'word_boundary': word_boundary_score(text),
        'phonetic_rules': phonetic_rules_score(text),
        'vc_alternation': vowel_consonant_alternation_score(text),
        'position_frequency': position_specific_frequency_score(text),
        'combined_linguistic': combined_linguistic_score(text),
    }
