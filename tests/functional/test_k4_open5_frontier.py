from __future__ import annotations

import pytest

from kryptos.k4.open5_frontier import (
    align_crib_with_edits,
    bearing_seed_candidates,
    hill_partial_block_coverage,
    keyed_lookup_streams,
)


def test_edit_alignment_recovers_planted_inserted_ciphertext_symbol():
    matches = align_crib_with_edits("ABXCD", "ABCD", 0, max_insertions=1, max_deletions=0)
    assert any(
        item["insertions"] == 1
        and item["deletions"] == 0
        and item["alignment"] == ((0, 0), (1, 1), (3, 2), (4, 3))
        for item in matches
    )


def test_edit_alignment_recovers_planted_missing_ciphertext_symbol():
    matches = align_crib_with_edits("ACD", "ABCD", 0, max_insertions=0, max_deletions=1)
    assert any(item["deletions"] == 1 and item["matches"] == 3 for item in matches)


def test_edit_alignment_rejects_invalid_bounds():
    with pytest.raises(ValueError):
        align_crib_with_edits("ABC", "ABC", -1)


def test_hill_partial_block_report_never_claims_full_matrix_solution():
    report = hill_partial_block_coverage({21: "E", 22: "A", 23: "S", 24: "T"}, sizes=(6,))
    assert len(report[6]) == 6
    assert all(row["fully_known_plaintext_blocks"] == 0 for row in report[6])
    assert all("no matrix elimination performed" in row["status"] for row in report[6])


def test_per_letter_lookup_preserves_supplied_physical_order():
    result = keyed_lookup_streams(["BERLIN", "TOKYO"], 4, transforms=("first", "last", "length"))
    assert [item["stream"] for item in result] == ["BTBT", "NONO", "FEFE"]
    assert all(item["requires_confirmed_physical_order"] for item in result)


def test_bearing_seeds_are_named_and_modular_not_routes():
    result = bearing_seed_candidates([67.5], moduli=(26,))
    assert len(result) == 3
    assert {item["encoding"] for item in result} == {"degrees", "tenths", "hundredths"}
    assert all(item["route_assumption"] is False for item in result)
    assert {item["seed"] for item in result} == {16, 25}


def test_bearing_outside_range_rejected():
    with pytest.raises(ValueError):
        bearing_seed_candidates([360])
