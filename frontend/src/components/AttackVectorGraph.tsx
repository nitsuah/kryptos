import { AttackVector } from "../api";

export default function AttackVectorGraph({ data }: { data: AttackVector[] }) {
  const ruledOut = data.filter(v => v.status === "Ruled Out");
  const others = data.filter(v => v.status !== "Ruled Out");

  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <h2>Attack Surface Analysis</h2>
      <div className="body">
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {data.map((v) => (
            <div
              key={v.name}
              title={`${v.name}: ${v.status}`}
              style={{
                width: '20px',
                height: '20px',
                backgroundColor: v.status === "Ruled Out" ? "var(--accent)" : "#555",
                borderRadius: '3px',
              }}
            />
          ))}
        </div>
        <p style={{ marginTop: '10px' }}>
          {ruledOut.length} ruled out, {others.length} remaining.
        </p>
      </div>
    </div>
  );
}
