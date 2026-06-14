import { useEffect, useMemo, useRef, useState } from "react";
import { KEYED_ALPHABET, vigenereSteps } from "../cipher";

// Animated keyed-alphabet Vigenère decryption for K1/K2: steps through each
// cipher letter, showing its position in the keyed tableau and the recovered
// plaintext letter, with play/pause and a speed control.
export default function SubstitutionAnimator({ cipher, keyword }: { cipher: string; keyword: string }) {
  const steps = useMemo(() => vigenereSteps(cipher, keyword), [cipher, keyword]);
  const [pos, setPos] = useState(0); // number of letters revealed
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(200); // ms per letter
  const timer = useRef<number | null>(null);

  useEffect(() => {
    if (!playing) return;
    if (pos >= steps.length) {
      setPlaying(false);
      return;
    }
    timer.current = window.setTimeout(() => setPos((p) => Math.min(p + 1, steps.length)), speed);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [playing, pos, speed, steps.length]);

  const current = pos < steps.length ? steps[pos] : null;
  const plain = steps
    .slice(0, pos)
    .map((s) => s.plain)
    .join("");

  return (
    <div>
      <div className="row" style={{ alignItems: "center", marginBottom: 12 }}>
        <button onClick={() => setPlaying((p) => !p)} disabled={pos >= steps.length}>
          {playing ? "Pause" : pos >= steps.length ? "Done" : "Play"}
        </button>
        <button onClick={() => { setPlaying(false); setPos(0); }}>Reset</button>
        <button onClick={() => setPos(steps.length)}>Skip to end</button>
        <div className="field" style={{ margin: 0 }}>
          <label>Speed {speed}ms</label>
          <input
            type="range"
            min={40}
            max={500}
            step={20}
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
          />
        </div>
        <span className="muted">
          {pos}/{steps.length}
        </span>
      </div>

      {/* Keyed alphabet tableau with the active cipher/key/plain cells lit */}
      <div className="field">
        <label>Keyed alphabet (KRYPTOS)</label>
        <div style={{ letterSpacing: 3 }}>
          {KEYED_ALPHABET.split("").map((ch, i) => {
            let color: string | undefined;
            if (current && i === current.cipherIdx) color = "var(--warning)";
            else if (current && i === current.keyIdx) color = "var(--highlight)";
            else if (current && i === current.plainIdx) color = "var(--accent)";
            return (
              <span key={i} style={{ color, fontWeight: color ? "bold" : "normal" }}>
                {ch}
              </span>
            );
          })}
        </div>
        <div className="muted" style={{ fontSize: 11 }}>
          <span style={{ color: "var(--warning)" }}>■ cipher</span>{"  "}
          <span style={{ color: "var(--highlight)" }}>■ key</span>{"  "}
          <span style={{ color: "var(--accent)" }}>■ plain</span>
        </div>
      </div>

      {current && (
        <div className="result">
          C={current.cipher} (pos {current.cipherIdx}) − K={current.key} (pos {current.keyIdx}) ={" "}
          <span style={{ color: "var(--accent)" }}>
            P={current.plain} (pos {current.plainIdx})
          </span>
        </div>
      )}

      <div className="field" style={{ marginTop: 12 }}>
        <label>Plaintext</label>
        <div className="result plaintext" style={{ minHeight: 40 }}>
          {plain}
          <span style={{ color: "var(--warning)" }}>{current ? current.cipher.toLowerCase() : ""}</span>
        </div>
      </div>
    </div>
  );
}
