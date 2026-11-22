"""Token auth, rate limiting and job caps on mutating and expensive API routes."""

from __future__ import annotations

import threading

import pytest
from fastapi.testclient import TestClient

from kryptos.api import k4_jobs
from kryptos.api.app import create_app
from kryptos.api.security import RATE_LIMITER, RateLimiter, is_loopback_host
from kryptos.rag.index import ArtifactIndex

TOKEN = "unit-test-api-token"
PROTECTED = [
    ("post", "/api/rag/reindex", None),
    ("post", "/api/k4/attacks/run", {"attack_id": "p21_crib_constraints"}),
    ("post", "/api/decrypt", {"section": "K3", "ciphertext": "ABC"}),
    ("post", "/api/vault/seal", {"plaintext": "x", "key": "KEY"}),
    ("post", "/api/vault/unseal", {"token": "t", "key": "KEY"}),
    ("get", "/api/vault/some-token", None),
]


@pytest.fixture(autouse=True)
def _instant_attack_jobs(monkeypatch):
    """Attack jobs finish immediately; the job registry is emptied after each test."""
    monkeypatch.setattr(
        "kryptos.api.k4_attack_routes.run_attack_worker",
        lambda job_id, req: k4_jobs.update_job(job_id, status="complete"),
    )
    yield
    with k4_jobs._JOBS_LOCK:
        k4_jobs._JOBS.clear()


@pytest.fixture()
def client(tmp_path):
    return TestClient(create_app(ArtifactIndex(tmp_path / "idx")))


def _auth_refused(resp) -> bool:
    """True when the response is the auth layer's refusal (not e.g. the vault's own 503)."""
    detail = resp.json().get("detail") if resp.headers.get("content-type", "").startswith("application/json") else ""
    return detail in {"Invalid or missing API token", "API token is not configured"}


def _call(client, method, path, body, headers=None):
    return getattr(client, method)(path, headers=headers or {}, **({"json": body} if body is not None else {}))


@pytest.mark.parametrize(("method", "path", "body"), PROTECTED)
def test_token_required_when_configured(client, monkeypatch, method, path, body):
    monkeypatch.setenv("KRYPTOS_API_TOKEN", TOKEN)
    assert _call(client, method, path, body).status_code == 401
    assert _call(client, method, path, body, {"Authorization": "Bearer wrong"}).status_code == 401
    for headers in ({"Authorization": f"Bearer {TOKEN}"}, {"X-Kryptos-Token": TOKEN}):
        ok = _call(client, method, path, body, headers)
        assert not _auth_refused(ok)


@pytest.mark.parametrize(("method", "path", "body"), PROTECTED)
def test_closed_without_token_or_opt_out(client, monkeypatch, method, path, body):
    monkeypatch.delenv("KRYPTOS_API_AUTH", raising=False)
    resp = _call(client, method, path, body)
    assert resp.status_code == 503 and _auth_refused(resp)


def test_opt_out_is_ignored_in_production(client, monkeypatch):
    monkeypatch.setenv("KRYPTOS_API_AUTH", "off")
    monkeypatch.setenv("RENDER", "true")
    assert _auth_refused(client.post("/api/rag/reindex"))
    monkeypatch.delenv("RENDER")
    monkeypatch.setenv("KRYPTOS_ENV", "production")
    assert _auth_refused(client.post("/api/rag/reindex"))


def test_opt_out_requires_loopback_peer(tmp_path, monkeypatch):
    app = create_app(ArtifactIndex(tmp_path / "idx"))
    remote = TestClient(app, client=("203.0.113.9", 5000))
    assert _auth_refused(remote.post("/api/rag/reindex"))
    local = TestClient(app, client=("127.0.0.1", 5000))
    assert not _auth_refused(local.post("/api/rag/reindex"))
    # A forwarding header means the request came through a proxy: not local dev.
    assert _auth_refused(local.post("/api/rag/reindex", headers={"X-Forwarded-For": "198.51.100.1"}))


def test_loopback_helper():
    assert is_loopback_host("127.0.0.1") and is_loopback_host("::1")
    assert not is_loopback_host("10.0.0.5") and not is_loopback_host(None)


def test_rate_limiter_window():
    rl = RateLimiter()
    assert all(rl.allow("a", 3) for _ in range(3))
    assert not rl.allow("a", 3)
    assert rl.allow("b", 3)
    assert rl.allow("a", 0)  # 0 disables


def test_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.setenv("KRYPTOS_API_TOKEN", TOKEN)
    monkeypatch.setenv("KRYPTOS_RATE_LIMIT_PER_MIN", "3")
    RATE_LIMITER.reset()
    codes = [client.post("/api/rag/reindex").status_code for _ in range(5)]
    assert codes[:3] == [401, 401, 401]
    assert codes[3:] == [429, 429]


def test_attack_job_cap(client, monkeypatch):
    monkeypatch.setenv("KRYPTOS_MAX_ATTACK_JOBS", "1")
    release = threading.Event()
    monkeypatch.setattr("kryptos.api.k4_attack_routes.run_attack_worker", lambda job_id, req: release.wait(5))
    try:
        first = client.post("/api/k4/attacks/run", json={"attack_id": "p21_crib_constraints"})
        assert first.status_code == 200
        second = client.post("/api/k4/attacks/run", json={"attack_id": "p22_frontier_checks"})
        assert second.status_code == 429
        assert second.headers["retry-after"]
    finally:
        release.set()


def test_read_only_routes_stay_open(client, monkeypatch):
    monkeypatch.setenv("KRYPTOS_API_TOKEN", TOKEN)
    assert client.get("/health").status_code == 200
    assert client.get("/api/k4/attacks/frontier").status_code == 200
