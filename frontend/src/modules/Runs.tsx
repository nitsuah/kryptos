import { useEffect, useState } from "react";
import { Candidate, Run, api } from "../api";
import CandidatesTable from "../components/CandidatesTable";
import RunsTable from "../components/RunsTable";
import { useDashboard } from "../shell/data";

// Campaign run history and candidates from Neon (GET /api/runs,
// /api/runs/{id}/candidates, /api/candidates). Empty without DATABASE_URL.
export default function Runs() {
  const { status } = useDashboard();
  const dbEnabled = status?.db_enabled === true;
  const runCount = status?.table_counts?.campaign_runs;
  const [runs, setRuns] = useState<Run[]>([]);
  const [top, setTop] = useState<Candidate[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [runCandidates, setRunCandidates] = useState<Candidate[]>([]);

  useEffect(() => {
    if (!dbEnabled) {
      setRuns([]);
      setTop([]);
      return;
    }
    api
      .runs(30)
      .then((r) => setRuns(r.runs))
      .catch(() => setRuns([]));
    api
      .topCandidates(20)
      .then((r) => setTop(r.candidates))
      .catch(() => setTop([]));
  }, [dbEnabled, runCount]);

  useEffect(() => {
    if (selected === null) {
      setRunCandidates([]);
      return;
    }
    api
      .runCandidates(selected)
      .then((r) => setRunCandidates(r.candidates))
      .catch(() => setRunCandidates([]));
  }, [selected]);

  if (status && !dbEnabled) {
    return (
      <div className="sub">
        <p>
          Run history lives in Neon. This server has no <code>DATABASE_URL</code>, so there is nothing to show.
        </p>
        <p className="muted small">
          Set <code>DATABASE_URL</code> to a Postgres connection string and run <code>kryptos db-init</code>. Decrypt,
          the ledger and attack jobs work without it.
        </p>
      </div>
    );
  }

  return (
    <div className="grid runs-grid">
      <section className="sub">
        <h3>Campaign runs</h3>
        <div className="table-wrap">
          <RunsTable runs={runs} onSelect={(id) => setSelected(id === selected ? null : id)} selectedId={selected} />
        </div>
      </section>
      <section className="sub">
        <h3>{selected === null ? "Top candidates · all runs" : `Run #${selected} candidates`}</h3>
        <div className="table-wrap">
          <CandidatesTable candidates={selected === null ? top : runCandidates} />
        </div>
        <p className="muted small">
          Candidates ranked before 2026-09-28 were scored with placeholder n-gram tables; treat old rankings with care.
        </p>
      </section>
    </div>
  );
}
