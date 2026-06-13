"""Tests for kryptos.persistence — best-effort Neon candidate/run storage."""

from __future__ import annotations

import json
import os

import pytest

from kryptos.persistence import db_enabled, fetch_recent_runs, fetch_run_candidates, persist_campaign_candidates

SAMPLE_CANDIDATES = [
    {"score": -10.0, "source": "quagmire", "key": [[1, 2], [3, 4]], "text": "EASTNORTHEAST", "metrics": {"ic": 0.06}},
    {"score": -25.0, "source": "beaufort", "key": None, "text": "GARBLEDTEXTHERE", "metrics": {}},
]


class TestDbDisabled:
    def test_db_enabled_false_without_url(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert db_enabled() is False

    def test_persist_returns_none_without_url(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert persist_campaign_candidates("stage1", "K4", "OBKR...", SAMPLE_CANDIDATES) is None

    def test_fetch_helpers_empty_without_url(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        assert fetch_recent_runs() == []
        assert fetch_run_candidates(1) == []


class TestReportingIntegration:
    def test_generate_artifacts_skips_db_when_disabled(self, tmp_path, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        from kryptos.k4.reporting import generate_candidate_artifacts

        paths = generate_candidate_artifacts("stage1", "K4", "OBKR" * 10, SAMPLE_CANDIDATES, out_dir=str(tmp_path))
        assert "json" in paths and "db_run_id" not in paths
        data = json.loads((tmp_path / "k4_candidates.json").read_text(encoding="utf-8"))
        assert data["candidate_count"] == 2

    def test_persist_db_false_forces_skip(self, tmp_path, monkeypatch):
        # Even if a (fake) URL is set, persist_db=False must not attempt a write
        monkeypatch.setenv("DATABASE_URL", "postgresql://unused")
        from kryptos.k4.reporting import generate_candidate_artifacts

        paths = generate_candidate_artifacts(
            "stage1", "K4", "OBKR" * 10, SAMPLE_CANDIDATES, out_dir=str(tmp_path), persist_db=False
        )
        assert "db_run_id" not in paths


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
class TestLivePersistence:
    @pytest.fixture(autouse=True)
    def _schema_and_cleanup(self):
        from kryptos.db import get_conn
        from kryptos.db_schema import init_schema

        init_schema()
        yield
        # Remove rows created by this test (candidates cascade via run id)
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM candidates WHERE text LIKE %s", ("__pers_test__%",))
                cur.execute("DELETE FROM campaign_runs WHERE label = %s", ("__pers_test__",))

    def test_persist_and_read_back(self):
        candidates = [
            {
                "score": -5.0,
                "source": "q3",
                "key": [[2, 3], [4, 5]],
                "text": "__pers_test__TOP",
                "metrics": {"ic": 0.07},
            },
            {"score": -9.0, "source": "q3", "key": None, "text": "__pers_test__SECOND", "metrics": {}},
        ]
        run_id = persist_campaign_candidates("__pers_test__", "__pers_test__", "OBKRUOX", candidates)
        assert isinstance(run_id, int)

        cands = fetch_run_candidates(run_id)
        assert [c["rank"] for c in cands] == [1, 2]
        assert cands[0]["text"] == "__pers_test__TOP"
        assert cands[0]["key"] == [[2, 3], [4, 5]]  # jsonb round-trips to list
        assert cands[0]["key_hash"] is not None
        assert cands[1]["key"] is None

        runs = fetch_recent_runs()
        assert any(r["id"] == run_id for r in runs)

    def test_persist_respects_limit(self):
        many = [
            {"score": -float(i), "source": "q3", "key": None, "text": f"__pers_test__{i}", "metrics": {}}
            for i in range(10)
        ]
        run_id = persist_campaign_candidates("__pers_test__", "__pers_test__", "OBKR", many, limit=3)
        assert len(fetch_run_candidates(run_id)) == 3
