/**
 * K4 ciphertext visualizer — shows the 97-char ciphertext with confirmed
 * crib positions overlaid as color-coded highlights.
 */

const K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR";

interface Crib {
  label: string;
  plain: string;
  start: number;
  end: number;   // exclusive
  color: string;
  glow: string;
}

const CRIBS: Crib[] = [
  { label: "EAST",      plain: "EAST",      start: 22, end: 26, color: "#1d9e75", glow: "rgba(29,158,117,0.5)" },
  { label: "NORTHEAST", plain: "NORTHEAST", start: 26, end: 35, color: "#7f77dd", glow: "rgba(127,119,221,0.5)" },
  { label: "BERLIN",    plain: "BERLIN",    start: 63, end: 69, color: "#ef9f27", glow: "rgba(239,159,39,0.5)" },
  { label: "CLOCK",     plain: "CLOCK",     start: 69, end: 74, color: "#e24b4a", glow: "rgba(226,75,74,0.5)" },
];

function getCribAt(pos: number): Crib | null {
  return CRIBS.find((c) => pos >= c.start && pos < c.end) ?? null;
}

interface Props {
  highlightPosition?: number | null;
}

export default function K4CipherVisualizer({ highlightPosition }: Props) {
  const chars = K4.split("");

  return (
    <div style={{ fontFamily: "var(--mono)" }}>
      {/* Legend */}
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginBottom: "12px", fontSize: "11px" }}>
        {CRIBS.map((c) => (
          <span key={c.label} style={{ display: "flex", alignItems: "center", gap: "5px" }}>
            <span style={{
              display: "inline-block",
              width: "10px",
              height: "10px",
              borderRadius: "2px",
              background: c.color,
              boxShadow: `0 0 6px ${c.glow}`,
            }} />
            <span style={{ color: c.color }}>{c.label}</span>
            <span style={{ color: "var(--text)", opacity: 0.6 }}>pos {c.start}–{c.end - 1}</span>
          </span>
        ))}
      </div>

      {/* Ciphertext grid */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "2px", lineHeight: 1 }}>
        {chars.map((ch, i) => {
          const crib = getCribAt(i);
          const isHighlight = highlightPosition === i;
          return (
            <span
              key={i}
              title={`pos ${i}${crib ? ` — ${crib.plain[i - crib.start]}` : ""}`}
              style={{
                display: "inline-flex",
                flexDirection: "column",
                alignItems: "center",
                width: "20px",
                fontSize: "13px",
                fontWeight: crib ? "bold" : "normal",
                color: crib ? crib.color : "var(--text)",
                background: crib
                  ? `${crib.glow.replace("0.5", "0.12")}`
                  : isHighlight
                    ? "rgba(255,255,255,0.08)"
                    : "transparent",
                borderRadius: "2px",
                border: crib
                  ? `1px solid ${crib.glow.replace("0.5", "0.3")}`
                  : isHighlight
                    ? "1px solid rgba(255,255,255,0.3)"
                    : "1px solid transparent",
                textShadow: crib ? `0 0 8px ${crib.glow}` : undefined,
                cursor: "default",
                transition: "all 0.1s",
                paddingBottom: "1px",
              }}
            >
              {ch}
              <span style={{ fontSize: "7px", opacity: 0.4, color: "var(--text)" }}>
                {i}
              </span>
            </span>
          );
        })}
      </div>

      {/* Crib annotation row */}
      <div style={{ marginTop: "12px", display: "flex", flexDirection: "column", gap: "4px" }}>
        {CRIBS.map((c) => (
          <div key={c.label} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "11px" }}>
            <span style={{ color: c.color, minWidth: "90px", letterSpacing: "1px" }}>{c.label}</span>
            <span style={{ color: "var(--text)", opacity: 0.6 }}>
              cipher: <span style={{ color: c.color, fontWeight: "bold" }}>{K4.slice(c.start, c.end)}</span>
              {" → "}
              plain: <span style={{ color: c.color }}>{c.plain}</span>
              {" at pos "}<span style={{ opacity: 0.8 }}>{c.start}–{c.end - 1}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
