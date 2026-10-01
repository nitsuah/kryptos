import { useMemo, useState } from "react";
import { FrontierVector, JobStatus } from "../api";
import AttackRunPanel from "../components/AttackRunPanel";
import { useDashboard } from "../shell/data";

// The P1–P22 attack queue and recent jobs on one screen: pick a vector on
// the left, read and run it top right, follow jobs bottom right.

function statusClass(s: string): string {
  return `st-${s.toLowerCase().replace(/[^a-z]+/g, "-")}`;
}

function shortName(v: FrontierVector): string {
  return v.name.replace(/^P\d+\s*[—-]\s*/, "");
}

function when(ts?: string | null): string {
  return ts ? ts.replace("T", " ").replace("Z", "").slice(5, 16) : "—";
}

function JobRow({ job, open, onToggle }: { job: JobStatus; open: boolean; onToggle: () => void }) {
  return (
    <li>
      <button type="button" className="row-btn job-row" aria-expanded={open} onClick={onToggle}>
        <span className={`job-status st-${job.status}`}>{job.status}</span>
        <span className="row-title">{job.attack_id}</span>
        <span className="job-meter" aria-hidden="true">
          <span style={{ width: `${Math.min(100, Math.max(0, job.progress_pct))}%` }} />
        </span>
        <span className="muted small">{when(job.created_at)}</span>
      </button>
      {open && (
        <div className="job-body">
          <p className="muted small">
            {job.progress_pct.toFixed(0)}% · {job.total_candidates.toLocaleString()} candidates
            {job.clock_time ? ` · clock ${job.clock_time}` : ""}
          </p>
          {job.error && <div className="result error">{job.error}</div>}
          {job.top_candidates.length > 0 && (
            <p className="small plaintext">best: {job.top_candidates[0].candidate_text.slice(0, 48)}</p>
          )}
          {job.summary && (
            <details className="json-details">
              <summary>Summary</summary>
              <pre>{JSON.stringify(job.summary, null, 2)}</pre>
            </details>
          )}
        </div>
      )}
    </li>
  );
}

export default function Attacks() {
  const { vectors, vectorsError, refreshVectors, jobs, jobsError, refreshJobs, status } = useDashboard();
  const [q, setQ] = useState("");
  const [selId, setSelId] = useState<string | null>(null);
  const [openJob, setOpenJob] = useState<string | null>(null);

  const running = useMemo(
    () => new Set(jobs.filter((j) => j.status === "queued" || j.status === "running").map((j) => j.attack_id)),
    [jobs],
  );

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return vectors
      .filter((v) => !needle || `${v.name} ${v.description} ${v.id} p${v.priority}`.toLowerCase().includes(needle))
      .sort((a, b) => {
        // Constraint suites first, then by priority.
        const ka = a.priority >= 21 ? a.priority - 100 : a.priority;
        const kb = b.priority >= 21 ? b.priority - 100 : b.priority;
        return ka - kb;
      });
  }, [vectors, q]);

  const selected = rows.find((v) => v.id === selId) ?? rows[0];

  return (
    <div className="fit attacks-layout">
      <section className="pane attacks-list">
        <div className="toolbar">
          <input
            type="search"
            className="search"
            placeholder="Search attacks (name, P-number)…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Search attacks"
          />
          <span className="muted small">
            {vectors.length} · {running.size} running
          </span>
        </div>
        <ul className="rows" aria-label="Attack vectors">
          {vectors.length === 0 &&
            (vectorsError ? (
              <li className="muted">
                Attack registry unavailable: {vectorsError}{" "}
                <button type="button" className="link-button" onClick={refreshVectors}>
                  retry
                </button>
              </li>
            ) : (
              <li className="muted">Loading the attack registry…</li>
            ))}
          {rows.map((v) => (
            <li key={v.id}>
              <button
                type="button"
                className="row-btn"
                aria-pressed={selected?.id === v.id}
                onClick={() => setSelId(v.id)}
              >
                <span className="prio">P{v.priority}</span>
                <span className="row-title">{shortName(v)}</span>
                {running.has(v.id) && <span className="live-dot" aria-label="job running" />}
                <span className={`vector-status ${statusClass(v.status)}`}>{v.status}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="pane attacks-detail">
        {selected ? (
          <>
            <h3>
              P{selected.priority} · {shortName(selected)}
            </h3>
            <p className="detail-text">{selected.description}</p>
            <p className="muted small">
              {selected.layer_count} layer{selected.layer_count === 1 ? "" : "s"}
              {selected.combo_estimate != null && ` · ~${selected.combo_estimate.toLocaleString()} combinations`}
              {" · "}
              <span className={statusClass(selected.status)}>{selected.status}</span>
            </p>
            {selected.runnable ? (
              <AttackRunPanel key={selected.id} vector={selected} onJobChange={refreshJobs} />
            ) : (
              <p className="muted small">Not runnable from the dashboard.</p>
            )}
          </>
        ) : (
          <p className="muted">Pick an attack.</p>
        )}
      </section>

      <section className="pane attacks-jobs">
        <h3>
          Recent jobs
          <button type="button" className="link-button" onClick={refreshJobs}>
            refresh
          </button>
        </h3>
        {jobsError && <div className="result error">Jobs unavailable: {jobsError}</div>}
        {jobs.length === 0 && !jobsError ? (
          <p className="muted small">
            No jobs yet.
            {status && !status.db_enabled && " Without DATABASE_URL, job history lives in memory until restart."}
          </p>
        ) : (
          <ul className="rows">
            {jobs.map((j) => (
              <JobRow
                key={j.job_id}
                job={j}
                open={openJob === j.job_id}
                onToggle={() => setOpenJob(openJob === j.job_id ? null : j.job_id)}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
