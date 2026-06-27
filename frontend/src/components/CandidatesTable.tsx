import { Candidate } from "../api";
import CandidateRow from "./CandidateRow";

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
          <CandidateRow key={`${c.campaign_run_id ?? "x"}-${c.rank}-${i}`} candidate={c} index={i} />
        ))}
      </tbody>
    </table>
  );
}
