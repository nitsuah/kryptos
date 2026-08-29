/**
 * Physical/Geometric Pivot status panel — v2 dashboard addition.
 *
 * Renders the canonical hypothesis graph (kryptos.k4.hypothesis_graph) as a
 * status table, plus a stats strip and the CIA->Berlin bearing figures.
 * Deliberately a table, not an interactive node/edge diagram — the graph
 * already has a Mermaid rendering in docs/analysis/K4_ACTIVE_RESEARCH.md;
 * duplicating that as a graph-layout widget here would need a new charting
 * dependency for marginal value over a table.
 */
import { useState, useEffect } from "react";
import { api, PivotStatusResponse, HypothesisGraphEdge } from "../api";

const EDGE_STATUS_COLORS: Record<HypothesisGraphEdge["status"], string> = {
  untested: "var(--text-muted, var(--text))",
  null: "var(--accent)",
  partial_null: "var(--warning)",
  confirmed: "var(--highlight)",
  eureka: "var(--danger)",
};

function formatDeg(deg: number): string {
  return `${deg.toFixed(2)}°`;
}

export default function PivotStatusPanel() {
  const [status, setStatus] = useState<PivotStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .pivotStatus()
      .then(setStatus)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  if (error) {
    return (
      <div className="panel" style={{ marginBottom: "16px" }}>
        <h2>Physical/Geometric Pivot</h2>
        <div className="body">
          <span style={{ color: "var(--danger)" }}>Failed to load pivot status: {error}</span>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="panel" style={{ marginBottom: "16px" }}>
        <h2>Physical/Geometric Pivot</h2>
        <div className="body">Loading…</div>
      </div>
    );
  }

  const edgeEntries = Object.entries(status.hypothesis_graph.edges);
  const eurekaCount = edgeEntries.filter(([, e]) => e.status === "eureka").length;
  const nullCount = edgeEntries.filter(([, e]) => e.status === "null").length;

  return (
    <div className="panel" style={{ marginBottom: "16px" }}>
      <h2>Physical/Geometric Pivot</h2>
      <div className="body">
        <div className="cards" style={{ marginBottom: "16px" }}>
          <div className="card">
            <div className="label">Candidates Tested</div>
            <div className="value" style={{ color: "var(--text)", fontSize: "20px" }}>
              {status.total_candidates_tested.toLocaleString()}
            </div>
          </div>
          <div className="card">
            <div className="label">Hypothesis Edges Null</div>
            <div className="value" style={{ color: "var(--accent)", fontSize: "20px" }}>
              {nullCount} / {edgeEntries.length}
            </div>
          </div>
          <div className="card">
            <div className="label">Breakthroughs</div>
            <div className="value" style={{ color: eurekaCount > 0 ? "var(--danger)" : "var(--text-muted, var(--text))", fontSize: "20px" }}>
              {eurekaCount}
            </div>
          </div>
        </div>

        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px", marginBottom: "16px" }}>
          <thead>
            <tr style={{ borderBottom: "0.5px solid var(--border)" }}>
              <th style={{ textAlign: "left", padding: "6px" }}>Edge</th>
              <th style={{ textAlign: "left", padding: "6px" }}>Status</th>
              <th style={{ textAlign: "left", padding: "6px" }}>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {edgeEntries.map(([key, edge]) => (
              <tr key={key} style={{ borderBottom: "0.5px solid var(--border)" }}>
                <td style={{ padding: "6px", fontFamily: "var(--mono)" }}>{key.replace("->", " → ")}</td>
                <td style={{ padding: "6px", color: EDGE_STATUS_COLORS[edge.status], textTransform: "uppercase" }}>
                  {edge.status}
                </td>
                <td style={{ padding: "6px", opacity: 0.75 }}>{edge.evidence || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div style={{ fontSize: "12px", opacity: 0.85 }}>
          <div>
            <strong>CIA → Berlin bearing:</strong>{" "}
            {formatDeg(status.bearings.cia_berlin_geodesic.forward_azimuth_deg)} (geodesic, precise) /{" "}
            {formatDeg(status.bearings.cia_berlin_spherical.forward_azimuth_deg)} (spherical approximation)
          </div>
          <div style={{ marginTop: "4px", color: "var(--warning)" }}>
            Kryptos lodestone deflection: {status.bearings.kryptos_lodestone_deflection.note}
          </div>
        </div>
      </div>
    </div>
  );
}
