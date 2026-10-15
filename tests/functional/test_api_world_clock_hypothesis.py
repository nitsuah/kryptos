"""API contract tests for the World Clock hypothesis diagnostic."""

from fastapi.testclient import TestClient

from kryptos.api.app import create_app
from kryptos.k4.world_clock_hypothesis import analyze_world_clock_hypothesis
from kryptos.rag.index import ArtifactIndex


def test_world_clock_hypothesis_endpoint_returns_reproducible_report(tmp_path):
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    response = client.get("/api/k4/world-clock/hypothesis")

    assert response.status_code == 200
    assert response.json() == analyze_world_clock_hypothesis()
