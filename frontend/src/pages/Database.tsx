import { StatusResponse } from "../api";

// Internal admin view (docs/analysis/K4-FRONTEND.md section 4): connection
// status and per-table row counts, read from /api/status. No user-facing data.

const TABLES = [
  { name: "campaign_runs", desc: "One row per candidate-generating run" },
  { name: "candidates", desc: "Ranked candidate decryptions per run" },
  { name: "discovered_cribs", desc: "Crib candidates with source provenance" },
  { name: "ops_decisions", desc: "Strategy decision log" },
  { name: "strategy_kb", desc: "Accumulated attack knowledge" },
];

export default function Database({ status }: { status: StatusResponse | null }) {
  const statusAvailable = status !== null;
  const enabled = status?.db_enabled === true;
  const counts = status?.table_counts ?? {};
  const connectionLabel = !statusAvailable ? "Status unavailable" : enabled ? "Neon connected" : "No database";

  return (
    <>
      <div className="panel">
        <h2>Connection</h2>
        <div className="body">
          <div className="row" style={{ alignItems: "center" }}>
            <span className="pip">
              <span className={`dot ${enabled ? "green" : "grey"}`} />
              {connectionLabel}
            </span>
          </div>
          {!statusAvailable && (
            <div className="banner" style={{ marginTop: 10 }}>
              Database status is unavailable because the API status request did not complete. This does not indicate
              whether Neon or its tables are configured.
            </div>
          )}
          {statusAvailable && !enabled && (
            <div className="banner" style={{ marginTop: 10 }}>
              DATABASE_URL is not configured. Set it (e.g. a Neon connection string) and run{" "}
              <code>kryptos db-init</code> to create the tables.
            </div>
          )}
        </div>
      </div>

      <div className="panel">
        <h2>Tables</h2>
        <div className="body">
          <table>
            <thead>
              <tr>
                <th>Table</th>
                <th>Rows</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {TABLES.map((t) => (
                <tr key={t.name}>
                  <td>{t.name}</td>
                  <td style={{ color: "var(--accent)" }}>
                    {!statusAvailable ? "Unavailable" : enabled ? (counts[t.name] ?? 0) : "—"}
                  </td>
                  <td className="muted">{t.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel">
        <h2>Environment</h2>
        <div className="body">
          <table>
            <tbody>
              <tr>
                <td>DATABASE_URL</td>
                <td className="muted">Neon/Postgres connection string (read by kryptos.db)</td>
              </tr>
              <tr>
                <td>
                  <code>kryptos db-init</code>
                </td>
                <td className="muted">Creates the tables above idempotently (kryptos.db_schema)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
