"""Tests for the dashboard API router (kryptos.api.dashboard)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from kryptos.api.app import create_app
from kryptos.rag.index import ArtifactIndex

# Verified K1 vector (keyed Vigenère, key PALIMPSEST)
K1_CIPHERTEXT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"


def _client(tmp_path) -> TestClient:
    # Unbuilt index — dashboard routes don't depend on it
    return TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))


class TestDashboardDbDisabled:
    @pytest.fixture(autouse=True)
    def _no_db(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)

    def test_status(self, tmp_path):
        resp = _client(tmp_path).get("/api/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["db_enabled"] is False
        assert body["table_counts"] == {}
        assert body["latest_run"] is None

    def test_runs_empty(self, tmp_path):
        resp = _client(tmp_path).get("/api/runs")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"db_enabled": False, "count": 0, "runs": []}

    def test_run_candidates_empty(self, tmp_path):
        resp = _client(tmp_path).get("/api/runs/1/candidates")
        assert resp.status_code == 200
        assert resp.json()["candidates"] == []

    def test_top_candidates_empty(self, tmp_path):
        resp = _client(tmp_path).get("/api/candidates", params={"limit": 5})
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    def test_runs_limit_validation(self, tmp_path):
        assert _client(tmp_path).get("/api/runs", params={"limit": 0}).status_code == 422
        assert _client(tmp_path).get("/api/runs", params={"limit": 999}).status_code == 422


class TestDecryptEndpoint:
    def test_k1_decrypt(self, tmp_path):
        resp = _client(tmp_path).post(
            "/api/decrypt", json={"section": "K1", "ciphertext": K1_CIPHERTEXT, "key": "PALIMPSEST"}
        )
        assert resp.status_code == 200
        assert resp.json() == {"section": "K1", "plaintext": K1_PLAINTEXT}

    def test_k1_lowercase_section(self, tmp_path):
        resp = _client(tmp_path).post(
            "/api/decrypt", json={"section": "k1", "ciphertext": K1_CIPHERTEXT, "key": "PALIMPSEST"}
        )
        assert resp.status_code == 200
        assert resp.json()["plaintext"] == K1_PLAINTEXT

    def test_k1_missing_key_returns_422(self, tmp_path):
        resp = _client(tmp_path).post("/api/decrypt", json={"section": "K1", "ciphertext": K1_CIPHERTEXT})
        assert resp.status_code == 422

    def test_unknown_section_returns_422(self, tmp_path):
        resp = _client(tmp_path).post("/api/decrypt", json={"section": "K9", "ciphertext": "ABC"})
        assert resp.status_code == 422

    def test_empty_ciphertext_returns_422(self, tmp_path):
        # Pydantic min_length=1 rejects empty ciphertext
        resp = _client(tmp_path).post("/api/decrypt", json={"section": "K1", "ciphertext": "", "key": "X"})
        assert resp.status_code == 422


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
class TestDashboardLive:
    @pytest.fixture(autouse=True)
    def _schema_and_cleanup(self):
        from kryptos.db import get_conn
        from kryptos.db_schema import init_schema

        init_schema()
        yield
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM candidates WHERE text LIKE %s", ("__api_test__%",))
                cur.execute("DELETE FROM campaign_runs WHERE label = %s", ("__api_test__",))

    def test_status_and_runs_after_persist(self, tmp_path):
        from kryptos.persistence import persist_campaign_candidates

        cands = [
            {"score": -3.0, "source": "q3", "key": [[1, 2], [3, 4]], "text": "__api_test__TOP", "metrics": {}},
            {"score": -7.0, "source": "q3", "key": None, "text": "__api_test__SECOND", "metrics": {}},
        ]
        run_id = persist_campaign_candidates("__api_test__", "__api_test__", "OBKR", cands)
        assert isinstance(run_id, int)

        client = _client(tmp_path)

        status = client.get("/api/status").json()
        assert status["db_enabled"] is True
        assert status["table_counts"]["campaign_runs"] >= 1

        runs = client.get("/api/runs").json()
        assert runs["db_enabled"] is True
        assert any(r["id"] == run_id for r in runs["runs"])

        cand_resp = client.get(f"/api/runs/{run_id}/candidates").json()
        assert [c["rank"] for c in cand_resp["candidates"]] == [1, 2]
        assert cand_resp["candidates"][0]["text"] == "__api_test__TOP"

        top = client.get("/api/candidates", params={"limit": 100}).json()
        assert any(c["text"] == "__api_test__TOP" for c in top["candidates"])
