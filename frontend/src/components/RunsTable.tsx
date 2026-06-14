import { Run } from "../api";

function fmtTime(ts: string | null): string {
  if (!ts) return "—";
  return ts.replace("T", " ").slice(0, 19);
}

export default function RunsTable({
  runs,
  onSelect,
  selectedId,
}: {
  runs: Run[];
  onSelect: (id: number) => void;
  selectedId: number | null;
}) {
  if (runs.length === 0) {
    return <div className="muted">No campaign runs recorded.</div>;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Cipher</th>
          <th>Stage</th>
          <th>Status</th>
          <th>Started</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <tr
            key={r.id}
            onClick={() => onSelect(r.id)}
            style={{
              cursor: "pointer",
              outline: r.id === selectedId ? "0.5px solid var(--accent)" : "none",
            }}
          >
            <td>{r.id}</td>
            <td>{r.cipher_label ?? "—"}</td>
            <td>{r.stage ?? "—"}</td>
            <td>{r.status ?? "—"}</td>
            <td>{fmtTime(r.started_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
