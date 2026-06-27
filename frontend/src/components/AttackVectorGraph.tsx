import { AttackVector } from "../api";

export default function AttackVectorGraph({ data }: { data: AttackVector[] }) {
  const ruledOut = data.filter(v => v.status === "Ruled Out");
  const inProgress = data.filter(v => v.status === "In Progress");
  const planned = data.filter(v => v.status === "Planned");

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <h2>Attack Surface Analysis</h2>
      <div className="body" style={{ position: 'relative' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '15px' }}>
          {data.map((v) => (
            <div
              key={v.name}
              title={`${v.name}: ${v.status}`}
              style={{
                width: '24px',
                height: '24px',
                backgroundColor:
                  v.status === "Ruled Out"
                    ? "var(--accent)"
                    : v.status === "In Progress"
                      ? "var(--warning)"
                      : v.status === "Planned"
                        ? "var(--text)"
                        : "var(--surface)",
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 'bold',
                textShadow: v.status === "In Progress" ? '0 0 8px var(--warning)' : (v.status === "Planned" ? '0 0 8px var(--text)' : 'none'),
                boxShadow: v.status === "Ruled Out" ? '0 0 5px var(--accent)' : 'none',
                cursor: 'help',
              }}
            >
              {v.status === "Ruled Out" ? '✓' : v.status === "In Progress" ? '▶' : '○'}
            </div>
          ))}
        </div>
        <p style={{ marginBottom: '5px' }}>
          <strong>Ruled Out:</strong> <span style={{ color: 'var(--accent)' }}>{ruledOut.length}</span> <br />
          <strong>In Progress:</strong> <span style={{ color: 'var(--warning)' }}>{inProgress.length}</span> <br />
          <strong>Planned:</strong> <span style={{ color: 'var(--text)' }}>{planned.length}</span> <br />
          <strong>Total:</strong> {data.length}
        </p>

        <div style={{
          marginTop: '25px',
          padding: '20px',
          border: '1px dashed rgba(29, 158, 117, 0.5)', /* Using direct rgba for dashed border for now */
          borderRadius: '5px',
          textAlign: 'center',
          minHeight: '180px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text)',
          background: 'repeating-linear-gradient(45deg, var(--bg), var(--bg) 5px, rgba(29, 158, 117, 0.05) 5px, rgba(29, 158, 117, 0.05) 6px)', /* Subtle pattern */
          boxShadow: '0 0 10px rgba(29, 158, 117, 0.3)', /* Outer glow */
        }}>
          <h3 style={{ color: 'var(--highlight)', textShadow: '0 0 5px var(--highlight)' }}>Interactive Data Flow</h3>
          <p style={{ fontSize: '12px', opacity: '0.8' }}>Visualizing relationships, dependencies, and data propagation within the K4 attack pipeline.</p>
          <div style={{ marginTop: '15px', color: 'var(--accent)', fontSize: '1.2em' }}>[ Placeholder for D3.js or similar visualization ]</div>
        </div>
      </div>
    </div>
  );
}
