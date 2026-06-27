import { KEYED_ALPHABET } from "../cipher";

export default function KeyedAlphabetTable({ highlight = {} }: { highlight?: Record<string, string> }) {
  return (
    <div className="panel" style={{ marginTop: '16px' }}>
      <h2>Keyed Alphabet</h2>
      <div className="body" style={{ letterSpacing: 3, fontSize: '1.2em' }}>
        {KEYED_ALPHABET.split("").map((ch, i) => {
          const color = highlight[i.toString()] || "var(--text)";
          return (
            <span key={i} style={{ color, fontWeight: highlight[i.toString()] ? "bold" : "normal" }}>
              {ch}
            </span>
          );
        })}
      </div>
    </div>
  );
}
