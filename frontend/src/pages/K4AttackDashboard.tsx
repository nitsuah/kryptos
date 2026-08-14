import { useState, useEffect } from "react";
import K4AttackDetails from "./K4AttackDetails";
import AttackVectorGraph from "../components/AttackVectorGraph";
import AttackRunPanel from "../components/AttackRunPanel";
import BerlinClock from "../components/BerlinClock";
import K4CipherVisualizer from "../components/K4CipherVisualizer";
import FormField from "../components/FormField";
import { api, AttackVector, FrontierVector } from "../api";

const STATUS_COLORS: Record<string, string> = {
  "Active": "var(--warning)",
  "Deferred": "var(--text-muted)",
  "Ruled Out": "var(--accent)",
  "In Progress": "var(--warning)",
  "Planned": "var(--text)",
};

function priorityClass(p: number): string {
  if (p === 1) return "priority-p1";
  if (p === 2) return "priority-p2";
  if (p <= 7)  return "priority-p3";
  return "priority-p8";
}

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

      {/* ── Hero Section ── */}
      <div className="k4-hero">
        {/* Left: live Berlin Clock */}
        <div className="k4-hero-clocks">
          <div>
            <BerlinClock size="md" showLabel />
            <div className="clock-label">LIVE · BERLIN CLOCK</div>
          </div>
        </div>

        {/* Center: K4 cipher with crib highlights */}
        <div className="k4-hero-cipher">
          <h3 className="section-title-glow">
            K4 CIPHERTEXT — 97 CHARACTERS
          </h3>
          <div className="cipher-scroll">
            <K4CipherVisualizer />
          </div>
          <div style={{ marginTop: "10px", fontSize: "11px", color: "var(--text)", opacity: 0.5, letterSpacing: "1px" }}>
            KRYPTOS · LANGLEY VA · SCULPTOR JIM SANBORN · COMMISSIONED 1990
          </div>
        </div>

        {/* Right: CIA timestamp clocks */}
        <div className="k4-hero-clocks">
          <div>
            <BerlinClock staticTime="13:00:00" size="sm" showLabel />
            <div className="clock-label">CIA EST · 13:00</div>
          </div>
          <div>
            <BerlinClock staticTime="19:00:00" size="sm" showLabel />
            <div className="clock-label">BERLIN CET · 19:00</div>
          </div>
        </div>
      </div>

      {/* ── Stats strip ── */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "16px", flexWrap: "wrap" }}>
        {[
          { label: "Ruled Out", value: ruledOutCount, color: "var(--accent)" },
          { label: "Total Vectors", value: attackVectors.length, color: "var(--text)" },
          { label: "Frontier Active", value: frontierActive, color: "var(--warning)" },
          { label: "Coverage", value: `${progress.toFixed(0)}%`, color: "var(--highlight)" },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="card"
            style={{ minWidth: "130px", flex: "1 1 130px" }}
          >
            <div className="label">{label}</div>
            <div className="value" style={{ color, fontSize: "20px" }}>{value}</div>
          </div>
        ))}
      </div>

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
                  <td style={{ color: STATUS_COLORS[v.status] }}>{v.status}</td>
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

      {/* ── Frontier P1–P10 panel ── */}
      {frontierVectors.length > 0 && (
        <div className="panel" style={{ marginTop: "20px" }}>
          <h2>
            <span className="live-dot" />
            Frontier Attack Queue — P1–P10
          </h2>
          <div className="body">
            {frontierVectors.map((v) => {
              const isExpanded = expandedFrontier === v.id;
              return (
                <div
                  key={v.id}
                  className="frontier-row"
                >
                  {/* Header row */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      cursor: "pointer",
                      padding: "4px 0",
                    }}
                    onClick={() => setExpandedFrontier(isExpanded ? null : v.id)}
                  >
                    <span
                      className={priorityClass(v.priority)}
                      style={{
                        display: "inline-block",
                        width: "22px",
                        height: "22px",
                        borderRadius: "50%",
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
                      <span style={{ fontSize: "11px", color: "var(--text)", opacity: 0.5, minWidth: "90px", textAlign: "right" }}>
                        ~{v.combo_estimate.toLocaleString()} combos
                      </span>
                    )}
                    <span style={{ fontSize: "12px", opacity: 0.5 }}>
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </div>

                  {/* Expanded detail */}
                  {isExpanded && (
                    <div style={{ marginTop: "10px", paddingLeft: "32px" }}>
                      <p style={{ fontSize: "13px", color: "var(--text)", opacity: 0.7, margin: "0 0 8px" }}>
                        {v.description}
                      </p>
                      <div style={{ fontSize: "12px", marginBottom: "8px" }}>
                        <span style={{ opacity: 0.6 }}>Layers:</span>{" "}
                        {v.layer_count} &nbsp;·&nbsp;
                        {v.runnable ? (
                          <span style={{ color: "var(--accent)" }}>Runnable</span>
                        ) : (
                          <span style={{ opacity: 0.5 }}>Not yet implemented</span>
                        )}
                      </div>
                      {v.runnable && <AttackRunPanel vector={v} />}
                      {!v.runnable && (
                        <div style={{ fontSize: "12px", opacity: 0.5, fontStyle: "italic", marginTop: "4px" }}>
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
