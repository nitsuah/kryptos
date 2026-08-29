// Typed client for the kryptos FastAPI backend (src/kryptos/api/dashboard.py).
// Same-origin in production (FastAPI serves the bundle); proxied in dev via vite.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";

function apiPath(path: string): string {
  return `${API_BASE_URL}${path}`;
}

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

export interface VaultSealResponse {
  token: string;
  cipher: string;
  max_reads: number;
  expires_at: string | null;
}

export interface VaultUnsealResponse {
  token: string;
  plaintext: string;
  reads_remaining: number;
  expires_at: string | null;
}

export interface VaultPeekResponse {
  token: string;
  cipher: string;
  status: string;
  max_reads: number;
  reads_used: number;
  reads_remaining: number;
  sealed_at: string | null;
  expires_at: string | null;
}

export interface AttackVector {
  name: string;
  status: string;
  artifact: string | null;
  description: string | null;
}

export interface AttackVectorsResponse {
  vectors: AttackVector[];
}

// --- Frontier P1-P10 attack vectors ---

export interface FrontierVector {
  id: string;
  priority: number;
  name: string;
  status: string;
  description: string;
  layer_count: number;
  combo_estimate: number | null;
  runnable: boolean;
}

export interface FrontierVectorsResponse {
  vectors: FrontierVector[];
}

// --- Physical/Geometric Pivot status (v2 dashboard panel) ---

export interface HypothesisGraphEdge {
  status: "untested" | "null" | "partial_null" | "confirmed" | "eureka";
  evidence: string;
  updated?: string;
}

export interface HypothesisGraph {
  nodes: string[];
  edges: Record<string, HypothesisGraphEdge>;
}

export interface BearingInfo {
  forward_azimuth_deg: number;
  back_azimuth_deg: number | null;
  distance_m: number;
  distance_ft: number;
  source: string;
  note: string | null;
}

export interface PivotStatusResponse {
  hypothesis_graph: HypothesisGraph;
  hypothesis_graph_mermaid: string;
  total_candidates_tested: number;
  bearings: Record<string, BearingInfo>;
}

export interface RunAttackRequest {
  attack_id: string;
  priority_only?: boolean;
  grid_sizes?: number[] | null;
  max_perms_per_grid?: number | null;
}

export interface AttackCandidate {
  candidate_text: string;
  keyword_hits: number;
  instructional_score?: number;
  alpha_name?: string;
  n_cols?: number;
  perm?: number[];
  clock_time?: string;
  // P6-specific
  variant?: string;
  // P7-specific
  key?: string;
  // P3/P4-specific
  source?: string;
  is_offset?: boolean;
}

export interface JobStatus {
  job_id: string;
  attack_id: string;
  status: string;  // "queued" | "running" | "complete" | "error" | "eureka"
  progress_pct: number;
  clock_time: string | null;
  total_candidates: number;
  top_candidates: AttackCandidate[];
  summary: Record<string, unknown> | null;
  error: string | null;
}


export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function getJSON<T>(path: string): Promise<T> {
  const resp = await fetch(apiPath(path));
  if (!resp.ok) {
    throw new ApiError(resp.status, await resp.text());
  }
  return (await resp.json()) as T;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(apiPath(path), {
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
  vaultSeal: (plaintext: string, key: string, ttl_seconds: number, max_reads: number) =>
    postJSON<VaultSealResponse>("/api/vault/seal", { plaintext, key, ttl_seconds, max_reads }),
  vaultUnseal: (token: string, key: string) =>
    postJSON<VaultUnsealResponse>("/api/vault/unseal", { token, key }),
  vaultPeek: (token: string) => getJSON<VaultPeekResponse>(`/api/vault/${encodeURIComponent(token)}`),
  attackVectors: () => getJSON<AttackVectorsResponse>("/api/attack-vectors"),
  frontierVectors: () => getJSON<FrontierVectorsResponse>("/api/k4/attacks/frontier"),
  pivotStatus: () => getJSON<PivotStatusResponse>("/api/k4/attacks/pivot-status"),
  runAttack: (req: RunAttackRequest) => postJSON<JobStatus>("/api/k4/attacks/run", req),
  jobStatus: (jobId: string) => getJSON<JobStatus>(`/api/k4/attacks/jobs/${jobId}`),
};
