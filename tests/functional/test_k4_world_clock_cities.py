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
        assert offsets["world_clock_city_count_mod24"] == wcc.TOTAL_CITY_COUNT % wcc.TOTAL_SEGMENTS
        assert offsets["world_clock_plate_entries_mod24"] == wcc.TOTAL_PLATE_ENTRIES % wcc.TOTAL_SEGMENTS
        for v in offsets.values():
            assert 0 <= v < wcc.TOTAL_SEGMENTS

    def test_city_count_and_plate_entries_differ_by_one(self):
        # 146 city names + 1 distinct International Date Line marker.
        assert wcc.TOTAL_PLATE_ENTRIES == wcc.TOTAL_CITY_COUNT + 1


class TestWorldClockSectorOffsets:
    def test_kamtschatka_hour_matches_segment_table(self):
        offsets = wcc.world_clock_sector_offsets()
        assert offsets["kamtschatka_hour_mod24"] == wcc.WORLD_CLOCK_SEGMENT_HOUR["KAMTSCHATKA"] % wcc.TOTAL_SEGMENTS

    def test_all_offsets_in_range(self):
        for v in wcc.world_clock_sector_offsets().values():
            assert 0 <= v < wcc.TOTAL_SEGMENTS

    def test_segment_hours_are_distinct_and_sequential(self):
        # 15-24 in order, confirming the sourced ring position of each
        # segment (two of them genuinely blank, not a gap in the table).
        hours = wcc.WORLD_CLOCK_SEGMENT_HOUR
        assert hours["KAMTSCHATKA"] == hours["MAGADAN_SACHALIN"] + 1
        assert hours["KAPDESCHNEW"] == hours["KAMTSCHATKA"] + 1
        assert hours["HONOLULU"] == hours["KAPDESCHNEW"] + 1


class TestRunWorldClockSectorSweep:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "sector_null.json"
        summary = wcc.run_world_clock_sector_sweep(null_artifact_path=str(artifact))
        assert summary["status"] == "null_result"
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["run_params"]["rotation_offsets"] == list(wcc.world_clock_sector_offsets().values())


class TestRunWorldClockCitySweep:
    def test_null_result_artifact(self, tmp_path):
        # Small scope for a fast structural check -- the full 130-city
        # production sweep (140,400 candidates) was already run for
        # real and is recorded in K4_WORLD_CLOCK_CITIES_NULL.json /
        # docs/analysis/K4_ACTIVE_RESEARCH.md, not re-run on every test pass.
        artifact = tmp_path / "null.json"
        summary = wcc.run_world_clock_city_sweep(grid_sizes=[7], max_perms_per_grid=5, null_artifact_path=str(artifact))
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
