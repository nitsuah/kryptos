import random

from kryptos.k4.scoring import combined_plaintext_score_extended, positional_letter_deviation_score

ENGLISH_SAMPLE = (
    "THIS IS A SHORT ENGLISH TEXT BLOCK WITH SOME COMMON WORDS LIKE THE AND CLOCK AND BERLIN TO TRIGGER PATTERNS"
)

# Create a pseudo-random shuffled version preserving length and letters
_random_letters = [c for c in ENGLISH_SAMPLE.upper() if c.isalpha()]
random.seed(1234)
random.shuffle(_random_letters)
RANDOM_SAMPLE = ''.join(_random_letters)


def test_positional_letter_deviation_prefers_english_like_text():
    eng_score = positional_letter_deviation_score(ENGLISH_SAMPLE)
    rand_score = positional_letter_deviation_score(RANDOM_SAMPLE)
    # English-like should be strictly greater (allow some tolerance)
    assert eng_score > rand_score, (eng_score, rand_score)
    assert 0.0 <= eng_score <= 1.0
    assert 0.0 <= rand_score <= 1.0


def test_extended_score_includes_positional_component():
    base_rand = combined_plaintext_score_extended(RANDOM_SAMPLE)
    base_eng = combined_plaintext_score_extended(ENGLISH_SAMPLE)
    # Expect extended score to be higher for English sample
    assert base_eng > base_rand
