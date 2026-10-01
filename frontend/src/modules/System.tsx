import { useEffect, useState } from "react";
import { Candidate, Run, apiPath, api } from "../api";
import LogTail from "../components/LogTail";
import PivotStatusPanel from "../components/PivotStatusPanel";
import { useDashboard } from "../shell/data";

// Descriptions for the Neon tables kryptos.db_schema creates. Counts come
// from /api/status, which reports whatever tables exist, so an unknown
// table still shows up (without a description).
const TABLES: Record<string, string> = {
  campaign_runs: "Candidate-generating runs",
  candidates: "Ranked candidate decryptions",
  k4_attack_jobs: "Finished attack jobs",
  k4_constraint_runs: "Crib-constraint suite runs",
  vault_payloads: "Sealed vault secrets",
  discovered_cribs: "Crib candidates with provenance",
  ops_decisions: "Strategy decision log",
  strategy_kb: "Attack knowledge",
  sanborn_timeline: "Sanborn's public statements",
  k4_research_findings: "Facts and ruled-out hypotheses",
  k4_keystream: "Per-position crib keystream",
  source_chunks: "Chunked primary sources",
};

function RunHistory({ dbEnabled, runCount }: { dbEnabled: boolean; runCount?: number }) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [top, setTop] = useState<Candidate[]>([]);
  useEffect(() => {
    if (!dbEnabled) return;
    api
      .runs(15)
      .then((r) => setRuns(r.runs))
      .catch(() => setRuns([]));
    api
      .topCandidates(5)
      .then((r) => setTop(r.candidates))
      .catch(() => setTop([]));
  }, [dbEnabled, runCount]);

  if (!dbEnabled) {
    return <p className="muted small">Run history is stored in Neon; this server has no DATABASE_URL.</p>;
  }
  return (
    <div className="scroll-y">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Cipher</th>
            <th>Stage</th>
            <th>Status</th>
            <th>Started</th>
          </tr>
        </thead>
        <tbody>
          {runs.length === 0 && (
            <tr>
              <td colSpan={5} className="muted">
                No runs recorded.
              </td>
            </tr>
          )}
          {runs.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.cipher_label ?? "—"}</td>
              <td>{r.stage ?? "—"}</td>
              <td>{r.status ?? "—"}</td>
              <td className="muted">{r.started_at ? r.started_at.replace("T", " ").slice(0, 16) : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {top.length > 0 && (
        <p className="small">
          Best stored candidate: <span className="plaintext">{top[0].text.slice(0, 48)}</span>{" "}
          <span className="muted">(scores before 2026-09-28 used placeholder n-gram tables)</span>
        </p>
      )}
    </div>
  );
}

export default function System() {
  const { status, statusError, online } = useDashboard();
  const base = apiPath("") || window.location.origin;
  const counts = status?.table_counts ?? {};
  const names = Array.from(new Set([...Object.keys(counts), ...Object.keys(TABLES)])).sort();
  const db = status?.db_enabled === true;

  return (
    <div className="fit system-layout">
      <section className="pane sys-conn">
        <h3>Connection</h3>
        <dl className="kv">
          <dt>API</dt>
          <dd>
            <span className={`dot ${online ? "green" : "red"}`} aria-hidden="true" /> {online ? "reachable" : "unreachable"}
          </dd>
          <dt>Base</dt>
          <dd>
            <code>{base}</code>
          </dd>
          <dt>Database</dt>
          <dd>
            <span className={`dot ${db ? "green" : "grey"}`} aria-hidden="true" />{" "}
            {status === null ? "unknown" : db ? "Neon connected" : "not configured"}
          </dd>
        </dl>
        {statusError && <div className="result error">/api/status failed: {statusError}</div>}
        <div className="scroll-y">
          <table>
            <thead>
              <tr>
                <th>Table</th>
                <th className="num">Rows</th>
              </tr>
            </thead>
            <tbody>
              {names.map((n) => (
                <tr key={n} title={TABLES[n] ?? ""}>
                  <td>
                    <code>{n}</code>
                  </td>
                  <td className="num">{db ? (counts[n] ?? 0).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="pane sys-log">
        <h3>Live log</h3>
        <LogTail />
      </section>

      <section className="pane sys-runs">
        <h3>Run history</h3>
        <RunHistory dbEnabled={db} runCount={status?.table_counts?.campaign_runs} />
      </section>

      <section className="pane sys-pivot">
        <h3>Physical / geometric pivot</h3>
        <PivotStatusPanel />
      </section>
    </div>
  );
}
