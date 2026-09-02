"""Tests for kryptos.k4.solar_geometry -- Phase 7 shadow-angle primitives."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from kryptos.k4 import solar_geometry as sg


class TestTopperRotationAngle:
    def test_zero_at_reference(self):
        ref = datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert sg.topper_rotation_angle_deg(ref, ref) == 0.0

    def test_full_revolution_per_minute(self):
        ref = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        query = datetime(2024, 1, 1, 0, 0, 30, tzinfo=timezone.utc)
        assert sg.topper_rotation_angle_deg(query, ref) == pytest.approx(180.0)

    def test_whole_minutes_are_always_zero(self):
        ref = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        query = datetime(2024, 1, 1, 3, 17, 0, tzinfo=timezone.utc)  # 197 whole minutes later
        assert sg.topper_rotation_angle_deg(query, ref) == 0.0


class TestTopperShadowOffsets:
    def test_whole_minute_historical_pairs_are_vacuous(self):
        # Documents the actual finding: every *whole-minute* sourced
        # timestamp (i.e. excluding the two sub-minute-precision moments
        # in PRECISE_QUERY_MOMENTS) is co-phased with any other, since the
        # topper's 60s period means any two whole-minute moments always
        # produce angle 0.
        whole_minute = {k: v for k, v in sg.QUERY_MOMENTS.items() if k not in sg.PRECISE_QUERY_MOMENTS}
        for ref_dt in sg.REFERENCE_EPOCHS.values():
            for query_dt in whole_minute.values():
                assert sg.topper_rotation_angle_deg(query_dt, ref_dt) == 0.0

    def test_returns_full_24_value_range(self):
        offsets = sg.topper_shadow_offsets()
        assert sorted(offsets.values()) == list(range(24))
        assert len(offsets) == 24


class TestPreciseTopperShadowOffsets:
    def test_returns_nonzero_distinct_offsets(self):
        # Unlike the whole-minute case, these two sourced timestamps carry
        # genuine non-zero seconds (:40 and :54), so this must NOT be
        # vacuous -- verifies the actual motivation for this function.
        offsets = sg.precise_topper_shadow_offsets()
        assert len(offsets) == 2
        assert len(set(offsets.values())) == 2  # distinct, not all collapsed

    def test_matches_hand_computed_values(self):
        # 18:52:40 CET -> 40s past the minute -> 40/60*360 = 240deg -> round(240/360*24)=16
        # 19:00:54 CET -> 54s past the minute -> 54/60*360 = 324deg -> round(324/360*24)=22
        offsets = sg.precise_topper_shadow_offsets()
        assert offsets["topper_precise_berlin_wall_presser_start"] == 16
        assert offsets["topper_precise_berlin_wall_presser_end"] == 22

    def test_sourced_timestamps_have_nonzero_seconds(self):
        for dt in sg.PRECISE_QUERY_MOMENTS.values():
            assert dt.second != 0


class TestSolarPosition:
    def test_requires_timezone_aware_datetime(self):
        with pytest.raises(ValueError):
            sg.solar_position(0.0, 0.0, datetime(2024, 1, 1))

    def test_greenwich_summer_solstice_noon(self):
        # Known reference: elevation ~ 90 - lat + obliquity(23.44) at local
        # solar noon near the solstice, azimuth roughly due south (~180).
        r = sg.solar_position(51.5, 0.0, datetime(2024, 6, 21, 12, 0, 0, tzinfo=timezone.utc))
        assert r["elevation_deg"] == pytest.approx(61.9, abs=1.0)
        assert r["azimuth_deg"] == pytest.approx(180.0, abs=5.0)

    def test_equator_equinox_noon_near_zenith(self):
        r = sg.solar_position(0.0, 0.0, datetime(2024, 3, 20, 12, 7, 0, tzinfo=timezone.utc))
        assert r["elevation_deg"] == pytest.approx(90.0, abs=1.0)

    def test_midnight_is_below_horizon(self):
        r = sg.solar_position(sg.CIA_LAT, sg.CIA_LON, datetime(2024, 6, 21, 5, 0, 0, tzinfo=timezone.utc))
        assert r["elevation_deg"] < 0

    def test_azimuth_and_elevation_in_valid_ranges(self):
        for dt in sg.QUERY_MOMENTS.values():
            r = sg.solar_position(sg.CIA_LAT, sg.CIA_LON, dt)
            assert 0.0 <= r["azimuth_deg"] < 360.0
            assert -90.0 <= r["elevation_deg"] <= 90.0


class TestSolarShadowBearings:
    def test_returns_named_bearing_pairs(self):
        bearings = sg.solar_shadow_bearings()
        for name in sg.QUERY_MOMENTS:
            assert f"solar_shadow_{name}" in bearings
            assert f"solar_shadow_{name}_reversed" in bearings

    def test_reversed_is_opposite(self):
        bearings = sg.solar_shadow_bearings()
        forward = bearings["solar_shadow_cia_dedication"]
        reverse = bearings["solar_shadow_cia_dedication_reversed"]
        assert reverse == pytest.approx((forward + 180.0) % 360.0)

    def test_flows_into_geography_derived_bearings(self):
        from kryptos.k4.clock_rotation import geography_derived_bearings

        bearings = geography_derived_bearings()
        assert "solar_shadow_cia_dedication" in bearings

    def test_flows_into_geo_bearing_order_names(self):
        from kryptos.k4.geometry_combined_sweep import GEO_BEARING_ORDER_NAMES

        assert "route_solar_shadow_cia_dedication" in GEO_BEARING_ORDER_NAMES
