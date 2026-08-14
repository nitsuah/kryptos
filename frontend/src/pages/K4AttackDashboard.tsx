import { useState, useEffect } from "react";
import K4AttackDetails from "./K4AttackDetails";
import AttackVectorGraph from "../components/AttackVectorGraph";
import AttackRunPanel from "../components/AttackRunPanel";
import FormField from "../components/FormField";
import { api, AttackVector, FrontierVector } from "../api";

const STATUS_COLORS: Record<string, string> = {
  "Active": "var(--warning)",
  "Deferred": "var(--text-muted)",
  "Ruled Out": "var(--accent)",
  "In Progress": "var(--warning)",
  "Planned": "var(--text)",
};

const PRIORITY_BADGE: Record<number, string> = {
  1: "#e74c3c",
  2: "#e67e22",
  3: "#f1c40f",
  4: "#f1c40f",
  5: "#2ecc71",
  6: "#2ecc71",
  7: "#2ecc71",
};

export default function K4AttackDashboard() {
  const [selectedVector, setSelectedVector] = useState<AttackVector | null>(null);
  const [filter, setFilter] = useState("");
  const [attackVectors, setAttackVectors] = useState<AttackVector[]>([]);
  const [frontierVectors, setFrontierVectors] = useState<FrontierVector[]>([]);
  const [expandedFrontier, setExpandedFrontier] = useState<string | null>("p1_three_layer");

  useEffect(() => {
    api.attackVectors().then((res) => setAttackVectors(res.vectors));
    api.frontierVectors().then((res) => setFrontierVectors(res.vectors));
  }, []);

  const filteredVectors = attackVectors.filter((v) =>
    v.name.toLowerCase().includes(filter.toLowerCase())
  );
  const ruledOutCount = attackVectors.filter((v) => v.status === "Ruled Out").length;
  const frontierActive = frontierVectors.filter((v) => v.status === "Active").length;
  const progress = attackVectors.length > 0 ? (ruledOutCount / attackVectors.length) * 100 : 0;

  return (
    <div className="page-container" style={{ position: "relative" }}>
      <div className="scan-line" />
      {selectedVector && (
        <K4AttackDetails vector={selectedVector} onClose={() => setSelectedVector(null)} />
      )}

      <h2>K4 ATTACK VECTOR FINGERPRINT</h2>

      <div className="dashboard-grid">
        {/* Controls panel */}
        <div className="panel">
          <h2>Analysis Controls</h2>
          <div className="body">
            <div className="row">
              <FormField label="Filter Vectors" style={{ flex: 1 }}>
                <input
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  placeholder="Search vectors…"
                />
              </FormField>
            </div>
            <div className="progress-container">
              <div className="label">Attack Surface Coverage</div>
              <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
              </div>
              <p>
                {ruledOutCount} / {attackVectors.length} vectors ruled out &nbsp;·&nbsp;
                <span style={{ color: "var(--warning)" }}>{frontierActive} frontier active</span>
              </p>
            </div>
          </div>
        </div>

        {/* Ruled-out registry */}
        <div className="panel">
          <h2>Attack Vector Registry</h2>
          <table className="attack-table">
            <thead>
              <tr>
                <th>Attack Vector</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredVectors.map((v) => (
                <tr
                  key={v.name}
                  onClick={() => setSelectedVector(v)}
                  className="clickable-row"
                >
                  <td>{v.name}</td>
                  <td
                    className={`status-${v.status.toLowerCase().replace(/\s+/g, "-")}`}
                    style={{ color: STATUS_COLORS[v.status] }}
                  >
                    {v.status}
                  </td>
                  <td>
                    <button className="small-button">View Details</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <AttackVectorGraph data={attackVectors} />
      </div>

      {/* Frontier P1-P10 panel */}
      {frontierVectors.length > 0 && (
        <div className="panel" style={{ marginTop: "20px" }}>
          <h2>Frontier Attack Queue — P1–P10</h2>
          <div className="body">
            {frontierVectors.map((v) => {
              const isExpanded = expandedFrontier === v.id;
              return (
                <div
                  key={v.id}
                  style={{
                    borderBottom: "1px solid var(--border)",
                    paddingBottom: "12px",
                    marginBottom: "12px",
                  }}
                >
                  {/* Header row */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      cursor: "pointer",
                    }}
                    onClick={() => setExpandedFrontier(isExpanded ? null : v.id)}
                  >
                    <span
                      style={{
                        display: "inline-block",
                        width: "22px",
                        height: "22px",
                        borderRadius: "50%",
                        background: PRIORITY_BADGE[v.priority] ?? "var(--text-muted)",
                        color: "#000",
                        fontWeight: "bold",
                        fontSize: "11px",
                        textAlign: "center",
                        lineHeight: "22px",
                        flexShrink: 0,
                      }}
                    >
                      {v.priority}
                    </span>
                    <span style={{ fontWeight: "bold", flex: 1 }}>{v.name}</span>
                    <span
                      style={{
                        fontSize: "11px",
                        color: STATUS_COLORS[v.status] ?? "var(--text)",
                        minWidth: "64px",
                        textAlign: "right",
                      }}
                    >
                      {v.status}
                    </span>
                    {v.combo_estimate != null && (
                      <span style={{ fontSize: "11px", color: "var(--text-muted)", minWidth: "90px", textAlign: "right" }}>
                        ~{v.combo_estimate.toLocaleString()} combos
                      </span>
                    )}
                    <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </div>

                  {/* Expanded detail */}
                  {isExpanded && (
                    <div style={{ marginTop: "10px", paddingLeft: "32px" }}>
                      <p style={{ fontSize: "13px", color: "var(--text-muted)", margin: "0 0 8px" }}>
                        {v.description}
                      </p>
                      <div style={{ fontSize: "12px", marginBottom: "8px" }}>
                        <span style={{ color: "var(--text-muted)" }}>Layers:</span>{" "}
                        {v.layer_count} &nbsp;·&nbsp;
                        {v.runnable ? (
                          <span style={{ color: "var(--accent)" }}>Runnable</span>
                        ) : (
                          <span style={{ color: "var(--text-muted)" }}>Not yet implemented</span>
                        )}
                      </div>
                      {v.runnable && <AttackRunPanel vector={v} />}
                      {!v.runnable && v.status === "Active" && (
                        <div
                          style={{
                            fontSize: "12px",
                            color: "var(--text-muted)",
                            fontStyle: "italic",
                            marginTop: "4px",
                          }}
                        >
                          Implementation pending — see TASKS.md
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
