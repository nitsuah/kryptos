import math

import pytest

from kryptos.k4 import scoring


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
    # extended score includes pattern bonus (25.0) PLUS positional letter deviation component (30 * pos_score)
    pos_score = scoring.positional_letter_deviation_score(text)
    expected = base + 25.0 + 30.0 * pos_score
    assert math.isclose(ext, expected, rel_tol=1e-9, abs_tol=1e-12)


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


def test_chi_square_and_cached_score_and_segment_scores():
    # chi-square for normal text should be finite
    chi = scoring.chi_square_stat('THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
    assert math.isfinite(chi)

    # cached combined score should match uncached and be deterministic
    s1 = scoring.combined_plaintext_score('SOME PLAINTEXT')
    s2 = scoring.combined_plaintext_score_cached('SOME PLAINTEXT')
    s3 = scoring.combined_plaintext_score_cached('SOME PLAINTEXT')
    assert math.isclose(s1, s2, rel_tol=1e-9)
    assert s2 == s3

    # segment scores
    segs = ['THE', 'QUICK', 'BROWN']
    seg_scores = scoring.segment_plaintext_scores(segs)
    assert set(segs) == set(seg_scores.keys())
    for v in seg_scores.values():
        assert isinstance(v, float)


def test_baseline_stats_and_letter_metrics():
    txt = 'THE QUICK BROWN FOX'
    stats = scoring.baseline_stats(txt)
    # basic expected keys
    expected_keys = {
        'chi_square',
        'bigram_score',
        'trigram_score',
        'quadgram_score',
        'crib_bonus',
        'rarity_weighted_crib_bonus',
        'combined_score',
    }
    assert expected_keys.issubset(set(stats.keys()))
    # numeric values
    for k in expected_keys:
        assert isinstance(stats[k], float)

    # letter entropy / coverage / index
    ent = scoring.letter_entropy('AAAA')
    assert ent == pytest.approx(0.0)
    cov = scoring.letter_coverage('ABC')
    assert cov <= 1.0 and cov >= 0.0
    ic = scoring.index_of_coincidence('AAA')
    assert isinstance(ic, float)
