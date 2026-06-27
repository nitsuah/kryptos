interface Props {
  vector: string;
  description: string | null;
}

export default function AttackVectorVisualizer({ vector, description }: Props) {
  return (
    <div className="panel">
      <h3>{vector}</h3>
      <div className="body" style={{ padding: '20px' }}>
        <p>{description || "No description available."}</p>
        <div style={{
          marginTop: '20px',
          padding: '10px',
          border: '1px solid var(--accent)',
          borderRadius: '5px',
          textAlign: 'center'
        }}>
          [Visual Fingerprint Placeholder]
        </div>
      </div>
    </div>
  );
}
