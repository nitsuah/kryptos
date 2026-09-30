import { useEffect, useMemo, useState } from "react";
import { AttackVector, FrontierVector, api } from "../api";
import AttackRunPanel from "../components/AttackRunPanel";
import { useDashboard } from "../shell/data";

const PHASES: { label: string; test: (p: number) => boolean }[] = [
  { label: "Constraint suites · P21–P22", test: (p) => p >= 21 },
  { label: "Core composite · P1–P7", test: (p) => p <= 7 },
  { label: "Run offline · P8–P10", test: (p) => p >= 8 && p <= 10 },
  { label: "Frontier expansion · P11–P20", test: (p) => p >= 11 && p <= 20 },
];

function statusClass(s: string): string {
  return `st-${s.toLowerCase().replace(/[^a-z]+/g, "-")}`;
}

function VectorRow({
  v,
  open,
  onToggle,
  activeJob,
  onJobChange,
}: {
  v: FrontierVector;
  open: boolean;
  onToggle: () => void;
  activeJob: boolean;
  onJobChange: () => void;
}) {
  return (
    <li className={`vector${open ? " open" : ""}`}>
      <button type="button" className="vector-head" aria-expanded={open} onClick={onToggle}>
        <span className="prio">P{v.priority}</span>
        <span className="vector-name">{v.name.replace(/^P\d+\s*[—-]\s*/, "")}</span>
        {activeJob && <span className="live-dot" aria-label="job running" />}
        <span className={`vector-status ${statusClass(v.status)}`}>{v.status}</span>
        <span className="chev" aria-hidden="true">
          {open ? "▴" : "▾"}
        </span>
      </button>
      {open && (
        <div className="vector-body">
          <p>{v.description}</p>
          <p className="muted small">
            {v.layer_count} layer{v.layer_count === 1 ? "" : "s"}
            {v.combo_estimate != null && ` · ~${v.combo_estimate.toLocaleString()} combinations`}
            {" · "}
            {v.runnable ? "runnable" : "not runnable from the dashboard"}
          </p>
          {v.runnable && <AttackRunPanel vector={v} onJobChange={onJobChange} />}
        </div>
      )}
    </li>
  );
}

export default function Attacks() {
  const { vectors, jobs, refreshJobs } = useDashboard();
  const [q, setQ] = useState("");
  const [runnableOnly, setRunnableOnly] = useState(false);
  const [openId, setOpenId] = useState<string | null>(null);
  const [registry, setRegistry] = useState<AttackVector[] | null>(null);

  useEffect(() => {
    api
      .attackVectors()
      .then((r) => setRegistry(r.vectors))
      .catch(() => setRegistry([]));
  }, []);

  const active = useMemo(
    () => new Set(jobs.filter((j) => j.status === "queued" || j.status === "running").map((j) => j.attack_id)),
    [jobs],
  );

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return vectors
      .filter((v) => !runnableOnly || v.runnable)
      .filter((v) => !needle || `${v.name} ${v.description} ${v.id} p${v.priority}`.toLowerCase().includes(needle));
  }, [vectors, q, runnableOnly]);

  return (
    <div className="grid attacks-grid">
      <section className="sub span-2">
        <div className="toolbar">
          <input
            type="search"
            className="search"
            placeholder="Search attacks (name, P-number)…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Search attacks"
          />
          <label className="check">
            <input type="checkbox" checked={runnableOnly} onChange={(e) => setRunnableOnly(e.target.checked)} />
            Runnable only
          </label>
          <span className="muted small">
            {vectors.length} vectors · {active.size} running
          </span>
        </div>

        {vectors.length === 0 ? (
          <p className="muted">Loading the attack registry…</p>
        ) : (
          PHASES.map((ph) => {
            const rows = filtered.filter((v) => ph.test(v.priority)).sort((a, b) => a.priority - b.priority);
            if (rows.length === 0) return null;
            return (
              <div key={ph.label} className="phase">
                <h4 className="phase-label">{ph.label}</h4>
                <ul className="vector-list">
                  {rows.map((v) => (
                    <VectorRow
                      key={v.id}
                      v={v}
                      open={openId === v.id}
                      onToggle={() => setOpenId(openId === v.id ? null : v.id)}
                      activeJob={active.has(v.id)}
                      onJobChange={refreshJobs}
                    />
                  ))}
                </ul>
              </div>
            );
          })
        )}
      </section>

      <section className="sub span-2">
        <details className="json-details">
          <summary>Earlier attack-vector registry ({registry?.length ?? "…"})</summary>
          {registry && registry.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Vector</th>
                  <th>Status</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {registry.map((r) => (
                  <tr key={r.name}>
                    <td>{r.name}</td>
                    <td className={statusClass(r.status)}>{r.status}</td>
                    <td className="muted">{r.description ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="muted">{registry ? "Registry unavailable." : "Loading…"}</p>
          )}
        </details>
      </section>
    </div>
  );
}
