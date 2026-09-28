"""Suite runs are stored in Neon when DATABASE_URL is set (exercised against a fake connection)."""

from __future__ import annotations

import json
from contextlib import contextmanager

from kryptos.k4 import hypothesis_ledger, run_store


class _Cur:
    def __init__(self, rows):
        self.rows = rows
        self._last = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=()):
        if sql.startswith("INSERT"):
            self.rows.append(json.loads(params[0]))
        else:
            self._last = (self.rows[-1],) if self.rows else None

    def fetchone(self):
        return self._last


def test_save_and_load_and_ledger_fallback(monkeypatch, tmp_path):
    rows: list = []

    class _Conn:
        def cursor(self):
            return _Cur(rows)

    @contextmanager
    def fake_conn():
        yield _Conn()

    monkeypatch.setenv("DATABASE_URL", "postgres://fake")
    monkeypatch.setattr("kryptos.db.get_conn", fake_conn)
    monkeypatch.chdir(tmp_path)  # no local artifact
    summary = {"timestamp": "2026-09-28T00:00:00Z", "run_params": {"widths": [2]}, "columnar_period": {}}
    assert run_store.save_run(summary) is True
    assert run_store.load_latest() == summary
    assert hypothesis_ledger.latest_run()["timestamp"] == "2026-09-28T00:00:00Z"


def test_disabled_without_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert run_store.save_run({"x": 1}) is False
    assert run_store.load_latest() is None
