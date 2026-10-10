"""Tests for the provisional, attributed 2017 World Clock face transcription."""

from __future__ import annotations

import pytest

from kryptos.k4.world_clock_faces_2017 import (
    WORLD_CLOCK_FACES_2017,
    face_labels,
    ordered_face_labels,
)


def test_transcription_keeps_reported_order_on_each_face():
    assert face_labels("+1", "top")[:3] == ("AMSTERDAM", "BERLIN", "BRUESSEL")
    assert face_labels("+1", "bottom")[:3] == ("OSLO", "KOPENHAGEN", "WIEN")
    assert face_labels("+12", "top") == ("KAMTSCHATKA",)


def test_unknown_and_confirmed_blank_faces_are_distinct():
    assert face_labels("-12/-11/-10/-9", "top") is None
    assert face_labels("-8", "bottom") == ()
    assert face_labels("+11", "bottom") == ()


def test_ordered_face_labels_preserves_caller_order_and_skips_only_blanks():
    assert ordered_face_labels(("+12", "+11"), "top") == [
        "KAMTSCHATKA",
        "MAGADAN",
        "SACHALIN",
    ]
    assert ordered_face_labels(("+12", "-8"), "bottom") == [
        "DATUMSGRENZE",
        "WELLINGTON",
    ]


def test_ordered_face_labels_refuses_to_fill_unknown_faces():
    assert ordered_face_labels(("-8", "-12/-11/-10/-9", "+12"), "top") is None


def test_invalid_face_requests_are_rejected():
    with pytest.raises(ValueError, match="unknown transcribed UTC offset"):
        face_labels("+13", "top")
    with pytest.raises(ValueError, match="side must be"):
        face_labels("+1", "left")  # type: ignore[arg-type]


def test_face_map_has_both_sides_for_every_record():
    assert all(set(face) == {"top", "bottom"} for face in WORLD_CLOCK_FACES_2017.values())
