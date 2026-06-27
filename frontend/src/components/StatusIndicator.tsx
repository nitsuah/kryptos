export default function StatusIndicator({ status }: { status: string }) {
  const color = status === "active" ? "green" : status === "error" ? "danger" : "amber";
  return (
    <div className="pip" style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 8px',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        background: 'var(--bg)'
    }}>
      <span className={`dot ${color}`} style={{ width: '10px', height: '10px', borderRadius: '50%' }}></span>
      <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px' }}>{status}</span>
    </div>
  );
}
