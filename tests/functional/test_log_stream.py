"""Tests for the SSE log tail: ring buffer, handler, and event stream."""

import asyncio
import logging

from fastapi.testclient import TestClient

from kryptos.api import log_stream
from kryptos.api.app import create_app
from kryptos.api.log_stream import LogBuffer, SSELogHandler, _format_sse, install_log_streaming, log_event_stream
from kryptos.rag.index import ArtifactIndex


async def _collect(agen, limit=100):
    out = []
    async for frame in agen:
        out.append(frame)
        if len(out) >= limit:
            break
    return out


def _run(coro):
    return asyncio.run(coro)


# --- LogBuffer ----------------------------------------------------------------


def test_log_buffer_tail_and_since():
    buf = LogBuffer(capacity=3)
    for line in ["a", "b", "c", "d"]:
        buf.append(line)
    # Capacity 3 -> oldest ("a") evicted.
    assert [line for _seq, line in buf.tail(10)] == ["b", "c", "d"]
    assert [line for _seq, line in buf.tail(2)] == ["c", "d"]

    seq_c = buf.tail(10)[1][0]
    assert [line for _seq, line in buf.since(seq_c)] == ["d"]
    assert buf.since(buf.latest_seq()) == []


# --- Handler ------------------------------------------------------------------


def test_handler_captures_records():
    buf = LogBuffer()
    handler = SSELogHandler(buf)
    logger = logging.getLogger("kryptos.test.capture")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("hello %s", "world")
    logger.debug("not captured")  # below handler level

    lines = [line for _seq, line in buf.tail(10)]
    assert any("hello world" in ln for ln in lines)
    assert not any("not captured" in ln for ln in lines)


def test_install_is_idempotent():
    name = "kryptos.test.install"
    h1 = install_log_streaming(logger_name=name, buffer=LogBuffer())
    h2 = install_log_streaming(logger_name=name, buffer=LogBuffer())
    assert h1 is h2
    logger = logging.getLogger(name)
    assert sum(isinstance(h, SSELogHandler) for h in logger.handlers) == 1


# --- SSE formatting -----------------------------------------------------------


def test_format_sse_multiline():
    frame = _format_sse("line1\nline2")
    assert frame == "data: line1\ndata: line2\n\n"


# --- Event stream -------------------------------------------------------------


def test_stream_replays_backlog_and_stops():
    buf = LogBuffer()
    for line in ["one", "two", "three"]:
        buf.append(line)

    async def never_disconnected():
        return False

    frames = _run(_collect(log_event_stream(never_disconnected, backlog=10, follow=False, buffer=buf)))
    assert frames == [_format_sse(x) for x in ["one", "two", "three"]]


def test_stream_stops_on_disconnect():
    buf = LogBuffer()
    buf.append("only")

    async def disconnected():
        return True

    # follow=True but the client is already gone: replay backlog, then return
    # at the first disconnect check rather than looping forever.
    frames = _run(
        asyncio.wait_for(
            _collect(log_event_stream(disconnected, backlog=10, follow=True, buffer=buf, poll_interval=0.01)),
            timeout=2.0,
        )
    )
    assert frames == [_format_sse("only")]


# --- HTTP layer ---------------------------------------------------------------


def test_http_stream_backlog(tmp_path, monkeypatch):
    # The endpoint uses the module-global LOG_BUFFER; seed it then read backlog.
    monkeypatch.setenv("KRYPTOS_LOG_TOKEN", "s3cret-token")
    log_stream.LOG_BUFFER.append("CAMPAIGN started")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))

    resp = client.get(
        "/api/stream/logs",
        params={"follow": "false", "backlog": "1000"},
        headers={"X-Kryptos-Log-Token": "s3cret-token"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert "data: CAMPAIGN started" in resp.text


# --- Public (redacted) vs full view --------------------------------------------


def test_redact_public_masks_credentials_and_tracebacks():
    line = "ERROR x: boom postgresql://user:hunter2@db.example/neondb password=abc\nTraceback (most recent call last):"
    out = log_stream.redact_public(line)
    assert "hunter2" not in out
    assert "abc" not in out
    assert "Traceback" not in out
    assert out.endswith("[details withheld]")


def test_redact_public_quoted_keys_and_auth_schemes():
    cases = [
        '{"password": "hunter2", "x": 1}',
        "{'api_key': 'hunter2'}",
        "Authorization: Bearer hunter2 next",
        "password=hunter2 ok",
    ]
    for case in cases:
        out = log_stream.redact_public(case)
        assert "hunter2" not in out, out
        assert "***" in out


def test_http_stream_masks_bearer_in_backlog_and_live(tmp_path, monkeypatch):
    monkeypatch.delenv("KRYPTOS_LOG_TOKEN", raising=False)
    log_stream.LOG_BUFFER.append("INFO upstream Authorization: Bearer abc123")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    resp = client.get("/api/stream/logs", params={"follow": "false", "backlog": "1000"})
    assert "abc123" not in resp.text

    buf = LogBuffer()
    logger = logging.getLogger("kryptos.test.bearer")
    logger.handlers = [SSELogHandler(buf)]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.info("calling with Authorization: Bearer %s", "abc123")
    ((_seq, public),) = buf.since(0, public=True)
    assert "abc123" not in public


def test_handler_public_line_hides_traceback_and_exception_text():
    buf = LogBuffer()
    handler = SSELogHandler(buf)
    logger = logging.getLogger("kryptos.test.public")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        raise RuntimeError('relation "secret_table" does not exist')
    except RuntimeError as exc:
        logger.exception("could not load run (%s)", exc)

    ((_seq, full),) = buf.tail(1)
    ((_seq, public),) = buf.tail(1, public=True)
    assert "Traceback" in full and "secret_table" in full
    assert "Traceback" not in public and "secret_table" not in public
    assert "<RuntimeError>" in public and public.endswith("[details withheld]")


def test_http_stream_anonymous_refused_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("KRYPTOS_LOG_TOKEN", raising=False)
    monkeypatch.delenv("KRYPTOS_LOG_STREAM_PUBLIC", raising=False)
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    assert client.get("/api/stream/logs", params={"follow": "false"}).status_code == 401


def test_http_stream_anonymous_gets_public_view(tmp_path, monkeypatch):
    monkeypatch.delenv("KRYPTOS_LOG_TOKEN", raising=False)
    monkeypatch.setenv("KRYPTOS_LOG_STREAM_PUBLIC", "redacted")
    log_stream.LOG_BUFFER.append("ERROR boom\nTraceback (most recent call last):\n  File site-packages/x.py")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    resp = client.get("/api/stream/logs", params={"follow": "false", "backlog": "1000"})
    assert resp.status_code == 200
    assert resp.headers["x-kryptos-log-view"] == "public"
    assert 'event: meta\ndata: {"view": "public"}' in resp.text
    assert "Traceback" not in resp.text and "site-packages" not in resp.text
    assert "data: ERROR boom [details withheld]" in resp.text


def test_http_stream_token_unlocks_full_view(tmp_path, monkeypatch):
    monkeypatch.setenv("KRYPTOS_LOG_TOKEN", "s3cret-token")
    log_stream.LOG_BUFFER.append("ERROR full\nTraceback (most recent call last):")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))

    bad = client.get("/api/stream/logs", params={"follow": "false", "token": "nope"})
    assert bad.status_code == 401

    ok = client.get("/api/stream/logs", params={"follow": "false"}, headers={"X-Kryptos-Log-Token": "s3cret-token"})
    assert ok.status_code == 200
    assert ok.headers["x-kryptos-log-view"] == "full"
    assert "Traceback" in ok.text


def test_http_stream_public_off_requires_token(tmp_path, monkeypatch):
    monkeypatch.delenv("KRYPTOS_LOG_TOKEN", raising=False)
    monkeypatch.setenv("KRYPTOS_LOG_STREAM_PUBLIC", "off")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    assert client.get("/api/stream/logs", params={"follow": "false"}).status_code == 401


def test_unhandled_errors_are_generic(tmp_path, monkeypatch):
    # No SPA mount, so the route added below is reachable even if frontend/dist exists.
    monkeypatch.setattr("kryptos.api.app._resolve_frontend_dist", lambda: None)
    app = create_app(index=ArtifactIndex(index_dir=tmp_path / "index"))

    @app.get("/api/__boom")
    def _boom():
        raise RuntimeError("psycopg2 relation secret_table does not exist")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/api/__boom")
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}
    assert "secret_table" not in resp.text


def test_redact_public_masks_bare_uuids():
    out = log_stream.redact_public("Sealed 3f2b8c1e-9d4a-4b7e-8c21-5a6d7e8f9a0b ok")
    assert "3f2b8c1e" not in out and "<id>" in out


def test_vault_records_are_hidden_from_public_view():
    buf = LogBuffer()
    handler = SSELogHandler(buf)
    vault_logger = logging.getLogger("kryptos.vault")
    other = logging.getLogger("kryptos.other_public_test")
    for lg in (vault_logger, other):
        lg.addHandler(handler)
        lg.setLevel(logging.INFO)
    try:
        vault_logger.info("Sealed vault payload ref=abcd1234")
        other.info("regular line")
    finally:
        vault_logger.removeHandler(handler)
        other.removeHandler(handler)
    public = [line for _s, line in buf.tail(10, public=True)]
    full = [line for _s, line in buf.tail(10)]
    assert any("regular line" in ln for ln in public)
    assert not any("vault" in ln.lower() for ln in public)
    assert any("Sealed vault payload" in ln for ln in full)
    assert not any("Sealed vault payload" in ln for _s, ln in buf.since(0, public=True))


def test_public_mode_defaults_to_off(monkeypatch):
    monkeypatch.delenv("KRYPTOS_LOG_STREAM_PUBLIC", raising=False)
    assert log_stream.public_log_mode() == "off"
    monkeypatch.setenv("KRYPTOS_LOG_STREAM_PUBLIC", "redacted")
    assert log_stream.public_log_mode() == "redacted"


def test_stream_slots_cap_and_release():
    slots = log_stream.StreamSlots()
    assert slots.acquire(2) and slots.acquire(2)
    assert not slots.acquire(2)
    slots.release()
    assert slots.acquire(2)


def test_http_stream_cap_returns_429(tmp_path, monkeypatch):
    monkeypatch.setenv("KRYPTOS_LOG_TOKEN", "s3cret-token")
    monkeypatch.setenv("KRYPTOS_MAX_LOG_STREAMS", "1")
    held = log_stream.StreamSlots()
    monkeypatch.setattr("kryptos.api.app.STREAM_SLOTS", held)
    assert held.acquire(1)
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))
    resp = client.get("/api/stream/logs", params={"follow": "false"}, headers={"X-Kryptos-Log-Token": "s3cret-token"})
    assert resp.status_code == 429
    held.release()
    ok = client.get("/api/stream/logs", params={"follow": "false"}, headers={"X-Kryptos-Log-Token": "s3cret-token"})
    assert ok.status_code == 200
    assert held.open_count == 0
