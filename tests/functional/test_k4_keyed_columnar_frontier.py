"""Regression tests for clue-derived long-key columnar frontier."""

from __future__ import annotations

from kryptos.k4 import frontier_checks as fc
from kryptos.k4.crib_constraints import STANDARD, crib_letters
from kryptos.k4.keyed_columnar_frontier import (
    candidate_keywords,
    keyed_columnar_order,
    run_keyed_columnar_frontier,
)
from kryptos.k4.physical_grid import K4
from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

PLAIN_TEXT = "".join(fc.reconstruction_plain()[i] for i in range(97))


def _cribs_of(text: str) -> dict[int, str]:
    return {i: text[i] for i in crib_letters()}


def _vig(plaintext: str, key: list[int]) -> str:
    return "".join(STANDARD[(STANDARD.index(ch) + key[i % len(key)]) % 26] for i, ch in enumerate(plaintext))


def test_keyed_columnar_order_uses_stable_ties():
    assert keyed_columnar_order("BALLOON") == (1, 0, 2, 3, 6, 4, 5)


def test_default_candidates_are_bounded_and_include_composite_clock_keys():
    candidates = candidate_keywords(city_names=["NISCHNIJ NOWGOROD", "BERLIN"])
    assert "NISCHNIJNOWGOROD" in candidates
    assert "NISCHNIJNOWGORODPALIMPSEST" in candidates
    assert "PALIMPSESTNISCHNIJNOWGOROD" in candidates
    assert all(15 <= len(word) <= 26 for word in candidates)
    assert "BERLIN" not in candidates


def test_planted_long_keyed_columnar_solution_is_found():
    # NISCHNIJNOWGOROD is a transcribed World Clock city label. The positive
    # control plants the exact stable alphabetical column order derived from it.
    keyword = "NISCHNIJNOWGOROD"
    order = list(keyed_columnar_order(keyword))
    periodic_key = [11, 3, 20, 7, 15, 0, 22]
    substituted = _vig(PLAIN_TEXT, periodic_key)
    ciphertext = apply_columnar_permutation_encrypt(substituted, len(keyword), order)

    result = run_keyed_columnar_frontier(
        ciphertext,
        _cribs_of(PLAIN_TEXT),
        keywords=[keyword],
        alphabet_keywords=["KRYPTOS"],
        periods=[len(periodic_key)],
    )

    assert result["status"] == "hits"
    assert result["unique_column_orders"] == 1
    assert any(
        hit["family"] == "vigenere"
        and hit["layer_order"] == "sub_then_trans"
        and hit["period"] == len(periodic_key)
        and any(example["order"] == order for example in hit["examples"])
        for hit in result["hits"]
    )


def test_k4_has_no_match_in_this_finite_clue_derived_family():
    result = run_keyed_columnar_frontier(K4)
    assert result["status"] == "null_result"
    assert result["crib_letters"] == 24
    assert result["keyword_candidates"] > 0
    assert result["unique_column_orders"] > 0
    assert result["checks_run"] > 0
    assert result["hits"] == []
    assert "does not rule out arbitrary" in result["scope_note"]
