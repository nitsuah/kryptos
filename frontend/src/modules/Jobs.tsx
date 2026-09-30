import { useState } from "react";
import { JobStatus } from "../api";
import { useDashboard } from "../shell/data";

function when(ts?: string | null): string {
  return ts ? ts.replace("T", " ").replace("Z", "").slice(0, 19) : "—";
}

function JobRow({ job, open, onToggle }: { job: JobStatus; open: boolean; onToggle: () => void }) {
  const active = job.status === "queued" || job.status === "running";
  return (
    <li className={`job st-${job.status}`}>
      <button type="button" className="job-head" aria-expanded={open} onClick={onToggle}>
        <span className={`job-status st-${job.status}`}>{job.status}</span>
        <span className="job-attack">{job.attack_id}</span>
        <span className="job-meter" aria-hidden="true">
          <span style={{ width: `${Math.min(100, Math.max(0, job.progress_pct))}%` }} />
        </span>
        <span className="job-when muted">{when(job.created_at)}</span>
      </button>
      {open && (
        <div className="job-body">
          <p className="muted small">
            job {job.job_id} · {job.progress_pct.toFixed(1)}% · {job.total_candidates.toLocaleString()} candidates
            {job.clock_time ? ` · clock ${job.clock_time}` : ""}
            {job.updated_at ? ` · updated ${when(job.updated_at)}` : ""}
          </p>
          {active && <p className="small">Still running; this row refreshes every few seconds.</p>}
          {job.error && <div className="result error">{job.error}</div>}
          {job.top_candidates.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Hits</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {job.top_candidates.slice(0, 10).map((c, i) => (
                  <tr key={i}>
                    <td className="plaintext">{c.candidate_text.slice(0, 48)}</td>
                    <td>{c.keyword_hits}</td>
                    <td>{c.instructional_score != null ? c.instructional_score.toFixed(2) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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

// Recent attack jobs from GET /api/k4/attacks/jobs (in-memory plus Neon).
export default function Jobs() {
  const { jobs, jobsError, refreshJobs, status } = useDashboard();
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <div className="sub">
      <div className="toolbar">
        <span className="muted small">
          {jobs.length} recent job{jobs.length === 1 ? "" : "s"}
          {status && !status.db_enabled && " · in memory only (no DATABASE_URL), cleared on restart"}
        </span>
        <button type="button" onClick={refreshJobs}>
          Refresh
        </button>
      </div>
      {jobsError && <div className="result error">Jobs unavailable: {jobsError}</div>}
      {jobs.length === 0 && !jobsError ? (
        <p className="muted">No attack jobs yet. Start one from Attacks.</p>
      ) : (
        <ul className="job-list">
          {jobs.map((j) => (
            <JobRow
              key={j.job_id}
              job={j}
              open={openId === j.job_id}
              onToggle={() => setOpenId(openId === j.job_id ? null : j.job_id)}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
