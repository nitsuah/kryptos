import { useEffect, useRef, useState } from "react";

type ConnState = "connecting" | "live" | "stopped" | "error";

const MAX_LINES = 1000;
const BACKLOG = 200;

// Live tail of the kryptos backend log via the SSE endpoint
// (GET /api/stream/logs, src/kryptos/api/log_stream.py). EventSource auto-
// reconnects on transient drops; the heartbeat comments the server sends keep
// idle proxies from closing the stream.
export default function LogTail() {
  const [lines, setLines] = useState<string[]>([]);
  const [state, setState] = useState<ConnState>("stopped");
  const [running, setRunning] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);
  const esRef = useRef<EventSource | null>(null);
  const bodyRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!running) {
      esRef.current?.close();
      esRef.current = null;
      setState("stopped");
      return;
    }

    setState("connecting");
    const es = new EventSource(`/api/stream/logs?backlog=${BACKLOG}&follow=true`);
    esRef.current = es;

    es.onopen = () => setState("live");
    es.onmessage = (e) => {
      setLines((prev) => {
        const next = prev.concat(e.data.split("\n"));
        return next.length > MAX_LINES ? next.slice(next.length - MAX_LINES) : next;
      });
    };
    es.onerror = () => {
      // EventSource retries on its own; surface the gap but keep the connection.
      setState("error");
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [running]);

  // Pin to the newest line as it arrives, unless the user opted out.
  useEffect(() => {
    if (autoScroll && bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [lines, autoScroll]);

  const label =
    state === "live"
      ? "● live"
      : state === "connecting"
        ? "○ connecting…"
        : state === "error"
          ? "● reconnecting…"
          : "○ stopped";
  const labelClass = state === "error" ? "error" : state === "live" ? "" : "muted";

  return (
    <div className="logtail">
      <div className="logtail-bar">
        <span className={labelClass}>{label}</span>
        <span className="muted">{lines.length} lines</span>
        <label className="logtail-toggle">
          <input type="checkbox" checked={autoScroll} onChange={(e) => setAutoScroll(e.target.checked)} />
          auto-scroll
        </label>
        <button type="button" onClick={() => setLines([])} disabled={lines.length === 0}>
          Clear
        </button>
        <button type="button" onClick={() => setRunning((r) => !r)}>
          {running ? "Pause" : "Resume"}
        </button>
      </div>
      <div className="logtail-body" ref={bodyRef}>
        {lines.length === 0 ? (
          <div className="muted">No log lines yet.</div>
        ) : (
          lines.map((line, i) => (
            <div key={i} className="logtail-line">
              {line}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
