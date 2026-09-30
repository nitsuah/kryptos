import { useMemo, useState } from "react";
import { LEDGER_TIERS, LedgerEntry, LedgerTier } from "../api";
import TierGauge from "../components/TierGauge";
import { TIER_HINT, TIER_LABEL } from "../k4";
import { useDashboard } from "../shell/data";

// Every hypothesis family from GET /api/k4/ledger. Master–detail: a compact
// list on the left (filter by tier or text), the selected family's scope,
// evidence, module and test on the right.
export default function Ledger() {
  const { ledger, ledgerError, refreshLedger } = useDashboard();
  const [tier, setTier] = useState<LedgerTier | "all">("all");
  const [q, setQ] = useState("");
  const [selId, setSelId] = useState<string | null>(null);

  const entries = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const order = (t: LedgerTier) => LEDGER_TIERS.indexOf(t);
    return (ledger?.entries ?? [])
      .filter((e) => tier === "all" || e.tier === tier)
      .filter(
        (e) =>
          !needle || [e.family, e.scope, e.evidence, e.module, e.id].some((f) => f.toLowerCase().includes(needle)),
      )
      .sort((a, b) => order(a.tier) - order(b.tier));
  }, [ledger, tier, q]);

  if (!ledger) {
    return (
      <div className="pane">
        {ledgerError ? (
          <div className="result error">
            Ledger unavailable: {ledgerError}{" "}
            <button type="button" onClick={refreshLedger}>
              Retry
            </button>
          </div>
        ) : (
          <p className="muted">Loading ledger…</p>
        )}
      </div>
    );
  }

  const selected: LedgerEntry | undefined = entries.find((e) => e.id === selId) ?? entries[0];

  return (
    <div className="fit ledger-layout">
      <section className="pane ledger-list">
        <div className="toolbar">
          <div className="seg" role="group" aria-label="Filter by tier">
            {(["all", ...LEDGER_TIERS] as const).map((t) => (
              <button
                type="button"
                key={t}
                className={`seg-btn ${t !== "all" ? `tier-${t}` : ""}`}
                aria-pressed={tier === t}
                onClick={() => setTier(t)}
              >
                {t === "all" ? "All" : TIER_LABEL[t]}
                <span className="seg-count">{t === "all" ? ledger.entries.length : ledger.counts[t]}</span>
              </button>
            ))}
          </div>
          <input
            type="search"
            className="search"
            placeholder="Search families, modules…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Search the ledger"
          />
        </div>
        <ul className="rows" aria-label="Hypothesis families">
          {entries.length === 0 && <li className="muted">No entries match.</li>}
          {entries.map((e) => (
            <li key={e.id}>
              <button
                type="button"
                className="row-btn"
                aria-pressed={selected?.id === e.id}
                onClick={() => setSelId(e.id)}
              >
                <span className={`tier-tag tier-${e.tier}`}>{TIER_LABEL[e.tier]}</span>
                <span className="row-title">{e.family}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="pane ledger-detail">
        <TierGauge counts={ledger.counts} size={104} onSelect={(t) => setTier(t === tier ? "all" : t)} />
        {selected ? (
          <article className="detail">
            <span className={`tier-tag tier-${selected.tier}`}>{TIER_LABEL[selected.tier]}</span>
            <h4>{selected.family}</h4>
            <p className="muted small">{TIER_HINT[selected.tier]}</p>
            <dl className="kv">
              {selected.scope && (
                <>
                  <dt>Scope</dt>
                  <dd>{selected.scope}</dd>
                </>
              )}
              {selected.evidence && (
                <>
                  <dt>Evidence</dt>
                  <dd>{selected.evidence}</dd>
                </>
              )}
              {selected.module && (
                <>
                  <dt>Module</dt>
                  <dd>
                    <code>{selected.module}</code>
                  </dd>
                </>
              )}
              {selected.test && (
                <>
                  <dt>Test</dt>
                  <dd>
                    <code>{selected.test}</code>
                  </dd>
                </>
              )}
            </dl>
          </article>
        ) : (
          <p className="muted">Pick a family.</p>
        )}
      </section>
    </div>
  );
}
