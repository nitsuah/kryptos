"""Tests for GET /api/k4/attacks/pivot-status — the v2 dashboard panel's data source."""

from __future__ import annotations

from fastapi.testclient import TestClient

from kryptos.api.app import create_app


def test_pivot_status_returns_hypothesis_graph_and_bearings():
    client = TestClient(create_app())
    resp = client.get("/api/k4/attacks/pivot-status")
    assert resp.status_code == 200

    data = resp.json()
    assert "edges" in data["hypothesis_graph"]
    assert "nodes" in data["hypothesis_graph"]
    assert data["hypothesis_graph_mermaid"].startswith("flowchart TD")
    assert data["total_candidates_tested"] > 0

    assert "cia_berlin_spherical" in data["bearings"]
    assert "cia_berlin_geodesic" in data["bearings"]
    assert "kryptos_lodestone_deflection" in data["bearings"]

    # The unmeasured community claim must be explicitly labeled as such, not
    # presented as a settled figure.
    lodestone = data["bearings"]["kryptos_lodestone_deflection"]
    assert "unmeasured" in lodestone["note"].lower()

    # Spherical and geodesic CIA->Berlin bearings should agree closely.
    spherical = data["bearings"]["cia_berlin_spherical"]["forward_azimuth_deg"]
    geodesic = data["bearings"]["cia_berlin_geodesic"]["forward_azimuth_deg"]
    assert abs(spherical - geodesic) < 0.5
