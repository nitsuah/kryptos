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
    def test_all_sourced_historical_pairs_are_vacuous(self):
        # Documents the actual finding: every sourced timestamp is
        # whole-minute precision, and the topper's 60s period means any
        # two whole-minute moments are always co-phased (angle 0).
        for ref_dt in sg.REFERENCE_EPOCHS.values():
            for query_dt in sg.QUERY_MOMENTS.values():
                assert sg.topper_rotation_angle_deg(query_dt, ref_dt) == 0.0

    def test_returns_full_24_value_range(self):
        offsets = sg.topper_shadow_offsets()
        assert sorted(offsets.values()) == list(range(24))
        assert len(offsets) == 24


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
