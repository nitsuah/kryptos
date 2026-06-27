import { AttackVector } from "../api";

export default function AttackVectorGraph({ data }: { data: AttackVector[] }) {
  const ruledOut = data.filter(v => v.status === "Ruled Out");
  const inProgress = data.filter(v => v.status === "In Progress");
  const planned = data.filter(v => v.status === "Planned");

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <h2>Attack Surface Analysis</h2>
      <div className="body">
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '10px' }}>
          {data.map((v) => (
            <div
              key={v.name}
              title={`${v.name}: ${v.status}`}
              style={{
                width: '20px',
                height: '20px',
                backgroundColor:
                  v.status === "Ruled Out"
                    ? "var(--accent)"
                    : v.status === "In Progress"
                      ? "var(--warning)"
                      : v.status === "Planned"
                        ? "var(--text)"
                        : "#555",
                borderRadius: '3px',
              }}
            />
          ))}
        </div>
        <p>
          <strong>Ruled Out:</strong> {ruledOut.length} <br />
          <strong>In Progress:</strong> {inProgress.length} <br />
          <strong>Planned:</strong> {planned.length} <br />
          <strong>Total:</strong> {data.length}
        </p>

        <div style={{
          marginTop: '20px',
          padding: '20px',
          border: '1px dashed var(--accent)',
          borderRadius: '5px',
          textAlign: 'center',
          minHeight: '150px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text)'
        }}>
          <h3>Advanced Visualization Placeholder</h3>
          <p>This area will contain an interactive graph showing dependencies and relationships between attack vectors.</p>
        </div>
      </div>
    </div>
  );
}
