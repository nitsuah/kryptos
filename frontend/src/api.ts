// Typed client for the kryptos FastAPI backend (src/kryptos/api/dashboard.py).
// Same-origin in production (FastAPI serves the bundle); proxied in dev via vite.

export interface StatusResponse {
  db_enabled: boolean;
  table_counts: Record<string, number>;
  latest_run: Run | null;
}

export interface Run {
  id: number;
  label: string | null;
  stage: string | null;
  cipher_label: string | null;
  status: string | null;
  started_at: string | null;
  finished_at: string | null;
}

export interface RunsResponse {
  db_enabled: boolean;
  count: number;
  runs: Run[];
}

export interface Candidate {
  campaign_run_id?: number;
  rank: number;
  score: number | null;
  source: string | null;
  key_hash: string | null;
  text: string;
  origin_stage?: string | null;
}

export interface CandidatesResponse {
  db_enabled: boolean;
  count: number;
  candidates: Candidate[];
}

export interface DecryptResponse {
  section: string;
  plaintext: string;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function getJSON<T>(path: string): Promise<T> {
  const resp = await fetch(path);
  if (!resp.ok) {
    throw new ApiError(resp.status, await resp.text());
  }
  return (await resp.json()) as T;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    let detail = await resp.text();
    try {
      detail = JSON.parse(detail).detail ?? detail;
    } catch {
      /* keep raw text */
    }
    throw new ApiError(resp.status, detail);
  }
  return (await resp.json()) as T;
}

export const api = {
  status: () => getJSON<StatusResponse>("/api/status"),
  runs: (limit = 20) => getJSON<RunsResponse>(`/api/runs?limit=${limit}`),
  runCandidates: (runId: number, limit = 50) =>
    getJSON<CandidatesResponse>(`/api/runs/${runId}/candidates?limit=${limit}`),
  topCandidates: (limit = 20) => getJSON<CandidatesResponse>(`/api/candidates?limit=${limit}`),
  decrypt: (section: string, ciphertext: string, key?: string) =>
    postJSON<DecryptResponse>("/api/decrypt", { section, ciphertext, key: key || null }),
};
