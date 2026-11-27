import { FormEvent, useState } from "react";
import { ApiError, api, hasOperatorToken, isLocalHost, isReadOnly } from "../api";
import { decodeK3, decodeVigenere } from "../cipher";
import FormField from "./FormField";

const SECTIONS = ["K1", "K2", "K3", "K4"];
export default function DecryptPanel() {
  const [section, setSection] = useState("K1");
  const [ciphertext, setCiphertext] = useState("");
  const [key, setKey] = useState("");
  const [plaintext, setPlaintext] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const keyRequired = section === "K1" || section === "K2";
  // Visitors decode solved sections here in the browser; K4 needs the server.
  const readOnly = isReadOnly();
  const unauthenticatedLocal = isLocalHost() && !hasOperatorToken();
  const useBrowserDecoder = readOnly || (unauthenticatedLocal && section !== "K4");
  const blocked = readOnly && section === "K4";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setPlaintext(null);
    try {
      if (useBrowserDecoder) {
        if (keyRequired && !/[A-Za-z]/.test(key)) throw new Error(`${section} requires a key`);
        setPlaintext(keyRequired ? decodeVigenere(ciphertext, key) : decodeK3(ciphertext));
        return;
      }
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
        <FormField label="Section" style={{ minWidth: 90 }}>
          <select value={section} onChange={(e) => setSection(e.target.value)}>
            {SECTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label={`Key ${keyRequired ? "(required)" : "(ignored)"}`} style={{ flex: 1, minWidth: 160 }}>
          <input
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder={keyRequired ? "PALIMPSEST" : "—"}
            disabled={!keyRequired}
          />
        </FormField>
      </div>
      <FormField label="Ciphertext">
        <textarea
          value={ciphertext}
          onChange={(e) => setCiphertext(e.target.value)}
          rows={3}
          placeholder="EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ..."
        />
      </FormField>
      {useBrowserDecoder && (
        <p className="muted small">
          {blocked
            ? "K4 is unsolved, and decrypting it on the server is operator only."
            : "K1 to K3 are decrypted in your browser."}
        </p>
      )}
      <button type="submit" disabled={busy || blocked || ciphertext.trim().length === 0}>
        {busy ? "Decrypting…" : "Execute"}
      </button>
      {error && <div className="result error">{error}</div>}
      {plaintext !== null && <div className="result plaintext">{plaintext}</div>}
    </form>
  );
}
