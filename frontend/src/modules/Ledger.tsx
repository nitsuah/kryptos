import { useMemo, useState } from "react";
import { LEDGER_TIERS, LedgerTier } from "../api";
import TierGauge from "../components/TierGauge";
import { TIER_HINT, TIER_LABEL } from "../k4";
import { useDashboard } from "../shell/data";

// Every hypothesis family from GET /api/k4/ledger, filterable by tier and
// text. Entries are collapsed to one line; opening one shows the scope,
// evidence, and the module and test behind it.
export default function Ledger() {
  const { ledger, ledgerError, refreshLedger } = useDashboard();
  const [tier, setTier] = useState<LedgerTier | "all">("all");
  const [q, setQ] = useState("");

  const entries = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const order = (t: LedgerTier) => LEDGER_TIERS.indexOf(t);
    return (ledger?.entries ?? [])
      .filter((e) => tier === "all" || e.tier === tier)
      .filter(
        (e) =>
          !needle ||
          [e.family, e.scope, e.evidence, e.module, e.id].some((f) => f.toLowerCase().includes(needle)),
      )
      .sort((a, b) => order(a.tier) - order(b.tier));
  }, [ledger, tier, q]);

  if (!ledger) {
    return (
      <div className="sub">
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

  return (
    <div className="grid ledger-grid">
      <section className="sub ledger-side">
        <TierGauge counts={ledger.counts} size={132} onSelect={(t) => setTier(t === tier ? "all" : t)} />
        {tier !== "all" && <p className="muted small">{TIER_HINT[tier]}</p>}
      </section>

      <section className="sub ledger-main">
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

        {entries.length === 0 ? (
          <p className="muted">No entries match.</p>
        ) : (
          <ul className="entry-list">
            {entries.map((e) => (
              <li key={e.id}>
                <details className="entry">
                  <summary>
                    <span className={`tier-tag tier-${e.tier}`}>{TIER_LABEL[e.tier]}</span>
                    <span className="entry-title">{e.family}</span>
                  </summary>
                  <dl className="entry-body">
                    {e.scope && (
                      <>
                        <dt>Scope</dt>
                        <dd>{e.scope}</dd>
                      </>
                    )}
                    {e.evidence && (
                      <>
                        <dt>Evidence</dt>
                        <dd>{e.evidence}</dd>
                      </>
                    )}
                    {e.module && (
                      <>
                        <dt>Module</dt>
                        <dd>
                          <code>{e.module}</code>
                        </dd>
                      </>
                    )}
                    {e.test && (
                      <>
                        <dt>Test</dt>
                        <dd>
                          <code>{e.test}</code>
                        </dd>
                      </>
                    )}
                    <dt>ID</dt>
                    <dd>
                      <code>{e.id}</code>
                    </dd>
                  </dl>
                </details>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
