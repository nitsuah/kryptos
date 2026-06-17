import { useState } from "react";
import { ApiError, VaultPeekResponse, VaultSealResponse, VaultUnsealResponse, api } from "../api";

// Vault page (docs/analysis/K4-FRONTEND.md): seal a secret under the keyed-
// alphabet Vigenère, share the opaque token, and unseal it once with the key.
// Backend: kryptos.api.vault_routes. Requires DATABASE_URL (else 503).

const TTL_OPTIONS: { label: string; seconds: number }[] = [
  { label: "1 hour", seconds: 3600 },
  { label: "1 day", seconds: 86400 },
  { label: "1 week", seconds: 604800 },
  { label: "30 days", seconds: 2592000 },
  { label: "No expiry", seconds: 0 },
];

function errText(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 503) return "Vault unavailable — the server has no DATABASE_URL configured.";
    return `[${e.status}] ${e.message}`;
  }
  return String(e);
}

function fmtExpiry(iso: string | null): string {
  return iso ? new Date(iso).toLocaleString() : "never";
}

function SealPanel() {
  const [plaintext, setPlaintext] = useState("");
  const [key, setKey] = useState("");
  const [ttl, setTtl] = useState(86400);
  const [maxReads, setMaxReads] = useState(1);
  const [result, setResult] = useState<VaultSealResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  async function seal() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.vaultSeal(plaintext, key, ttl, maxReads));
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  }

  function copyToken() {
    if (!result) return;
    navigator.clipboard?.writeText(result.token).then(
      () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      },
      () => undefined,
    );
  }

  return (
    <div className="panel">
      <h2>Seal a secret</h2>
      <div className="body">
        <div className="field">
          <label>Plaintext</label>
          <textarea
            rows={3}
            value={plaintext}
            onChange={(e) => setPlaintext(e.target.value)}
            placeholder="The secret to seal"
          />
        </div>
        <div className="field">
          <label>Key (keyed-alphabet Vigenère)</label>
          <input value={key} onChange={(e) => setKey(e.target.value)} placeholder="e.g. PALIMPSEST" />
        </div>
        <div className="row">
          <div className="field" style={{ flex: 1 }}>
            <label>Expires after</label>
            <select value={ttl} onChange={(e) => setTtl(Number(e.target.value))}>
              {TTL_OPTIONS.map((o) => (
                <option key={o.seconds} value={o.seconds}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label>Max reads</label>
            <input
              type="number"
              min={1}
              max={1000}
              value={maxReads}
              onChange={(e) => setMaxReads(Math.max(1, Number(e.target.value) || 1))}
            />
          </div>
        </div>
        <button onClick={seal} disabled={busy || !plaintext || !key}>
          {busy ? "Sealing…" : "Seal"}
        </button>

        {error && <div className="result error">{error}</div>}
        {result && (
          <div className="result">
            <div>
              <strong>Token:</strong> {result.token}{" "}
              <button onClick={copyToken} style={{ padding: "2px 6px" }}>
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
            <div className="muted">
              cipher {result.cipher} · max reads {result.max_reads} · expires{" "}
              {fmtExpiry(result.expires_at)}
            </div>
            <div className="muted">Share the token and key separately — the key is never stored.</div>
          </div>
        )}
      </div>
    </div>
  );
}

function UnsealPanel() {
  const [token, setToken] = useState("");
  const [key, setKey] = useState("");
  const [result, setResult] = useState<VaultUnsealResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function unseal() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.vaultUnseal(token.trim(), key));
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <h2>Unseal</h2>
      <div className="body">
        <div className="field">
          <label>Token</label>
          <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="vault token (UUID)" />
        </div>
        <div className="field">
          <label>Key</label>
          <input value={key} onChange={(e) => setKey(e.target.value)} placeholder="the sealing key" />
        </div>
        <button onClick={unseal} disabled={busy || !token || !key}>
          {busy ? "Unsealing…" : "Unseal (consumes a read)"}
        </button>

        {error && <div className="result error">{error}</div>}
        {result && (
          <div className="result">
            <div className="plaintext" style={{ marginBottom: 6 }}>
              {result.plaintext}
            </div>
            <div className="muted">
              {result.reads_remaining} read{result.reads_remaining === 1 ? "" : "s"} remaining · expires{" "}
              {fmtExpiry(result.expires_at)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function PeekPanel() {
  const [token, setToken] = useState("");
  const [result, setResult] = useState<VaultPeekResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function peek() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.vaultPeek(token.trim()));
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <h2>Status</h2>
      <div className="body">
        <div className="row" style={{ alignItems: "flex-end" }}>
          <div className="field" style={{ flex: 1, marginBottom: 0 }}>
            <label>Token</label>
            <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="check a token without reading" />
          </div>
          <button onClick={peek} disabled={busy || !token}>
            {busy ? "…" : "Check"}
          </button>
        </div>

        {error && <div className="result error">{error}</div>}
        {result && (
          <div className="result">
            <div>
              <strong>{result.status}</strong>
            </div>
            <div className="muted">
              reads {result.reads_used}/{result.max_reads} · sealed {fmtExpiry(result.sealed_at)} · expires{" "}
              {fmtExpiry(result.expires_at)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Vault() {
  return (
    <>
      <SealPanel />
      <UnsealPanel />
      <PeekPanel />
    </>
  );
}
