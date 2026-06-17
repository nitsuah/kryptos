"""Tests for serving the built frontend SPA from the FastAPI app."""

import pytest
from fastapi.testclient import TestClient

from kryptos.api import app as app_module
from kryptos.api.app import _resolve_frontend_dist, create_app
from kryptos.rag.index import ArtifactIndex

pytestmark = pytest.mark.slow


def _make_dist(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>kryptos</title>", encoding="utf-8")
    (dist / "assets").mkdir()
    (dist / "assets" / "app.js").write_text("console.log('kryptos');", encoding="utf-8")
    return dist


def test_resolve_frontend_dist_env_override(tmp_path, monkeypatch):
    dist = _make_dist(tmp_path)
    monkeypatch.setenv("KRYPTOS_FRONTEND_DIST", str(dist))
    assert _resolve_frontend_dist() == dist


def test_resolve_frontend_dist_ignores_dir_without_index(tmp_path, monkeypatch):
    empty = tmp_path / "dist"
    empty.mkdir()
    monkeypatch.setenv("KRYPTOS_FRONTEND_DIST", str(empty))
    # A dir without index.html never counts; the override is skipped.
    assert _resolve_frontend_dist() != empty


def test_spa_served_when_dist_present(tmp_path, monkeypatch):
    dist = _make_dist(tmp_path)
    monkeypatch.setenv("KRYPTOS_FRONTEND_DIST", str(dist))

    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))

    # SPA index is served at root and for unknown client-side routes.
    root = client.get("/")
    assert root.status_code == 200
    assert "kryptos" in root.text

    asset = client.get("/assets/app.js")
    assert asset.status_code == 200
    assert "console.log" in asset.text

    # API + health routes still win over the catch-all SPA mount.
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/status").status_code == 200


def test_api_only_when_dist_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "_resolve_frontend_dist", lambda: None)

    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/status").status_code == 200
    # No SPA mounted -> unknown path is a normal 404, not an index fallback.
    assert client.get("/definitely-not-a-route").status_code == 404
