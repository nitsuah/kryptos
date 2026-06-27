import { Run } from "../api";

function fmtTime(ts: string | null): string {
  if (!ts) return "—";
  return ts.replace("T", " ").slice(0, 19);
}

export default function RunRow({ run, onSelect, selectedId }: { run: Run; onSelect: (id: number) => void; selectedId: number | null }) {
  return (
    <tr
      key={run.id}
      onClick={() => onSelect(run.id)}
      style={{
        cursor: "pointer",
        outline: run.id === selectedId ? "0.5px solid var(--accent)" : "none",
      }}
    >
      <td>{run.id}</td>
      <td>{run.cipher_label ?? "—"}</td>
      <td>{run.stage ?? "—"}</td>
      <td>{run.status ?? "—"}</td>
      <td>{fmtTime(run.started_at)}</td>
    </tr>
  );
}
