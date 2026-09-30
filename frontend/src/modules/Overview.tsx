import CipherMatrix from "../components/CipherMatrix";
import TierGauge from "../components/TierGauge";
import WorldClock from "../components/WorldClock";
import { useDashboard } from "../shell/data";
import { useNav } from "../shell/nav";

// K4 at a glance: the ciphertext with its four cribs, the ledger's totals,
// what is still open, and the World Clock that BERLIN CLOCK refers to.
export default function Overview() {
  const { ledger, ledgerError } = useDashboard();
  const nav = useNav();
  const open = ledger?.entries.filter((e) => e.tier === "open") ?? [];
  const run = ledger?.latest_run;

  return (
    <div className="fit ov-layout">
      <section className="pane ov-cipher">
        <h3>K4 ciphertext · 97 letters · 24 known</h3>
        <CipherMatrix />
      </section>

      <section className="pane ov-ledger">
        <h3>Hypothesis ledger</h3>
        {ledgerError && !ledger ? (
          <div className="result error">Ledger unavailable: {ledgerError}</div>
        ) : (
          <TierGauge counts={ledger?.counts ?? null} size={112} onSelect={() => nav.go("ledger")} />
        )}
        <p className="muted small">
          {run?.timestamp
            ? `Latest crib-constraint run ${run.timestamp.replace("T", " ").slice(0, 16)} UTC.`
            : "No crib-constraint run on this server yet."}
        </p>
      </section>

      <section className="pane ov-open">
        <h3>
          Still open
          <button type="button" className="link-button" onClick={() => nav.go("ledger")}>
            full ledger →
          </button>
        </h3>
        {open.length === 0 ? (
          <p className="muted">{ledger ? "Nothing open in the ledger." : "Loading…"}</p>
        ) : (
          <ol className="open-list">
            {open.map((e) => (
              <li key={e.id} title={e.scope}>
                {e.family}
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="pane ov-clock">
        <h3>Weltzeituhr · Alexanderplatz</h3>
        <WorldClock />
      </section>
    </div>
  );
}
