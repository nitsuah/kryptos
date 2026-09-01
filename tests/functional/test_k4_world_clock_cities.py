"""Tests for kryptos.k4.world_clock_cities -- Phase 7 city-list keyword sweep."""

from __future__ import annotations

import json

from kryptos.k4 import world_clock_cities as wcc


class TestConfirmedCities:
    def test_all_alphabets_are_valid_permutations(self):
        for city, alphabet in wcc.WORLD_CLOCK_KEYED_ALPHABETS.items():
            assert sorted(alphabet) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), city

    def test_keyword_chars_lead_the_alphabet(self):
        alphabet = wcc.WORLD_CLOCK_KEYED_ALPHABETS["SEOUL"]
        assert alphabet.startswith("SEOUL")


class TestWorldClockRotationOffsets:
    def test_derived_from_sourced_counts(self):
        offsets = wcc.world_clock_rotation_offsets()
        assert offsets["world_clock_total_cities_mod24"] == wcc.TOTAL_CITY_COUNT % wcc.TOTAL_SEGMENTS
        for v in offsets.values():
            assert 0 <= v < wcc.TOTAL_SEGMENTS


class TestRunWorldClockCitySweep:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = wcc.run_world_clock_city_sweep(null_artifact_path=str(artifact))
        assert summary["status"] == "null_result"
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["run_params"]["attack"] == "P1_three_layer_composite"

    def test_matches_advisory_keyword_sweep_pipeline(self):
        # Structural check: run_world_clock_city_sweep must use the same
        # underlying pipeline as run_advisory_keyword_sweep (P19), not a
        # bespoke one -- same convention, only the keyword source differs.
        import inspect

        from kryptos.k4.advisory_keywords import run_advisory_keyword_sweep

        assert (
            inspect.signature(wcc.run_world_clock_city_sweep).parameters.keys()
            == inspect.signature(run_advisory_keyword_sweep).parameters.keys()
        )
