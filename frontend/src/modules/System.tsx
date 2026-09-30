import { apiPath } from "../api";
import PivotStatusPanel from "../components/PivotStatusPanel";
import { useDashboard } from "../shell/data";

// Descriptions for the Neon tables kryptos.db_schema creates. Counts come
// from /api/status, which reports whatever tables exist, so an unknown
// table still shows up (without a description).
const TABLES: Record<string, string> = {
  campaign_runs: "One row per candidate-generating run",
  candidates: "Ranked candidate decryptions per run",
  k4_attack_jobs: "Finished attack jobs (survive a restart)",
  k4_constraint_runs: "Crib-constraint suite summaries (ledger latest run)",
  vault_payloads: "Sealed vault secrets",
  discovered_cribs: "Crib candidates with source provenance",
  ops_decisions: "Strategy decision log",
  strategy_kb: "Accumulated attack knowledge",
  sanborn_timeline: "Sanborn's public statements",
  k4_research_findings: "Confirmed facts and ruled-out hypotheses",
  k4_keystream: "Per-position crib keystream",
  source_chunks: "Chunked primary sources",
};

export default function System() {
  const { status, statusError, online } = useDashboard();
  const base = apiPath("") || window.location.origin;
  const counts = status?.table_counts ?? {};
  const names = Array.from(new Set([...Object.keys(counts), ...Object.keys(TABLES)])).sort();

  return (
    <div className="grid system-grid">
      <section className="sub">
        <h3>Connection</h3>
        <dl className="kv">
          <dt>API</dt>
          <dd>
            <span className={`dot ${online ? "green" : "red"}`} aria-hidden="true" /> {online ? "reachable" : "unreachable"}
          </dd>
          <dt>Base URL</dt>
          <dd>
            <code>{base}</code>
          </dd>
          <dt>Database</dt>
          <dd>
            <span className={`dot ${status?.db_enabled ? "green" : "grey"}`} aria-hidden="true" />{" "}
            {status === null ? "unknown" : status.db_enabled ? "Neon connected" : "not configured"}
          </dd>
          <dt>Latest run</dt>
          <dd>
            {status?.latest_run
              ? `#${status.latest_run.id} ${status.latest_run.cipher_label ?? ""} ${status.latest_run.status ?? ""}`
              : "—"}
          </dd>
        </dl>
        {statusError && <div className="result error">/api/status failed: {statusError}</div>}
        {status && !status.db_enabled && (
          <p className="muted small">
            Set <code>DATABASE_URL</code> and run <code>kryptos db-init</code> to enable run history, job persistence
            and the vault.
          </p>
        )}
      </section>

      <section className="sub">
        <h3>Tables</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Table</th>
                <th>Rows</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {names.map((n) => (
                <tr key={n}>
                  <td>
                    <code>{n}</code>
                  </td>
                  <td className="num">{status?.db_enabled ? (counts[n] ?? 0).toLocaleString() : "—"}</td>
                  <td className="muted">{TABLES[n] ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="span-2">
        <PivotStatusPanel />
      </div>
    </div>
  );
}
