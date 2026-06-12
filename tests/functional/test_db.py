"""Tests for kryptos.db — DATABASE_URL connection helper."""

from __future__ import annotations

import os

import pytest

from kryptos.db import get_conn, get_db_url


class TestGetDbUrl:
    def test_raises_without_database_url(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises(RuntimeError, match="DATABASE_URL"):
            get_db_url()

    def test_returns_url_unchanged(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/db")
        assert get_db_url() == "postgresql://user:pass@host/db"

    def test_strips_inline_comment(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host/db  # comment")
        assert get_db_url() == "postgresql://user:pass@host/db"


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
class TestGetConnLive:
    def test_get_conn_executes_query(self):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                assert cur.fetchone() == (1,)
