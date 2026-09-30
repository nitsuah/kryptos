import { useState } from "react";
import Decoder from "../components/Decoder";
import DecryptPanel from "../components/DecryptPanel";
import { PeekPanel, SealPanel, UnsealPanel } from "../components/VaultForms";

// Hands-on tools: the K1–K3 decoder on the left; ad-hoc decrypt and the
// vault on the right, one form at a time so the screen never scrolls.
type Tool = "decrypt" | "seal" | "unseal" | "check";

const TOOLS: { id: Tool; label: string }[] = [
  { id: "decrypt", label: "Decrypt" },
  { id: "seal", label: "Seal" },
  { id: "unseal", label: "Unseal" },
  { id: "check", label: "Check token" },
];

export default function Lab() {
  const [tool, setTool] = useState<Tool>("decrypt");
  return (
    <div className="fit lab-layout">
      <section className="pane lab-decoder">
        <h3>K1–K3 decoder</h3>
        <Decoder />
      </section>
      <section className="pane lab-tools">
        <div className="seg" role="group" aria-label="Tool">
          {TOOLS.map((t) => (
            <button
              type="button"
              key={t.id}
              className="seg-btn"
              aria-pressed={tool === t.id}
              onClick={() => setTool(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="lab-tool">
          {tool === "decrypt" && (
            <div className="form-block">
              <h3>Ad-hoc decrypt</h3>
              <DecryptPanel />
            </div>
          )}
          {tool === "seal" && <SealPanel />}
          {tool === "unseal" && <UnsealPanel />}
          {tool === "check" && <PeekPanel />}
        </div>
        {tool !== "decrypt" && (
          <p className="muted small">
            The vault seals text under the keyed-alphabet Vigenère and stores only the ciphertext; it needs
            DATABASE_URL on the server.
          </p>
        )}
      </section>
    </div>
  );
}
