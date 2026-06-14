import { Candidate } from "../api";

function fmtScore(score: number | null): string {
  return score === null || score === undefined ? "—" : score.toFixed(3);
}

export default function CandidatesTable({ candidates }: { candidates: Candidate[] }) {
  if (candidates.length === 0) {
    return <div className="muted">No candidates yet.</div>;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Score</th>
          <th>Source</th>
          <th>Stage</th>
          <th>Plaintext</th>
        </tr>
      </thead>
      <tbody>
        {candidates.map((c, i) => (
          <tr key={`${c.campaign_run_id ?? "x"}-${c.rank}-${i}`}>
            <td>{c.rank}</td>
            <td>{fmtScore(c.score)}</td>
            <td>{c.source ?? "—"}</td>
            <td>{c.origin_stage ?? "—"}</td>
            <td className="plaintext">{c.text.slice(0, 64)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
