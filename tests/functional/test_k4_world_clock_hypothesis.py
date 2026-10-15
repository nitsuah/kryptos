"""Tests for the deterministic six-segment World Clock diagnostic."""

import json

import pytest

from kryptos.k4.world_clock_hypothesis import (
    CIPHERTEXT,
    EXPECTED_SEGMENT_LENGTHS,
    analyze_world_clock_hypothesis,
    split_on_delimiter,
    shuffled_delimiter_control,
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
    assert report["shuffled_control"]["sample_size"] == 5000
    assert "not a p-value" in report["shuffled_control"]["interpretation"]
    assert report["ciphertext_length"] == 97


def test_historical_count_mismatch_is_explicit_not_silently_resolved():
    report = analyze_world_clock_hypothesis()
    baseline = report["historical_baseline"]
    assert baseline["original_city_names"] == 80
    assert baseline["segment_letters_total"] == 92
    assert baseline["difference_letters_minus_city_names"] == 12
    assert "do not map one-to-one" in baseline["interpretation"]



def test_shuffled_control_is_reproducible_and_preserves_delimiter_count():
    stream = transform_through_keyed_alphabet()
    first = shuffled_delimiter_control(stream, sample_size=200, seed=123)
    second = shuffled_delimiter_control(stream, sample_size=200, seed=123)

    assert first == second
    assert first["sample_size"] == 200
    assert first["seed"] == 123
    assert first["delimiter_count_preserved"] == stream.count("X") == 5
    assert first["character_multiset_preserved"] is True
    assert 0 <= first["exact_signature_hits"] <= 200
    assert first["observed_hit_rate"] == first["exact_signature_hits"] / 200
    assert "selection" in first["interpretation"]


def test_shuffled_control_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="at least 1"):
        shuffled_delimiter_control("ABC", sample_size=0)
    with pytest.raises(ValueError, match="uppercase A-Z"):
        shuffled_delimiter_control("abc")


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
