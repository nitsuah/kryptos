import { FormEvent, useState } from "react";
import { ApiError, api } from "../api";

const SECTIONS = ["K1", "K2", "K3", "K4"];

export default function DecryptPanel() {
  const [section, setSection] = useState("K1");
  const [ciphertext, setCiphertext] = useState("");
  const [key, setKey] = useState("");
  const [plaintext, setPlaintext] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const keyRequired = section === "K1" || section === "K2";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setPlaintext(null);
    try {
      const resp = await api.decrypt(section, ciphertext.trim(), key.trim() || undefined);
      setPlaintext(resp.plaintext);
    } catch (err) {
      setError(err instanceof ApiError ? `[${err.status}] ${err.message}` : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <div className="row">
        <div className="field" style={{ minWidth: 90 }}>
          <label>Section</label>
          <select value={section} onChange={(e) => setSection(e.target.value)}>
            {SECTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="field" style={{ flex: 1, minWidth: 160 }}>
          <label>Key {keyRequired ? "(required)" : "(ignored)"}</label>
          <input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder={keyRequired ? "PALIMPSEST" : "—"}
            disabled={!keyRequired}
          />
        </div>
      </div>
      <div className="field">
        <label>Ciphertext</label>
        <textarea
          value={ciphertext}
          onChange={(e) => setCiphertext(e.target.value)}
          rows={3}
          placeholder="EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ..."
        />
      </div>
      <button type="submit" disabled={busy || ciphertext.trim().length === 0}>
        {busy ? "Decrypting…" : "Execute"}
      </button>
      {error && <div className="result error">{error}</div>}
      {plaintext !== null && <div className="result plaintext">{plaintext}</div>}
    </form>
  );
}
