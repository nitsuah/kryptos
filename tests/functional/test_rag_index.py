import json

import pytest

from kryptos.rag.index import ArtifactIndex

pytestmark = pytest.mark.slow


def _write_sample_artifacts(artifacts_root):
    decisions = artifacts_root / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "a.json").write_text(
        json.dumps({"hypothesis": "Hill cipher 2x2 with key matrix [[5, 10], [13, 1]]"}),
        encoding="utf-8",
    )
    (artifacts_root / "notes.md").write_text(
        "# Notes\nBerlin Clock lamp counts as transposition column widths.",
        encoding="utf-8",
    )


def test_status_before_build(tmp_path):
    index = ArtifactIndex(index_dir=tmp_path / "index")
    assert index.status() == {"indexed": False}


def test_build_and_search(tmp_path):
    artifacts_root = tmp_path / "artifacts"
    _write_sample_artifacts(artifacts_root)

    index = ArtifactIndex(index_dir=tmp_path / "index")
    status = index.build(artifacts_root=artifacts_root)

    assert status["indexed"] is True
    assert status["chunk_count"] == 2

    results = index.search("Hill cipher key matrix", k=1)
    assert len(results) == 1
    assert results[0].path == "decisions/a.json"


def test_load_round_trip(tmp_path):
    artifacts_root = tmp_path / "artifacts"
    _write_sample_artifacts(artifacts_root)

    index_dir = tmp_path / "index"
    ArtifactIndex(index_dir=index_dir).build(artifacts_root=artifacts_root)

    reloaded = ArtifactIndex(index_dir=index_dir)
    assert reloaded.load() is True
    assert reloaded.status()["chunk_count"] == 2

    results = reloaded.search("Berlin Clock transposition", k=1)
    assert results[0].path == "notes.md"


def test_build_empty_artifacts(tmp_path):
    artifacts_root = tmp_path / "artifacts"
    artifacts_root.mkdir()

    index = ArtifactIndex(index_dir=tmp_path / "index")
    status = index.build(artifacts_root=artifacts_root)

    assert status["indexed"] is True
    assert status["chunk_count"] == 0
    assert index.search("anything", k=5) == []
