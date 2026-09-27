"""Characterization tests for the K4 attack routes: job creation, status
transitions (queued/running/complete/error/eureka), and dispatch to the
correct attack module.

These tests exercise the public HTTP surface (POST /run, GET /jobs/{id},
GET /frontier) via FastAPI's TestClient, so they hold regardless of how the
job-store / dispatch machinery behind the routes is organized internally.
"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from kryptos.api.app import create_app
from kryptos.api.k4_attack_routes import FRONTIER_VECTORS
from kryptos.k4.eureka import EurekaSignal


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Attacks write artifacts (e.g. K4_*_NULL.json) to the working directory, and
    # later attacks read them back; keep each test's output out of the repo.
    monkeypatch.chdir(tmp_path)
    return TestClient(create_app())


@pytest.fixture()
def fast_attacks(monkeypatch):
    """Replace the real sweeps with instant fakes: these tests pin the job
    lifecycle and dispatch, not attack speed (the real sweeps can take >10s on CI)."""
    monkeypatch.setattr("kryptos.k4.gronsfeld.run_gronsfeld_sweep", lambda *a, **k: {"fake": "gronsfeld"})
    monkeypatch.setattr("kryptos.k4.key_csp.run_key_csp_attack", lambda *a, **k: {"fake": "key_csp"})


def _poll_until_done(client: TestClient, job_id: str, timeout: float = 10.0) -> dict:
    deadline = time.time() + timeout
    job = None
    while time.time() < deadline:
        resp = client.get(f"/api/k4/attacks/jobs/{job_id}")
        assert resp.status_code == 200
        job = resp.json()
        if job["status"] not in ("queued", "running"):
            return job
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} did not finish within {timeout}s (last status: {job})")


# ---------------------------------------------------------------------------
# GET /frontier
# ---------------------------------------------------------------------------
def test_frontier_lists_all_vectors(client):
    resp = client.get("/api/k4/attacks/frontier")
    assert resp.status_code == 200
    vectors = resp.json()["vectors"]
    assert len(vectors) == len(FRONTIER_VECTORS)
    ids = {v["id"] for v in vectors}
    assert "p1_three_layer" in ids
    assert "p7_gronsfeld" in ids
    assert "p8_myszkowski" in ids  # a deferred/non-runnable vector


# ---------------------------------------------------------------------------
# POST /run — validation
# ---------------------------------------------------------------------------
def test_run_unknown_attack_id_is_rejected(client):
    resp = client.post("/api/k4/attacks/run", json={"attack_id": "totally_bogus"})
    assert resp.status_code == 422
    assert "not runnable" in resp.json()["detail"]


def test_run_deferred_attack_is_rejected(client):
    resp = client.post("/api/k4/attacks/run", json={"attack_id": "p8_myszkowski"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /jobs/{id} — unknown job
# ---------------------------------------------------------------------------
def test_job_status_404_for_unknown_job(client):
    resp = client.get("/api/k4/attacks/jobs/does-not-exist")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /run — end-to-end lifecycle (attack stubbed by fast_attacks)
# ---------------------------------------------------------------------------
def test_run_gronsfeld_job_reaches_complete(client, fast_attacks):
    resp = client.post("/api/k4/attacks/run", json={"attack_id": "p7_gronsfeld"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["attack_id"] == "p7_gronsfeld"
    # The worker thread can finish before the response is built.
    assert body["status"] in ("queued", "running", "complete")
    job_id = body["job_id"]

    job = _poll_until_done(client, job_id)
    assert job["status"] == "complete"
    assert job["progress_pct"] == 100.0
    assert job["summary"] is not None
    assert job["job_id"] == job_id
    assert job["attack_id"] == "p7_gronsfeld"


# ---------------------------------------------------------------------------
# POST /run — error path (attack module raises)
# ---------------------------------------------------------------------------
def test_run_job_records_error_on_exception(client, monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr("kryptos.k4.gronsfeld.run_gronsfeld_sweep", _boom)

    resp = client.post("/api/k4/attacks/run", json={"attack_id": "p7_gronsfeld"})
    job_id = resp.json()["job_id"]

    job = _poll_until_done(client, job_id)
    assert job["status"] == "error"
    assert job["error"] == "synthetic failure"


# ---------------------------------------------------------------------------
# POST /run — eureka path (attack module raises EurekaSignal)
# ---------------------------------------------------------------------------
def test_run_job_records_eureka_signal(client, monkeypatch):
    def _eureka(*args, **kwargs):
        raise EurekaSignal(snapshot_path="K4_TEST_SNAPSHOT.md", result={"candidate_text": "BERLINCLOCK"})

    monkeypatch.setattr("kryptos.k4.gronsfeld.run_gronsfeld_sweep", _eureka)

    resp = client.post("/api/k4/attacks/run", json={"attack_id": "p7_gronsfeld"})
    job_id = resp.json()["job_id"]

    job = _poll_until_done(client, job_id)
    assert job["status"] == "eureka"
    assert job["progress_pct"] == 100.0
    assert job["summary"]["snapshot_path"] == "K4_TEST_SNAPSHOT.md"
    assert job["summary"]["result"] == {"candidate_text": "BERLINCLOCK"}


# ---------------------------------------------------------------------------
# Multiple concurrent jobs get distinct, independently-tracked state
# ---------------------------------------------------------------------------
def test_run_multiple_jobs_have_independent_state(client, fast_attacks):
    resp1 = client.post("/api/k4/attacks/run", json={"attack_id": "p7_gronsfeld"})
    resp2 = client.post("/api/k4/attacks/run", json={"attack_id": "p18_key_csp"})
    job_id_1 = resp1.json()["job_id"]
    job_id_2 = resp2.json()["job_id"]
    assert job_id_1 != job_id_2

    job1 = _poll_until_done(client, job_id_1)
    job2 = _poll_until_done(client, job_id_2)
    assert job1["attack_id"] == "p7_gronsfeld"
    assert job2["attack_id"] == "p18_key_csp"
    assert job1["summary"] == {"fake": "gronsfeld"}
    assert job2["summary"] == {"fake": "key_csp"}
