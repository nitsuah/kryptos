import { LEDGER_TIERS } from "../api";
import { TIER_HINT, TIER_LABEL } from "../k4";

// Plain-language meanings, reachable by click, tap and keyboard.
export default function StatusKey() {
  return (
    <details className="status-key">
      <summary>Status key</summary>
      <dl>
        {LEDGER_TIERS.map((t) => (
          <div key={t}>
            <dt>{TIER_LABEL[t]}</dt>
            <dd>{TIER_HINT[t]}</dd>
          </div>
        ))}
        <div>
          <dt>Null</dt>
          <dd>A test that found nothing beyond what chance would give.</dd>
        </div>
        <div>
          <dt>Crib</dt>
          <dd>Plaintext letters the sculptor has revealed, at known positions. K4 has 24.</dd>
        </div>
      </dl>
    </details>
  );
}
