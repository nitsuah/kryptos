import { Run } from "../api";
import RunRow from "./RunRow";

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
          <RunRow key={r.id} run={r} onSelect={onSelect} selectedId={selectedId} />
        ))}
      </tbody>
    </table>
  );
}
