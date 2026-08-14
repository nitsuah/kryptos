import { useState, useEffect, useRef } from "react";
import { api, FrontierVector, JobStatus, AttackCandidate } from "../api";

interface Props {
  vector: FrontierVector;
}

const STATUS_LABELS: Record<string, string> = {
  queued: "Queued",
  running: "Running…",
  complete: "Complete",
  error: "Error",
  eureka: "🚨 EUREKA",
};

function CandidateRow({ c }: { c: AttackCandidate }) {
  const params = [c.alpha_name, c.n_cols != null ? `${c.n_cols}col` : null, c.variant, c.key].filter(Boolean).join(" / ");
  return (
    <tr>
      <td style={{ fontFamily: "monospace", fontSize: "11px", wordBreak: "break-all" }}>
        {c.candidate_text.slice(0, 40)}{c.candidate_text.length > 40 ? "…" : ""}
      </td>
      <td style={{ textAlign: "center" }}>{c.keyword_hits}</td>
      <td style={{ textAlign: "center" }}>{c.instructional_score != null ? c.instructional_score.toFixed(2) : "—"}</td>
      <td style={{ fontSize: "11px" }}>{c.clock_time ?? c.source ?? "—"}</td>
      <td style={{ fontSize: "11px" }}>{params || "—"}</td>
    </tr>
  );
}

export default function AttackRunPanel({ vector }: Props) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [launching, setLaunching] = useState(false);
  const [priorityOnly, setPriorityOnly] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isRunning = job?.status === "running" || job?.status === "queued";

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const startPolling = (jobId: string) => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const status = await api.jobStatus(jobId);
        setJob(status);
        if (status.status !== "running" && status.status !== "queued") {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, 1500);
  };

  const handleRun = async () => {
    setLaunching(true);
    try {
      const result = await api.runAttack({
        attack_id: vector.id,
        priority_only: priorityOnly,
        max_perms_per_grid: 720,
      });
      setJob(result);
      if (result.status === "running" || result.status === "queued") {
        startPolling(result.job_id);
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setJob({
        job_id: "",
        attack_id: vector.id,
        status: "error",
        progress_pct: 0,
        clock_time: null,
        total_candidates: 0,
        top_candidates: [],
        summary: null,
        error: msg,
      });
    } finally {
      setLaunching(false);
    }
  };

  const statusColor = job
    ? job.status === "complete"
      ? "var(--accent)"
      : job.status === "eureka"
        ? "#ff4444"
        : job.status === "error"
          ? "#ff8800"
          : job.status === "running"
            ? "var(--warning)"
            : "var(--text)"
    : undefined;

  return (
    <div style={{ marginTop: "16px" }}>
      {/* Launch controls */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={priorityOnly}
            onChange={(e) => setPriorityOnly(e.target.checked)}
            disabled={isRunning || launching}
          />
          Priority timestamps only (13:00 + 19:00)
        </label>
        <button
          className="small-button"
          onClick={handleRun}
          disabled={isRunning || launching || !vector.runnable}
          style={{ minWidth: "120px" }}
        >
          {launching ? "Launching…" : isRunning ? "Running…" : "▶ Run Attack"}
        </button>
        {job && (
          <span style={{ fontSize: "12px", color: statusColor }}>
            {STATUS_LABELS[job.status] ?? job.status}
          </span>
        )}
      </div>

      {/* Progress bar */}
      {job && (job.status === "running" || job.status === "queued") && (
        <div style={{ marginTop: "10px" }}>
          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>
            Clock state: {job.clock_time ?? "—"} &nbsp;·&nbsp;
            {job.total_candidates.toLocaleString()} candidates checked
          </div>
          <div className="progress-bar-container">
            <div className="progress-bar" style={{ width: `${job.progress_pct}%` }} />
          </div>
          <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
            {job.progress_pct.toFixed(1)}% complete
          </div>
        </div>
      )}

      {/* Error */}
      {job?.status === "error" && (
        <div style={{ marginTop: "10px", color: "#ff8800", fontSize: "12px", fontFamily: "monospace" }}>
          Error: {job.error}
        </div>
      )}

      {/* Eureka banner */}
      {job?.status === "eureka" && (
        <div style={{
          marginTop: "12px",
          padding: "12px",
          border: "2px solid #ff4444",
          borderRadius: "4px",
          background: "rgba(255,68,68,0.1)",
          color: "#ff4444",
          fontWeight: "bold",
          fontSize: "14px",
          animation: "pulse 1s ease-in-out infinite alternate",
        }}>
          🚨 EUREKA SIGNAL — All 4 cribs matched!
          {job.summary && (
            <div style={{ fontSize: "11px", marginTop: "6px", fontWeight: "normal", fontFamily: "monospace" }}>
              Snapshot: {(job.summary as { snapshot_path?: string }).snapshot_path ?? "—"}
            </div>
          )}
        </div>
      )}

      {/* Top candidates */}
      {job && job.top_candidates.length > 0 && (
        <div style={{ marginTop: "14px" }}>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "6px" }}>
            Top near-misses ({job.top_candidates.length})
          </div>
          <div style={{ overflowX: "auto" }}>
            <table className="attack-table" style={{ fontSize: "11px" }}>
              <thead>
                <tr>
                  <th>Candidate (40 chars)</th>
                  <th>Hits</th>
                  <th>Score</th>
                  <th>Clock</th>
                  <th>Params</th>
                </tr>
              </thead>
              <tbody>
                {job.top_candidates.map((c, i) => (
                  <CandidateRow key={i} c={c} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Complete summary */}
      {job?.status === "complete" && (
        <div style={{ marginTop: "10px", fontSize: "12px", color: "var(--accent)" }}>
          ✓ Sweep complete — {job.total_candidates.toLocaleString()} candidates checked, null result.
        </div>
      )}
    </div>
  );
}
