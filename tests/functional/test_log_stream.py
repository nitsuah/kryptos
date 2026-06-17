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


def test_http_stream_backlog(tmp_path):
    # The endpoint uses the module-global LOG_BUFFER; seed it then read backlog.
    log_stream.LOG_BUFFER.append("CAMPAIGN started")
    client = TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))

    resp = client.get("/api/stream/logs", params={"follow": "false", "backlog": "1000"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert "data: CAMPAIGN started" in resp.text
