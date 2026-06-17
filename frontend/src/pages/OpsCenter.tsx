import { useEffect, useState } from "react";
import { Candidate, Run, StatusResponse, api } from "../api";
import MetricCards from "../components/MetricCards";
import RunsTable from "../components/RunsTable";
import CandidatesTable from "../components/CandidatesTable";
import DecryptPanel from "../components/DecryptPanel";
import LogTail from "../components/LogTail";

export default function OpsCenter({ status }: { status: StatusResponse | null }) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [topCandidates, setTopCandidates] = useState<Candidate[]>([]);
  const [selectedRun, setSelectedRun] = useState<number | null>(null);
  const [runCandidates, setRunCandidates] = useState<Candidate[]>([]);

  // Refresh run history + top candidates whenever the DB-enabled status flips on.
  useEffect(() => {
    if (!status?.db_enabled) {
      setRuns([]);
      setTopCandidates([]);
      return;
    }
    api.runs(20).then((r) => setRuns(r.runs)).catch(() => setRuns([]));
    api
      .topCandidates(20)
      .then((r) => setTopCandidates(r.candidates))
      .catch(() => setTopCandidates([]));
  }, [status?.db_enabled, status?.table_counts?.campaign_runs]);

  useEffect(() => {
    if (selectedRun === null) {
      setRunCandidates([]);
      return;
    }
    api
      .runCandidates(selectedRun)
      .then((r) => setRunCandidates(r.candidates))
      .catch(() => setRunCandidates([]));
  }, [selectedRun]);

  return (
    <>
      <MetricCards status={status} />

      <div className="panel">
        <h2>Ad-hoc decrypt</h2>
        <div className="body">
          <DecryptPanel />
        </div>
      </div>

      <div className="panel">
        <h2>Top candidates (all runs)</h2>
        <div className="body">
          <CandidatesTable candidates={topCandidates} />
        </div>
      </div>

      <div className="panel">
        <h2>Live log</h2>
        <div className="body">
          <LogTail />
        </div>
      </div>

      <div className="panel">
        <h2>Campaign runs</h2>
        <div className="body">
          <RunsTable runs={runs} onSelect={setSelectedRun} selectedId={selectedRun} />
        </div>
      </div>

      {selectedRun !== null && (
        <div className="panel">
          <h2>Run #{selectedRun} candidates</h2>
          <div className="body">
            <CandidatesTable candidates={runCandidates} />
          </div>
        </div>
      )}
    </>
  );
}
