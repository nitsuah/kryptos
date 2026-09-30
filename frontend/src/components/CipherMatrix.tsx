import { useState } from "react";
import { CRIBS, K4, cribAt } from "../k4";

// The 97 K4 letters in a grid that reflows with the width available. Crib
// letters are tinted per crib; hovering, focusing or tapping any cell shows
// its index and, for crib cells, the plaintext letter Sanborn released.
export default function CipherMatrix() {
  const [focus, setFocus] = useState<number | null>(null);
  const crib = focus === null ? null : cribAt(focus);

  return (
    <div className="cipher-matrix">
      <div className="cm-grid" role="list" aria-label="K4 ciphertext, 97 letters">
        {K4.split("").map((ch, i) => {
          const c = cribAt(i);
          return (
            <button
              type="button"
              role="listitem"
              key={i}
              className={`cm-cell${c ? ` crib tone-${c.tone}` : ""}${focus === i ? " focus" : ""}`}
              onMouseEnter={() => setFocus(i)}
              onFocus={() => setFocus(i)}
              onClick={() => setFocus(i)}
              aria-label={`position ${i}: ${ch}${c ? `, plaintext ${c.plain[i - c.start]} (${c.label})` : ""}`}
            >
              <span className="cm-ch">{ch}</span>
              <span className="cm-plain" aria-hidden="true">
                {c ? c.plain[i - c.start] : ""}
              </span>
              <span className="cm-idx" aria-hidden="true">
                {i}
              </span>
            </button>
          );
        })}
      </div>
      <div className="cm-readout" aria-live="polite">
        {focus === null ? (
          <span className="muted">Hover or tap a letter.</span>
        ) : (
          <>
            <span className="cm-readout-pos">POS {String(focus).padStart(2, "0")}</span>
            <span>
              cipher <b>{K4[focus]}</b>
            </span>
            {crib ? (
              <span className={`tone-${crib.tone}`}>
                plain <b>{crib.plain[focus - crib.start]}</b> · {crib.label} {crib.start}–{crib.end - 1}
              </span>
            ) : (
              <span className="muted">plain unknown</span>
            )}
          </>
        )}
      </div>
      <ul className="cm-legend">
        {CRIBS.map((c) => (
          <li key={c.label} className={`tone-${c.tone}`}>
            <span className="swatch" aria-hidden="true" />
            <b>{c.label}</b>
            <span className="muted">
              {K4.slice(c.start, c.end)} · {c.start}–{c.end - 1} · {c.released}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
