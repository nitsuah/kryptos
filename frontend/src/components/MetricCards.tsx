import { StatusResponse } from "../api";

export default function MetricCards({ status }: { status: StatusResponse | null }) {
  const counts = status?.table_counts ?? {};
  const cards = [
    { label: "Campaign runs", value: counts.campaign_runs ?? 0 },
    { label: "Candidates scored", value: counts.candidates ?? 0 },
    { label: "Discovered cribs", value: counts.discovered_cribs ?? 0 },
    { label: "Strategy KB", value: counts.strategy_kb ?? 0 },
  ];
  return (
    <div className="cards">
      {cards.map((c) => (
        <div className="card" key={c.label}>
          <div className="label">{c.label}</div>
          <div className="value">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
