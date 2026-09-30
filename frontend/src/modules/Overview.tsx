import { useEffect, useState } from "react";
import BerlinClock from "../components/BerlinClock";
import CipherMatrix from "../components/CipherMatrix";
import TierGauge from "../components/TierGauge";
import { useDashboard } from "../shell/data";
import { useNav } from "../shell/nav";

const ZONES = [
  { label: "UTC", tz: "UTC" },
  { label: "BERLIN", tz: "Europe/Berlin" },
  { label: "LANGLEY", tz: "America/New_York" },
];

function useNow(ms = 1000): Date {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), ms);
    return () => clearInterval(id);
  }, [ms]);
  return now;
}

function fmt(now: Date, tz: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    timeZone: tz,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(now);
}

export default function Overview() {
  const { ledger, ledgerError } = useDashboard();
  const nav = useNav();
  const now = useNow();
  const open = ledger?.entries.filter((e) => e.tier === "open") ?? [];
  const run = ledger?.latest_run;

  return (
    <div className="grid ov-grid">
      <section className="sub span-2">
        <h3>K4 ciphertext · 97 letters · 24 known</h3>
        <CipherMatrix />
      </section>

      <section className="sub">
        <h3>Hypothesis ledger</h3>
        {ledgerError && !ledger ? (
          <div className="result error">Ledger unavailable: {ledgerError}</div>
        ) : (
          <TierGauge counts={ledger?.counts ?? null} onSelect={() => nav.go("ledger")} />
        )}
        <p className="muted small">
          {run?.timestamp
            ? `Latest crib-constraint run ${run.timestamp.replace("T", " ").slice(0, 16)} UTC · ${run.columnar_survivors_period_le_22} columnar and ${run.geometry_survivors_period_le_22} geometric survivors at period ≤ 22.`
            : "No crib-constraint run recorded on this server yet. Run P21 from Attacks."}
        </p>
      </section>

      <section className="sub">
        <h3>Open fronts</h3>
        {open.length === 0 ? (
          <p className="muted">{ledger ? "Nothing open in the ledger." : "Loading…"}</p>
        ) : (
          <ol className="open-list">
            {open.map((e) => (
              <li key={e.id}>
                <span>{e.family}</span>
                {e.scope && <span className="muted small">{e.scope}</span>}
              </li>
            ))}
          </ol>
        )}
        <button type="button" className="link-button" onClick={() => nav.go("ledger")}>
          Full ledger →
        </button>
      </section>

      <section className="sub span-2 clocks">
        <h3>Clocks</h3>
        <div className="clock-row">
          <BerlinClock size="sm" showLabel />
          <dl className="zones">
            {ZONES.map((z) => (
              <div key={z.tz}>
                <dt>{z.label}</dt>
                <dd>{fmt(now, z.tz)}</dd>
              </div>
            ))}
          </dl>
          <p className="muted small clock-note">
            The lamp clock is the Mengenlehreuhr. Sanborn said in 2025 that BERLIN CLOCK in K4 means the Weltzeituhr
            (World Clock) at Alexanderplatz.
          </p>
        </div>
      </section>
    </div>
  );
}
