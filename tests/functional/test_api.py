import json

import pytest
from fastapi.testclient import TestClient

from kryptos import paths
from kryptos.api.app import create_app
from kryptos.rag.index import ArtifactIndex

pytestmark = pytest.mark.slow


def _write_sample_artifacts(artifacts_root):
    decisions = artifacts_root / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "a.json").write_text(
        json.dumps({"hypothesis": "Hill cipher 2x2 with key matrix [[5, 10], [13, 1]]"}),
        encoding="utf-8",
    )


def test_health_endpoint(tmp_path):
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    assert client.get("/health").json() == {"status": "ok"}


def test_rag_search_before_index_returns_409(tmp_path):
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    resp = client.get("/api/rag/search", params={"q": "foo"})
    assert resp.status_code == 409


def test_rag_status_and_search_with_prebuilt_index(tmp_path):
    artifacts_root = tmp_path / "artifacts"
    _write_sample_artifacts(artifacts_root)

    index = ArtifactIndex(index_dir=tmp_path / "index")
    index.build(artifacts_root=artifacts_root)

    client = TestClient(create_app(index=index))

    status = client.get("/api/rag/status").json()
    assert status["indexed"] is True
    assert status["chunk_count"] == 1

    resp = client.get("/api/rag/search", params={"q": "Hill cipher key matrix", "k": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "Hill cipher key matrix"
    assert body["results"][0]["path"] == "decisions/a.json"


def test_rag_reindex_endpoint(tmp_path, monkeypatch):
    artifacts_root = tmp_path / "artifacts"
    _write_sample_artifacts(artifacts_root)

    monkeypatch.setenv(paths.ENV_ROOT, str(tmp_path))
    paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
    try:
        index = ArtifactIndex(index_dir=tmp_path / "index")
        client = TestClient(create_app(index=index))

        resp = client.post("/api/rag/reindex")
        assert resp.status_code == 200
        assert resp.json()["chunk_count"] == 1

        status = client.get("/api/rag/status").json()
        assert status["indexed"] is True
    finally:
        paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
