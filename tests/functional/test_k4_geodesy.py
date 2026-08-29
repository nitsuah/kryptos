"""Tests for kryptos.k4.geodesy — precise WGS84 geodesic bearing/distance."""

from __future__ import annotations

import pytest

from kryptos.k4 import geodesy
from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_DEG


class TestGeodesicBearingDistance:
    def test_due_north(self):
        # Same longitude, higher latitude -> bearing 0 (due north)
        result = geodesy.geodesic_bearing_distance(0.0, 0.0, 10.0, 0.0)
        assert result["forward_azimuth_deg"] == pytest.approx(0.0, abs=1e-6)
        assert result["distance_m"] > 0

    def test_due_east_on_equator(self):
        # On the equator, due east is bearing 90
        result = geodesy.geodesic_bearing_distance(0.0, 0.0, 0.0, 10.0)
        assert result["forward_azimuth_deg"] == pytest.approx(90.0, abs=1e-6)

    def test_back_azimuth_matches_direct_reverse_calculation(self):
        forward = geodesy.geodesic_bearing_distance(38.957, -77.145, 52.520, 13.405)
        reverse = geodesy.geodesic_bearing_distance(52.520, 13.405, 38.957, -77.145)
        assert forward["back_azimuth_deg"] == pytest.approx(reverse["forward_azimuth_deg"], abs=1e-6)

    def test_distance_ft_matches_meters_conversion(self):
        result = geodesy.geodesic_bearing_distance(0.0, 0.0, 1.0, 0.0)
        assert result["distance_ft"] == pytest.approx(result["distance_m"] * 3.280839895, rel=1e-9)

    def test_azimuths_in_valid_range(self):
        result = geodesy.geodesic_bearing_distance(38.957, -77.145, 52.520, 13.405)
        assert 0 <= result["forward_azimuth_deg"] < 360
        assert 0 <= result["back_azimuth_deg"] < 360


class TestCiaBerlinGeodesic:
    def test_matches_spherical_approximation_closely(self):
        # The precise geodesic and bearing_attack's spherical approximation
        # should agree to within a fraction of a degree over this distance.
        precise = geodesy.cia_berlin_geodesic()
        assert precise["forward_azimuth_deg"] == pytest.approx(CIA_BERLIN_BEARING_DEG, abs=0.1)

    def test_distance_is_plausible_transatlantic_scale(self):
        precise = geodesy.cia_berlin_geodesic()
        # CIA HQ to Berlin is roughly 6700 km
        assert 6_600_000 < precise["distance_m"] < 6_900_000
