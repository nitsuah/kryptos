"""Tests for kryptos.k4.physical_geometry."""

from __future__ import annotations

from kryptos.k4 import physical_geometry as pg


class TestMeasurement:
    def test_unknown_measurement_reports_not_known(self):
        assert not pg.UNKNOWN_DEGREES.is_known

    def test_known_measurement_reports_known(self):
        m = pg.Measurement(value=44.45, unit="degrees", source="test")
        assert m.is_known

    def test_str_of_unknown_says_unmeasured(self):
        assert "unmeasured" in str(pg.UNKNOWN_DEGREES)

    def test_str_of_known_includes_source(self):
        m = pg.Measurement(value=44.45, unit="degrees", source="test-source")
        assert "test-source" in str(m)


class TestCurrentGeometry:
    def test_compass_bearing_is_unmeasured(self):
        # The whole point of Phase 8's open lead: this must not silently
        # acquire a fabricated value.
        assert not pg.CURRENT.compass_rose.true_bearing.is_known

    def test_secondary_estimate_is_present_but_flagged(self):
        est = pg.CURRENT.compass_rose.secondary_estimate
        assert est.is_known
        assert "not exact" in est.source

    def test_lodestone_deflection_is_unmeasured(self):
        assert not pg.CURRENT.lodestone.deflection.is_known

    def test_tableau_reading_direction_is_confirmed(self):
        # This one genuinely is known -- CIA's own page.
        assert pg.CURRENT.tableau.measured
        assert pg.CURRENT.tableau.reading_direction == "back"
        assert "cia.gov" in pg.CURRENT.tableau.source


class TestKnownAndUnmeasured:
    def test_known_measurements_nonempty(self):
        # secondary_estimate + tableau are both known even with nothing
        # else measured yet.
        known = pg.known_measurements()
        assert "compass_rose.secondary_estimate" in known
        assert "tableau.reading_direction" in known

    def test_unmeasured_fields_nonempty(self):
        missing = pg.unmeasured_fields()
        assert "compass_rose.true_bearing" in missing
        assert "lodestone.deflection" in missing

    def test_known_and_unmeasured_are_disjoint(self):
        assert set(pg.known_measurements()) & set(pg.unmeasured_fields()) == set()


class TestStatusReport:
    def test_report_is_a_nonempty_string(self):
        report = pg.status_report()
        assert isinstance(report, str)
        assert "Known" in report
        assert "Unmeasured" in report
