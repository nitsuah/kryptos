import { Candidate } from "../api";

function fmtScore(score: number | null): string {
  return score === null || score === undefined ? "—" : score.toFixed(3);
}

export default function CandidateRow({ candidate, index }: { candidate: Candidate; index: number }) {
  return (
    <tr key={`${candidate.campaign_run_id ?? "x"}-${candidate.rank}-${index}`}>
      <td>{candidate.rank}</td>
      <td>{fmtScore(candidate.score)}</td>
      <td>{candidate.source ?? "—"}</td>
      <td>{candidate.origin_stage ?? "—"}</td>
      <td className="plaintext">{candidate.text.slice(0, 64)}</td>
    </tr>
  );
}
