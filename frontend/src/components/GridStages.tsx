import { useState } from "react";
import { Grid, k3Stages } from "../cipher";

function GridView({ grid }: { grid: Grid }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "auto", borderCollapse: "collapse" }}>
        <tbody>
          {grid.map((row, r) => (
            <tr key={r}>
              {row.map((ch, c) => (
                <td
                  key={c}
                  style={{
                    border: "0.5px solid var(--border)",
                    padding: "1px 4px",
                    textAlign: "center",
                    color: ch === " " ? "var(--border)" : "var(--text)",
                  }}
                >
                  {ch === " " ? "·" : ch}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Stepped K3 double-rotational-transposition visualizer: fill 24-col grid,
// rotate 90cw, reshape to 8 cols, rotate 90cw -> plaintext.
export default function GridStages({ cipher }: { cipher: string }) {
  const stages = k3Stages(cipher);
  const [step, setStep] = useState(0);
  const stage = stages[step];

  return (
    <div>
      <div className="row" style={{ alignItems: "center", marginBottom: 12 }}>
        <button onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0}>
          ◀ Prev
        </button>
        <button onClick={() => setStep((s) => Math.min(stages.length - 1, s + 1))} disabled={step === stages.length - 1}>
          Next ▶
        </button>
        <span className="muted">
          stage {step + 1}/{stages.length}
        </span>
      </div>
      <div className="field">
        <label>{stage.label}</label>
        <div className="muted" style={{ fontSize: 11 }}>
          {stage.grid.length} rows × {stage.grid[0]?.length ?? 0} cols
        </div>
      </div>
      <GridView grid={stage.grid} />
    </div>
  );
}
