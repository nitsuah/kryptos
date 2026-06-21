"""Server-Sent Events log tail for the dashboard.

A process-wide :class:`LogBuffer` (a bounded, thread-safe ring) is fed by a
:class:`logging.Handler` attached to the ``kryptos`` logger. The SSE endpoint
replays the recent backlog and then polls the buffer for new lines, so log
records emitted from worker threads need no asyncio/thread coordination — the
generator just reads the latest sequence numbers on each tick.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import deque
from collections.abc import AsyncIterator

DEFAULT_CAPACITY = 1000
_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_HANDLER_MARKER = "_kryptos_sse_handler"


class LogBuffer:
    """Bounded ring of formatted log lines, each tagged with a monotonic seq."""

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self._buf: deque[tuple[int, str]] = deque(maxlen=capacity)
        self._seq = 0
        self._lock = threading.Lock()

    def append(self, line: str) -> int:
        with self._lock:
            self._seq += 1
            self._buf.append((self._seq, line))
            return self._seq

    def latest_seq(self) -> int:
        with self._lock:
            return self._seq

    def tail(self, count: int) -> list[tuple[int, str]]:
        """Return up to ``count`` most-recent entries (oldest first)."""
        with self._lock:
            items = list(self._buf)
        return items[-count:] if count > 0 else []

    def since(self, seq: int) -> list[tuple[int, str]]:
        """Return entries with sequence strictly greater than ``seq``."""
        with self._lock:
            return [(s, line) for (s, line) in self._buf if s > seq]


# Process-wide buffer shared by the handler and the endpoint.
LOG_BUFFER = LogBuffer()


class SSELogHandler(logging.Handler):
    """Logging handler that appends formatted records to a :class:`LogBuffer`."""

    def __init__(self, buffer: LogBuffer, level: int = logging.INFO) -> None:
        super().__init__(level=level)
        self.buffer = buffer
        self.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        setattr(self, _HANDLER_MARKER, True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.buffer.append(self.format(record))
        except Exception:  # noqa: BLE001 - logging must never raise
            self.handleError(record)


def install_log_streaming(logger_name: str = "kryptos", buffer: LogBuffer | None = None) -> SSELogHandler:
    """Attach an :class:`SSELogHandler` to ``logger_name`` (idempotent).

    Returns the handler (existing or newly created). The logger level is lowered
    to INFO if it was higher so records actually reach the handler.
    """
    target = buffer or LOG_BUFFER
    logger = logging.getLogger(logger_name)
    for h in logger.handlers:
        if getattr(h, _HANDLER_MARKER, False):
            return h  # type: ignore[return-value]
    handler = SSELogHandler(target)
    logger.addHandler(handler)
    if logger.level == logging.NOTSET or logger.level > logging.INFO:
        logger.setLevel(logging.INFO)
    return handler


def _format_sse(line: str) -> str:
    """Encode a (possibly multi-line) log line as one SSE ``data:`` event."""
    body = "\n".join(f"data: {part}" for part in line.splitlines() or [""])
    return f"{body}\n\n"


async def log_event_stream(
    is_disconnected,
    backlog: int = 200,
    follow: bool = True,
    buffer: LogBuffer | None = None,
    poll_interval: float = 0.5,
    heartbeat_interval: float = 15.0,
) -> AsyncIterator[str]:
    """Yield SSE frames: the recent backlog, then (if ``follow``) live lines.

    ``is_disconnected`` is an awaitable returning True when the client has gone
    away (e.g. ``starlette.Request.is_disconnected``). Heartbeat comments keep
    proxies from closing an idle connection.
    """
    buf = buffer or LOG_BUFFER

    last_seq = 0
    for seq, line in buf.tail(backlog):
        last_seq = seq
        yield _format_sse(line)

    if not follow:
        return

    # Without backlog, start from the current tip so we only stream new lines.
    if last_seq == 0:
        last_seq = buf.latest_seq()

    since_heartbeat = 0.0
    while True:
        if await is_disconnected():
            return
        new_entries = buf.since(last_seq)
        if new_entries:
            for seq, line in new_entries:
                last_seq = seq
                yield _format_sse(line)
            since_heartbeat = 0.0
        else:
            since_heartbeat += poll_interval
            if since_heartbeat >= heartbeat_interval:
                since_heartbeat = 0.0
                yield ": keep-alive\n\n"
        await asyncio.sleep(poll_interval)


__all__ = [
    "LogBuffer",
    "LOG_BUFFER",
    "SSELogHandler",
    "install_log_streaming",
    "log_event_stream",
]
