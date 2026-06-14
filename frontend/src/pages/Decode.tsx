import { useState } from "react";
import { SECTION_DATA, decodeK3, decodeVigenere } from "../cipher";
import { ApiError, api } from "../api";
import SubstitutionAnimator from "../components/SubstitutionAnimator";
import GridStages from "../components/GridStages";

type Section = "K1" | "K2" | "K3";
const SECTIONS: Section[] = ["K1", "K2", "K3"];

function localPlaintext(section: Section): string {
  const data = SECTION_DATA[section];
  return section === "K3" ? decodeK3(data.cipher) : decodeVigenere(data.cipher, data.key ?? "");
}

export default function Decode() {
  const [section, setSection] = useState<Section>("K1");
  const [check, setCheck] = useState<string | null>(null);
  const data = SECTION_DATA[section];

  // Cross-check the client-side animation against the backend pipeline.
  async function verify() {
    setCheck("checking…");
    try {
      const resp = await api.decrypt(section, data.cipher, data.key ?? undefined);
      const local = localPlaintext(section);
      const match = resp.plaintext.replace(/\s+$/, "") === local.replace(/\s+$/, "");
      setCheck(match ? "✓ matches backend /api/decrypt" : "✗ differs from backend");
    } catch (e) {
      setCheck(e instanceof ApiError ? `backend error [${e.status}]` : String(e));
    }
  }

  return (
    <>
      <div className="panel">
        <h2>K1–K3 decoder</h2>
        <div className="body">
          <div className="row" style={{ marginBottom: 12 }}>
            {SECTIONS.map((s) => (
              <button
                key={s}
                onClick={() => {
                  setSection(s);
                  setCheck(null);
                }}
                style={{ borderColor: s === section ? "var(--accent)" : "var(--border)" }}
              >
                {s}
              </button>
            ))}
            <button onClick={verify}>Verify vs backend</button>
            {check && <span className="muted">{check}</span>}
          </div>
          <div className="muted" style={{ marginBottom: 12 }}>
            {data.note}
          </div>
          {section === "K3" ? (
            <GridStages cipher={data.cipher} />
          ) : (
            <SubstitutionAnimator cipher={data.cipher} keyword={data.key ?? ""} />
          )}
        </div>
      </div>
    </>
  );
}
