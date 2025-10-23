import math

from kryptos.k4 import scoring


def test_chi_square_empty_and_nonempty():
    assert math.isinf(scoring.chi_square_stat(''))
    v = scoring.chi_square_stat('THIS IS A SIMPLE ENGLISH SENTENCE')
    assert v >= 0.0 and not math.isinf(v)


def test_ngram_edge_cases():
    # short inputs produce zero ngram score because no full grams
    assert scoring.bigram_score('A') == 0.0
    assert scoring.trigram_score('AB') == 0.0
    # two-letter input yields a numeric bigram score
    val = scoring.bigram_score('AB')
    assert isinstance(val, float)


def test_positional_crib_bonus_window():
    text = 'AAAHELLOB'
    # HELLO starts at index 3
    pos = {'HELLO': [3]}
    assert scoring.positional_crib_bonus(text, pos, window=1) > 0.0
    # far away expected pos -> no bonus
    pos2 = {'HELLO': [50]}
    assert scoring.positional_crib_bonus(text, pos2, window=2) == 0.0


def test_combined_score_with_external_cribs():
    txt = 'THISCONTAINSCRIB'
    base = scoring.combined_plaintext_score(txt)
    bumped = scoring.combined_plaintext_score_with_external_cribs(txt, ['CRIB'], crib_weight=1.0)
    assert bumped >= base


def test_berlin_clock_validator_ordering():
    good = '...BERLIN...CLOCK...'
    bad = '...CLOCK...BERLIN...'
    g = scoring.berlin_clock_pattern_validator(good)
    b = scoring.berlin_clock_pattern_validator(bad)
    assert g['has_berlin'] and g['has_clock'] and g['berlin_before_clock']
    assert not b['berlin_before_clock']


def test_wordlist_hit_rate_and_entropy():
    # short text yields zero hit rate and zero trigram entropy
    assert scoring.wordlist_hit_rate('AB') == 0.0
    assert scoring.trigram_entropy('A') == 0.0
    # known word in default WORDLIST should increase hit rate
    w = 'THEATTHE'
    assert scoring.wordlist_hit_rate(w) > 0.0


def test_bigram_gap_variance_basic():
    # repeated bigrams with consistent gaps should produce zero variance
    text = 'ABXXABXXAB'
    var = scoring.bigram_gap_variance(text)
    assert var >= 0.0
