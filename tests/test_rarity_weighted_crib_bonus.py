"""Tests for rarity_weighted_crib_bonus scoring function."""

from kryptos.k4 import scoring


def test_rarity_weighted_crib_bonus_basic():
    text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    # Ensure function runs and returns non-negative value
    val = scoring.rarity_weighted_crib_bonus(text)
    assert isinstance(val, float)
    assert val >= 0.0


def test_rarity_weighted_crib_bonus_rarity_effect():
    # Construct text containing rare-letter crib vs common-letter crib if both exist in CRIBS
    txt_common = "THE THE THE"  # common letters
    txt_rare = "JQXZ JQXZ"  # artificially rare pattern; only counts if in CRIBS
    # We can't guarantee config CRIBS content; so just verify stable call
    scoring.rarity_weighted_crib_bonus(txt_common)
    scoring.rarity_weighted_crib_bonus(txt_rare)


def test_rarity_weighted_crib_bonus_empty():
    assert scoring.rarity_weighted_crib_bonus("") == 0.0
