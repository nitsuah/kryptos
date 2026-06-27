import { StatusResponse } from "../api";
import MetricCard from "./MetricCard";

export default function MetricCards({ status }: { status: StatusResponse | null }) {
  const counts = status?.table_counts ?? {};
  return (
    <div className="cards">
      <MetricCard label="Campaign runs" value={counts.campaign_runs ?? 0} />
      <MetricCard label="Candidates scored" value={counts.candidates ?? 0} />
      <MetricCard label="Discovered cribs" value={counts.discovered_cribs ?? 0} />
      <MetricCard label="Strategy KB" value={counts.strategy_kb ?? 0} />
    </div>
  );
}
