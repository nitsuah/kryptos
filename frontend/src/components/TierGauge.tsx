import { LEDGER_TIERS, LedgerTier } from "../api";
import { TIER_LABEL } from "../k4";

// Segmented ring of ledger tier counts, with the total in the middle.
export default function TierGauge({
  counts,
  size = 150,
  onSelect,
}: {
  counts: Record<LedgerTier, number> | null;
  size?: number;
  onSelect?: (tier: LedgerTier) => void;
}) {
  const total = counts ? LEDGER_TIERS.reduce((n, t) => n + (counts[t] ?? 0), 0) : 0;
  const r = 40;
  const circ = 2 * Math.PI * r;
  const gap = total > 0 ? 1.6 : 0;
  let offset = 0;

  return (
    <div className="tier-gauge">
      <svg viewBox="0 0 100 100" width={size} height={size} role="img" aria-label={`${total} hypothesis families`}>
        <circle cx={50} cy={50} r={r} className="tg-track" />
        {counts &&
          total > 0 &&
          LEDGER_TIERS.map((t) => {
            const len = ((counts[t] ?? 0) / total) * circ;
            const seg = (
              <circle
                key={t}
                cx={50}
                cy={50}
                r={r}
                className={`tg-seg tier-${t}`}
                strokeDasharray={`${Math.max(len - gap, 0)} ${circ}`}
                strokeDashoffset={-offset}
                transform="rotate(-90 50 50)"
              />
            );
            offset += len;
            return seg;
          })}
        <text x={50} y={49} className="tg-total" textAnchor="middle">
          {counts ? total : "··"}
        </text>
        <text x={50} y={62} className="tg-caption" textAnchor="middle">
          FAMILIES
        </text>
      </svg>
      <ul className="tg-legend">
        {LEDGER_TIERS.map((t) => (
          <li key={t}>
            <button type="button" className={`tier-chip tier-${t}`} onClick={() => onSelect?.(t)} disabled={!onSelect}>
              <span className="swatch" aria-hidden="true" />
              <span className="tg-name">{TIER_LABEL[t]}</span>
              <b>{counts ? counts[t] ?? 0 : "–"}</b>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
