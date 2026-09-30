/**
 * Physical/Geometric Pivot summary (GET /api/k4/attacks/pivot-status):
 * candidates tested, the hypothesis graph's edges and the CIA→Berlin
 * bearings. The graph is shown as a table; its Mermaid rendering lives in
 * docs/analysis/K4_ACTIVE_RESEARCH.md.
 */
import { useEffect, useState } from "react";
import { api, PivotStatusResponse } from "../api";

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

  if (error) return <div className="result error">Pivot status unavailable: {error}</div>;
  if (!status) return <p className="muted small">Loading…</p>;

  const edges = Object.entries(status.hypothesis_graph.edges);
  const nulls = edges.filter(([, e]) => e.status === "null").length;
  const eureka = edges.filter(([, e]) => e.status === "eureka").length;

  return (
    <div className="pivot">
      <dl className="stat-line">
        <div>
          <dt>Candidates</dt>
          <dd>{status.total_candidates_tested.toLocaleString()}</dd>
        </div>
        <div>
          <dt>Edges null</dt>
          <dd>
            {nulls} / {edges.length}
          </dd>
        </div>
        <div>
          <dt>Breakthroughs</dt>
          <dd className={eureka ? "st-eureka" : ""}>{eureka}</dd>
        </div>
        <div>
          <dt>CIA → Berlin</dt>
          <dd>{formatDeg(status.bearings.cia_berlin_geodesic.forward_azimuth_deg)}</dd>
        </div>
      </dl>
      <div className="scroll-y">
        <table>
          <thead>
            <tr>
              <th>Edge</th>
              <th>Status</th>
              <th>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {edges.map(([key, edge]) => (
              <tr key={key}>
                <td>
                  <code>{key.replace("->", " → ")}</code>
                </td>
                <td className={`st-${edge.status.replace(/_/g, "-")}`}>{edge.status}</td>
                <td className="muted">{edge.evidence || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small">Lodestone deflection: {status.bearings.kryptos_lodestone_deflection.note}</p>
    </div>
  );
}
