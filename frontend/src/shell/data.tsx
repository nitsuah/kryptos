// Shared dashboard data. One provider polls the few endpoints every module
// summarises (status, ledger, attack registry, recent jobs), so the carousel's
// side previews and the active module read the same numbers without each
// face fetching on its own. Module-specific data (runs, candidates, pivot
// status) is still fetched inside the module that shows it.

import { createContext, ReactNode, useCallback, useContext, useEffect, useRef, useState } from "react";
import { FrontierVector, JobStatus, LedgerResponse, StatusResponse, api } from "../api";

export interface DashboardData {
  status: StatusResponse | null;
  statusError: string | null;
  online: boolean;
  ledger: LedgerResponse | null;
  ledgerError: string | null;
  vectors: FrontierVector[];
  jobs: JobStatus[];
  jobsError: string | null;
  refreshJobs: () => void;
  refreshLedger: () => void;
}

const Ctx = createContext<DashboardData | null>(null);

const STATUS_MS = 10_000;
const LEDGER_MS = 60_000;
const JOBS_IDLE_MS = 20_000;
const JOBS_ACTIVE_MS = 3_000;

function message(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

function isActive(job: JobStatus): boolean {
  return job.status === "queued" || job.status === "running";
}

// setInterval that pauses while the tab is hidden and re-runs on return.
function usePoll(fn: () => void, ms: number) {
  const saved = useRef(fn);
  saved.current = fn;
  useEffect(() => {
    let id: ReturnType<typeof setInterval> | null = null;
    const start = () => {
      if (id === null) id = setInterval(() => saved.current(), ms);
    };
    const stop = () => {
      if (id !== null) clearInterval(id);
      id = null;
    };
    const onVisibility = () => {
      if (document.hidden) {
        stop();
      } else {
        saved.current();
        start();
      }
    };
    start();
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      stop();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [ms]);
}

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [ledger, setLedger] = useState<LedgerResponse | null>(null);
  const [ledgerError, setLedgerError] = useState<string | null>(null);
  const [vectors, setVectors] = useState<FrontierVector[]>([]);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [jobsError, setJobsError] = useState<string | null>(null);

  const refreshStatus = useCallback(() => {
    api
      .status()
      .then((s) => {
        setStatus(s);
        setStatusError(null);
      })
      .catch((e) => setStatusError(message(e)));
  }, []);

  const refreshLedger = useCallback(() => {
    api
      .ledger()
      .then((l) => {
        setLedger(l);
        setLedgerError(null);
      })
      .catch((e) => setLedgerError(message(e)));
  }, []);

  const refreshJobs = useCallback(() => {
    api
      .jobs(25)
      .then((r) => {
        setJobs(r.jobs);
        setJobsError(null);
      })
      .catch((e) => setJobsError(message(e)));
  }, []);

  useEffect(() => {
    refreshStatus();
    refreshLedger();
    refreshJobs();
    api
      .frontierVectors()
      .then((r) => setVectors(r.vectors))
      .catch(() => setVectors([]));
  }, [refreshStatus, refreshLedger, refreshJobs]);

  // A finished P21/P22 job changes the ledger's latest run, so refresh it
  // when the number of active jobs drops.
  const activeCount = jobs.filter(isActive).length;
  const prevActive = useRef(activeCount);
  useEffect(() => {
    if (activeCount < prevActive.current) refreshLedger();
    prevActive.current = activeCount;
  }, [activeCount, refreshLedger]);

  usePoll(refreshStatus, STATUS_MS);
  usePoll(refreshLedger, LEDGER_MS);
  usePoll(refreshJobs, activeCount > 0 ? JOBS_ACTIVE_MS : JOBS_IDLE_MS);

  const value: DashboardData = {
    status,
    statusError,
    online: status !== null && statusError === null,
    ledger,
    ledgerError,
    vectors,
    jobs,
    jobsError,
    refreshJobs,
    refreshLedger,
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useDashboard(): DashboardData {
  const v = useContext(Ctx);
  if (!v) throw new Error("useDashboard must be used inside DashboardDataProvider");
  return v;
}
