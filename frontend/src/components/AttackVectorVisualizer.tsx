interface Props {
  vector: string;
}

export default function AttackVectorVisualizer({ vector }: Props) {
  // Simple visualization placeholder - can be made complex based on requirements
  return (
    <div className="panel">
      <h2>Visual Fingerprint: {vector}</h2>
      <div className="body" style={{ textAlign: 'center', padding: '20px' }}>
        <div style={{
          display: 'inline-flex',
          width: '100px',
          height: '100px',
          border: '1px solid var(--accent)',
          borderRadius: '50%',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          [DATA]
        </div>
        <p>Visualization logic for {vector} to be implemented.</p>
      </div>
    </div>
  );
}
