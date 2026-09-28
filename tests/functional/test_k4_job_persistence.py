"""K4 attack jobs persist to Neon when DATABASE_URL is set (exercised against a fake connection)."""

from __future__ import annotations

from contextlib import contextmanager

import pytest

from kryptos.api import k4_jobs


class _FakeCursor:
    def __init__(self, store):
        self.store = store
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=()):
        sql = " ".join(sql.split())
        if sql.startswith("INSERT INTO k4_attack_jobs"):
            self.store[params[0]] = tuple(params)
        elif "WHERE job_id" in sql:
            self._rows = [self.store[params[0]]] if params[0] in self.store else []
        elif "ORDER BY created_at" in sql:
            self._rows = sorted(self.store.values(), key=lambda r: r[7], reverse=True)[: params[0]]

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


@pytest.fixture()
def fake_db(monkeypatch):
    store: dict = {}

    class _Conn:
        def cursor(self):
            return _FakeCursor(store)

    @contextmanager
    def fake_get_conn():
        yield _Conn()

    monkeypatch.setenv("DATABASE_URL", "postgres://fake")
    monkeypatch.setattr("kryptos.db.get_conn", fake_get_conn)
    return store


def test_terminal_job_is_persisted_and_reloaded(fake_db, monkeypatch):
    job_id = k4_jobs.new_job("p21_crib_constraints")
    k4_jobs.update_job(job_id, status="running")
    assert job_id not in fake_db  # only terminal states are written
    k4_jobs.update_job(job_id, status="complete", progress_pct=100.0, summary={"status": "complete"})
    assert job_id in fake_db

    monkeypatch.setattr(k4_jobs, "_JOBS", {})  # simulate a restart
    job = k4_jobs.get_job(job_id)
    assert job is not None and job["status"] == "complete" and job["summary"] == {"status": "complete"}
    assert [j["job_id"] for j in k4_jobs.list_jobs()] == [job_id]


def test_no_database_means_memory_only(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    job_id = k4_jobs.new_job("p18_key_csp")
    k4_jobs.update_job(job_id, status="error", error="boom")
    assert k4_jobs.get_job(job_id)["error"] == "boom"
    assert k4_jobs.get_job("00000000-0000-0000-0000-000000000000") is None


def test_database_errors_never_break_a_job(monkeypatch):
    @contextmanager
    def broken():
        raise RuntimeError("db down")
        yield

    monkeypatch.setenv("DATABASE_URL", "postgres://fake")
    monkeypatch.setattr("kryptos.db.get_conn", broken)
    job_id = k4_jobs.new_job("p18_key_csp")
    k4_jobs.update_job(job_id, status="complete")
    assert k4_jobs.get_job(job_id)["status"] == "complete"
    assert k4_jobs.list_jobs(5)


def test_exclusive_new_job_refuses_while_active(monkeypatch):
    from kryptos.api import k4_jobs

    monkeypatch.setattr(k4_jobs, "_JOBS", {})
    monkeypatch.setattr(k4_jobs, "_persist", lambda job: None)
    first = k4_jobs.new_job("exclusive_probe", exclusive=True)
    assert first is not None
    assert k4_jobs.new_job("exclusive_probe", exclusive=True) is None
    assert k4_jobs.active_job("exclusive_probe") == first
    other = k4_jobs.new_job("exclusive_probe")  # non-exclusive callers are unaffected
    assert other is not None
    k4_jobs.update_job(first, status="complete")
    k4_jobs.update_job(other, status="error")
    assert k4_jobs.active_job("exclusive_probe") is None
    assert k4_jobs.new_job("exclusive_probe", exclusive=True) is not None
