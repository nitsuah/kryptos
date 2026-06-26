import React from "react";

const attackVectors = [
  { name: "Clock → Hill 2×2 Invertibility", status: "Ruled Out", artifact: "K4_CLOCK_HILL_NULL.json" },
  { name: "4-char Clock Key → Vigenère", status: "Ruled Out", artifact: "K4_CLOCK_VIG_NULL.json" },
  { name: "Non-standard Berlin Clock Sub-row", status: "Ruled Out", artifact: "K4_CLOCK_SUBROW_NULL.json" },
  { name: "Berlin Clock → Columnar Transposition", status: "Ruled Out", artifact: "K4_CLOCK_TRANS_NULL.json" },
  { name: "Beaufort Cipher Sweep", status: "Ruled Out", artifact: "K4_BEAUFORT_NULL.json" },
  { name: "Quagmire I-IV Sweep", status: "Ruled Out", artifact: "K4_QUAGMIRE_NULL.json" },
  { name: "Physical-Grid Tableau-Walk", status: "Ruled Out", artifact: "K4_PHYSICAL_GRID_NULL.json" },
  { name: "Composite (Clock/Grid/Alphabet)", status: "Ruled Out", artifact: "K4_COMPOSITE_SWEEP_NULL.json" },
];

export default function K4AttackDashboard() {
  return (
    <div className="page-container">
      <h2>K4 ATTACK VECTOR FINGERPRINT</h2>
      <div className="terminal-box">
        <table className="attack-table">
          <thead>
            <tr>
              <th>Attack Vector</th>
              <th>Status</th>
              <th>Artifact</th>
            </tr>
          </thead>
          <tbody>
            {attackVectors.map((v) => (
              <tr key={v.name}>
                <td>{v.name}</td>
                <td className="status-ruled-out">{v.status}</td>
                <td><a href={`/artifacts/${v.artifact}`}>{v.artifact}</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
