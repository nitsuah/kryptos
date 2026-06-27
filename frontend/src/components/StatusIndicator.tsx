export default function StatusIndicator({ status }: { status: string }) {
  const color = status === "active" ? "green" : status === "error" ? "danger" : "amber";
  return (
    <div className="pip">
      <span className={`dot ${color}`}></span>
      <span style={{ fontSize: '11px', textTransform: 'uppercase' }}>{status}</span>
    </div>
  );
}
