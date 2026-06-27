import { useState, useEffect } from "react";
import K4AttackDetails from "./K4AttackDetails";
import AttackVectorGraph from "../components/AttackVectorGraph";
import FormField from "../components/FormField";
import { api, AttackVector } from "../api";

export default function K4AttackDashboard() {
  const [selectedVector, setSelectedVector] = useState<AttackVector | null>(null);
  const [filter, setFilter] = useState("");
  const [attackVectors, setAttackVectors] = useState<AttackVector[]>([]);

  useEffect(() => {
    api.attackVectors().then(res => setAttackVectors(res.vectors));
  }, []);

  const filteredVectors = attackVectors.filter(v => v.name.toLowerCase().includes(filter.toLowerCase()));
  const ruledOutCount = attackVectors.filter(v => v.status === "Ruled Out").length;
  const progress = attackVectors.length > 0 ? (ruledOutCount / attackVectors.length) * 100 : 0;

  return (
    <div className="page-container" style={{ position: 'relative' }}>
      <div className="scan-line"></div>
      {selectedVector && (
        <K4AttackDetails vector={selectedVector} onClose={() => setSelectedVector(null)} />
      )}
      <h2>K4 ATTACK VECTOR FINGERPRINT</h2>

      <div className="panel" style={{ marginBottom: '16px' }}>
        <div className="body">
          <div className="row">
            <FormField label="Filter Vectors" style={{ flex: 1 }}>
              <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Search vectors..." />
            </FormField>
          </div>
          <div className="label">Attack Surface Coverage</div>
          <div className="progress-bar-container" style={{ height: '20px', background: 'var(--surface)', borderRadius: '3px', marginTop: '8px', border: '1px solid var(--border)' }}>
            <div className="progress-bar" style={{ height: '100%', width: `${progress}%`, background: 'var(--accent)', borderRadius: '3px' }}></div>
          </div>
          <p style={{ marginTop: '5px', color: 'var(--text)' }}>{ruledOutCount} / {attackVectors.length} vectors ruled out</p>
        </div>
      </div>

      <div className="panel">
        <table className="attack-table">
          <thead>
            <tr>
              <th style={{ color: 'var(--accent)' }}>Attack Vector</th>
              <th style={{ color: 'var(--accent)' }}>Status</th>
              <th style={{ color: 'var(--accent)' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredVectors.map((v) => (
              <tr key={v.name} onClick={() => setSelectedVector(v)} style={{ cursor: 'pointer', borderBottom: '0.5px solid rgba(29, 158, 117, 0.1)' }}>
                <td style={{ color: 'var(--text)' }}>{v.name}</td>
                <td className={v.status === "Ruled Out" ? "status-ruled-out" : ""} style={{ color: v.status === "Ruled Out" ? 'var(--accent)' : v.status === "In Progress" ? 'var(--warning)' : 'var(--text)' }}>{v.status}</td>
                <td><button style={{ background: 'var(--surface)', color: 'var(--accent)', border: '0.5px solid var(--accent)', padding: '5px 10px', borderRadius: '3px', cursor: 'pointer' }}>View Details</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <AttackVectorGraph data={attackVectors} />
    </div>
  );
}
