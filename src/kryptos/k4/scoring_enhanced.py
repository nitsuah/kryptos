"""Enhanced scoring functions with linguistic analysis.

Adds syllable structure, word boundary detection, and phonetic rules
to improve plaintext quality assessment. These features help distinguish
real English text from high-scoring gibberish.
"""

from __future__ import annotations

MIN_TEXT_LENGTH_FOR_SYLLABLE_ANALYSIS = 3

COMMON_WORDS = {
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

VOWELS = set('AEIOUY')
CONSONANTS = set('BCDFGHJKLMNPQRSTVWXZ')

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
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < MIN_TEXT_LENGTH_FOR_SYLLABLE_ANALYSIS:
        return 0.0

    valid_patterns = 0
    total_windows = 0

    for length in [2, 3, 4, 5]:
        if length > len(seq):
            break

        for i in range(len(seq) - length + 1):
            window = seq[i : i + length]
            total_windows += 1

            pattern = ''.join('V' if c in VOWELS else 'C' for c in window)

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
                'CCCVC',
            }:
                valid_patterns += 1

    if total_windows == 0:
        return 0.0

    ratio = valid_patterns / total_windows
    return ratio * 100.0


def word_boundary_score(text: str) -> float:
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0

    found_words = 0
    total_positions = len(seq)

    for i in range(len(seq) - 1):
        if seq[i : i + 2] in COMMON_WORDS:
            found_words += 1

    for i in range(len(seq) - 2):
        if seq[i : i + 3] in COMMON_WORDS:
            found_words += 2

    density = found_words / total_positions if total_positions > 0 else 0.0
    return density * 100.0


def phonetic_rules_score(text: str) -> float:
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 2:
        return 0.0

    penalty = 0.0
    bonus = 0.0
    total_bigrams = len(seq) - 1

    for i in range(len(seq) - 1):
        bigram = seq[i : i + 2]

        if bigram in BAD_CLUSTERS:
            penalty += 5.0

        if seq[i] == 'Q' and (i + 1 >= len(seq) or seq[i + 1] != 'U'):
            penalty += 10.0

        if bigram in GOOD_DIGRAPHS:
            bonus += GOOD_DIGRAPHS[bigram]

    penalty_normalized = (penalty / total_bigrams) * 50.0 if total_bigrams > 0 else 0.0
    bonus_normalized = (bonus / total_bigrams) * 50.0 if total_bigrams > 0 else 0.0

    return min(50.0, bonus_normalized) - min(50.0, penalty_normalized)


def vowel_consonant_alternation_score(text: str) -> float:
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 3:
        return 0.0

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

    penalty = sum(max(0, run - 4) * 5.0 for run in runs)

    avg_run = sum(runs) / len(runs) if runs else 0.0
    ideal_deviation = abs(avg_run - 2.0)

    score = 50.0 - penalty - (ideal_deviation * 10.0)
    return max(0.0, min(50.0, score))


def position_specific_frequency_score(text: str) -> float:
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if len(seq) < 5:
        return 0.0

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

            if first in 'TAOSW':
                score += 1.0

            if last in 'ESTDN':
                score += 1.0

            if first in 'XQZ':
                score -= 2.0

    return (score / total) * 50.0 if total > 0 else 0.0


def combined_linguistic_score(text: str) -> float:
    syllable = syllable_structure_score(text)
    word_boundary = word_boundary_score(text)
    phonetic = phonetic_rules_score(text)
    vc_alternation = vowel_consonant_alternation_score(text)
    position_freq = position_specific_frequency_score(text)

    total = syllable * 0.5 + word_boundary * 0.8 + phonetic * 0.6 + vc_alternation * 0.4 + position_freq * 0.3

    return total


def enhanced_combined_score(text: str) -> float:
    from .scoring import combined_plaintext_score

    base_score = combined_plaintext_score(text)
    linguistic_bonus = combined_linguistic_score(text)

    return base_score + linguistic_bonus


def linguistic_diagnostics(text: str) -> dict[str, float]:
    return {
        'syllable_structure': syllable_structure_score(text),
        'word_boundary': word_boundary_score(text),
        'phonetic_rules': phonetic_rules_score(text),
        'vc_alternation': vowel_consonant_alternation_score(text),
        'position_frequency': position_specific_frequency_score(text),
        'combined_linguistic': combined_linguistic_score(text),
    }
