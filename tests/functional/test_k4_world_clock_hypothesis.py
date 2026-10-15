"""Tests for the deterministic six-segment World Clock diagnostic."""

import json

import pytest

from kryptos.k4.world_clock_hypothesis import (
    CIPHERTEXT,
    EXPECTED_SEGMENT_LENGTHS,
    analyze_world_clock_hypothesis,
    split_on_delimiter,
    transform_through_keyed_alphabet,
    write_world_clock_diagnostic,
)


def test_transform_reproduces_recorded_stream_and_delimiters():
    report = analyze_world_clock_hypothesis()
    assert report["transformed_stream"] == (
        "FIABVFYFNOVRIGFRPMIIXMRBWUUDBTNAGGFEXEUGQUGGLAZZXHEQARVKPHXPTMITCDWEESZMDAXNKAZYEQJKPNAVOVHVLAJHB"
    )
    assert report["delimiter_positions_zero_based"] == [20, 36, 48, 58, 74]
    assert report["segment_lengths"] == EXPECTED_SEGMENT_LENGTHS
    assert report["matches_recorded_segment_lengths"] is True
    assert report["rotation_control"]["tested_circular_offsets"] == 97
    assert report["rotation_control"]["offsets_matching_recorded_segment_lengths"] == [0]
    assert report["rotation_control"]["unique_segment_length_signatures"] == 97
    assert "not an independent significance test" in report["rotation_control"]["interpretation"]
    assert report["ciphertext_length"] == 97


def test_historical_count_mismatch_is_explicit_not_silently_resolved():
    report = analyze_world_clock_hypothesis()
    baseline = report["historical_baseline"]
    assert baseline["original_city_names"] == 80
    assert baseline["segment_letters_total"] == 92
    assert baseline["difference_letters_minus_city_names"] == 12
    assert "do not map one-to-one" in baseline["interpretation"]


def test_transform_rejects_empty_input_after_normalization():
    with pytest.raises(ValueError, match="at least one letter"):
        transform_through_keyed_alphabet("!? 123")


def test_split_requires_single_uppercase_delimiter():
    assert split_on_delimiter("ABXCDX") == ["AB", "CD", ""]
    with pytest.raises(ValueError, match="one uppercase"):
        split_on_delimiter("AB", "xx")


def test_execution_artifact_is_same_as_api_report(tmp_path):
    target = tmp_path / "runs" / "world_clock.json"
    written = write_world_clock_diagnostic(target)
    persisted = json.loads(target.read_text(encoding="utf-8"))
    assert persisted == written == analyze_world_clock_hypothesis(CIPHERTEXT)
