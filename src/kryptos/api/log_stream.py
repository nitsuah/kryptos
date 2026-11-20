"""Server-Sent Events log tail for the dashboard.

A process-wide :class:`LogBuffer` (a bounded, thread-safe ring) is fed by a
:class:`logging.Handler` attached to the ``kryptos`` logger. The SSE endpoint
replays the recent backlog and then polls the buffer for new lines, so log
records emitted from worker threads need no asyncio/thread coordination — the
generator just reads the latest sequence numbers on each tick.

Every record is stored twice: the full formatted line (with tracebacks) and a
*public* line that is safe for anonymous dashboard visitors. The public line is
the first line of the message only, with exception arguments reduced to their
class name, URL credentials masked, and tracebacks withheld. The full view is
only served to callers presenting ``KRYPTOS_LOG_TOKEN``; full details also go
to the server's stderr (Render logs), never to anonymous clients.
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import re
import threading
from collections import deque
from collections.abc import AsyncIterator

DEFAULT_CAPACITY = 1000
_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_HANDLER_MARKER = "_kryptos_sse_handler"
_PUBLIC_MAX_CHARS = 300
_WITHHELD = " [details withheld]"

# scheme://user:password@host -> scheme://***@host
_URL_CREDS = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://)[^/\s:@]+(?::[^/\s@]*)?@")
# key=value / key: value pairs whose key looks secret. Keys may be quoted (JSON / dict
# reprs), and an auth scheme plus its credential ("Bearer abc") is masked as one value.
_SECRET_KV = re.compile(
    r"(?i)([\"']?)\b([a-z0-9_-]*(?:password|passwd|secret|token|api[_-]?key|authorization|dsn)[a-z0-9_-]*)\1"
    r"(\s*[=:]\s*)((?:bearer|basic|digest|token)\s+[^\s\"',}]+|\"[^\"]*\"|'[^']*'|[^\s,}]+)"
)


def redact_public(text: str) -> str:
    """Reduce an arbitrary log line to a one-line, credential-masked public form."""
    lines = (text or "").splitlines() or [""]
    first = lines[0]
    first = _URL_CREDS.sub(r"\1***@", first)
    first = _SECRET_KV.sub(r"\1\2\1\3***", first)
    withheld = len(lines) > 1
    if len(first) > _PUBLIC_MAX_CHARS:
        first = first[:_PUBLIC_MAX_CHARS] + "…"
        withheld = True
    return first + (_WITHHELD if withheld else "")


class LogBuffer:
    """Bounded ring of formatted log lines, each tagged with a monotonic seq."""

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self._buf: deque[tuple[int, str, str]] = deque(maxlen=capacity)
        self._seq = 0
        self._lock = threading.Lock()

    def append(self, line: str, public: str | None = None) -> int:
        """Store ``line`` (full view) plus its public form (redacted if not given)."""
        public_line = redact_public(line) if public is None else public
        with self._lock:
            self._seq += 1
            self._buf.append((self._seq, line, public_line))
            return self._seq

    def latest_seq(self) -> int:
        with self._lock:
            return self._seq

    @staticmethod
    def _pick(entry: tuple[int, str, str], public: bool) -> tuple[int, str]:
        seq, full, pub = entry
        return (seq, pub if public else full)

    def tail(self, count: int, public: bool = False) -> list[tuple[int, str]]:
        """Return up to ``count`` most-recent entries (oldest first)."""
        with self._lock:
            items = list(self._buf)
        items = items[-count:] if count > 0 else []
        return [self._pick(e, public) for e in items]

    def since(self, seq: int, public: bool = False) -> list[tuple[int, str]]:
        """Return entries with sequence strictly greater than ``seq``."""
        with self._lock:
            return [self._pick(e, public) for e in self._buf if e[0] > seq]


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
            self.buffer.append(self.format(record), self.format_public(record))
        except Exception:  # noqa: BLE001 - logging must never raise
            self.handleError(record)

    def format_public(self, record: logging.LogRecord) -> str:
        """One-line public form: exception args become their class name, no traceback."""
        args = record.args
        if isinstance(args, tuple):
            args = tuple(f"<{type(a).__name__}>" if isinstance(a, BaseException) else a for a in args)
        elif isinstance(args, dict):
            args = {k: (f"<{type(v).__name__}>" if isinstance(v, BaseException) else v) for k, v in args.items()}
        try:
            message = str(record.msg) % args if args else str(record.msg)
        except Exception:  # noqa: BLE001 - malformed format string
            message = str(record.msg)
        stamp = logging.Formatter().formatTime(record)
        line = redact_public(f"{stamp} {record.levelname} {record.name}: {message}")
        if (record.exc_info or record.exc_text or record.stack_info) and not line.endswith(_WITHHELD):
            line += _WITHHELD
        return line


def log_token() -> str | None:
    """The admin token that unlocks the full (unredacted) log view, if configured."""
    token = (os.getenv("KRYPTOS_LOG_TOKEN") or "").strip()
    return token or None


def public_log_mode() -> str:
    """``redacted`` (default) serves anonymous visitors the public view; ``off`` refuses them."""
    mode = (os.getenv("KRYPTOS_LOG_STREAM_PUBLIC") or "redacted").strip().lower()
    return "off" if mode in {"off", "0", "false", "no", "disabled"} else "redacted"


def token_matches(presented: str | None) -> bool:
    expected = log_token()
    if not expected or not presented:
        return False
    return hmac.compare_digest(presented.encode(), expected.encode())


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
    public: bool = False,
) -> AsyncIterator[str]:
    """Yield SSE frames: the recent backlog, then (if ``follow``) live lines.

    ``is_disconnected`` is an awaitable returning True when the client has gone
    away (e.g. ``starlette.Request.is_disconnected``). Heartbeat comments keep
    proxies from closing an idle connection.
    """
    buf = buffer or LOG_BUFFER

    last_seq = 0
    for seq, line in buf.tail(backlog, public=public):
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
        new_entries = buf.since(last_seq, public=public)
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
    "log_token",
    "public_log_mode",
    "redact_public",
    "token_matches",
]
