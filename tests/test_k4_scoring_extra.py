import math

import pytest

from k4 import scoring


def test_berlin_clock_validator_variants():
    # neither
    r = scoring.berlin_clock_pattern_validator('NO MATCH HERE')
    assert r['has_berlin'] is False
    assert r['has_clock'] is False
    assert r['berlin_before_clock'] is False
    assert r['pattern_bonus'] == 0

    # only BERLIN
    r = scoring.berlin_clock_pattern_validator('...BERLIN...')
    assert r['has_berlin'] is True
    assert r['has_clock'] is False
    assert r['pattern_bonus'] == 0

    # only CLOCK
    r = scoring.berlin_clock_pattern_validator('...CLOCK...')
    assert r['has_berlin'] is False
    assert r['has_clock'] is True
    assert r['pattern_bonus'] == 0

    # both but wrong order
    r = scoring.berlin_clock_pattern_validator('CLOCK THEN BERLIN')
    assert r['has_berlin'] is True
    assert r['has_clock'] is True
    assert r['berlin_before_clock'] is False
    assert r['pattern_bonus'] == 0

    # correct order
    s = 'XXXBERLINYYYCLOCKZZZ'
    r = scoring.berlin_clock_pattern_validator(s)
    assert r['has_berlin'] is True and r['has_clock'] is True
    assert r['berlin_before_clock'] is True
    assert r['pattern_bonus'] == 1


def test_combined_extended_includes_pattern_bonus():
    text = 'SOMETHINGBERLINANDCLOCKHERE'
    base = scoring.combined_plaintext_score(text)
    ext = scoring.combined_plaintext_score_extended(text)
    # pattern present and in order => bonus of exactly 25.0
    assert math.isclose(ext, base + 25.0, rel_tol=1e-9, abs_tol=1e-12)


def test_positional_crib_bonus_and_combined():
    text = 'XXXXSECRETYYYY'
    # SECRET starts at index 4
    base = scoring.combined_plaintext_score(text)
    pos_map = {'SECRET': [4]}
    pos_bonus = scoring.positional_crib_bonus(text, pos_map)
    # 8 * len('SECRET') == 8*6 == 48
    assert pos_bonus == 48
    combined = scoring.combined_plaintext_score_with_positions(text, pos_map)
    assert math.isclose(combined, base + 48, rel_tol=1e-9)


def test_positional_crib_no_positional_returns_zero():
    assert scoring.positional_crib_bonus('ANYTEXT', {}) == 0.0


def test_wordlist_hit_rate_bounds_and_hit():
    # too short
    assert scoring.wordlist_hit_rate('AB') == 0.0
    # 'THE' is in fallback WORDLIST -> should produce hit rate 1.0 for exact match
    assert scoring.wordlist_hit_rate('THE') == pytest.approx(1.0)


def test_trigram_entropy_edge_and_nonzero():
    # too short
    assert scoring.trigram_entropy('AA') == 0.0
    # repeated trigram -> entropy 0
    assert scoring.trigram_entropy('AAAAAA') == pytest.approx(0.0)
    # unique trigrams -> entropy equals 2.0 for 4 unique trigrams
    assert scoring.trigram_entropy('ABCDEF') == pytest.approx(2.0)


def test_bigram_gap_variance_zero_and_nonzero():
    # short -> zero
    assert scoring.bigram_gap_variance('ABC') == 0.0
    # repeating with equal gaps -> variance 0
    assert scoring.bigram_gap_variance('ABABAB') == pytest.approx(0.0)
    # gaps vary; assert non-negative and less than a small bound
    val = scoring.bigram_gap_variance('ABCDABDAB')
    assert val >= 0.0
    assert val < 1.0


def test_repeating_bigram_fraction():
    # ABABAB => bigrams: AB,BA,AB,BA,AB -> repeats should equal total bigrams => fraction 1.0
    assert scoring.repeating_bigram_fraction('ABABAB') == pytest.approx(1.0)
