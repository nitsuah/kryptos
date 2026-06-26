import { useEffect, useState } from "react";
import { api, StatusResponse } from "./api";
import Topbar from "./components/Topbar";
import OpsCenter from "./pages/OpsCenter";
import Decode from "./pages/Decode";
import Database from "./pages/Database";
import Vault from "./pages/Vault";
import K4AttackDashboard from "./pages/K4AttackDashboard";

type Page = "ops" | "decode" | "database" | "vault" | "k4";

export default function App() {
  const [page, setPage] = useState<Page>("ops");
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refreshStatus() {
    try {
      setStatus(await api.status());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  useEffect(() => {
    refreshStatus();
    const id = setInterval(refreshStatus, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="app">
      <Topbar status={status} />
      <nav className="nav">
        <button className={page === "ops" ? "active" : ""} onClick={() => setPage("ops")}>
          Ops Center
        </button>
        <button className={page === "decode" ? "active" : ""} onClick={() => setPage("decode")}>
          Decode
        </button>
        <button className={page === "database" ? "active" : ""} onClick={() => setPage("database")}>
          Database
        </button>
        <button className={page === "vault" ? "active" : ""} onClick={() => setPage("vault")}>
          Vault
        </button>
        <button className={page === "k4" ? "active" : ""} onClick={() => setPage("k4")}>
          K4 Dashboard
        </button>
      </nav>
      <main className="main">
        {error && <div className="banner">API unreachable: {error}</div>}
        {page === "ops" && status && !status.db_enabled && (
          <div className="banner">
            DATABASE_URL not configured — run history is empty. Decrypt still works.
          </div>
        )}
        {page === "ops" && <OpsCenter status={status} />}
        {page === "decode" && <Decode />}
        {page === "database" && <Database status={status} />}
        {page === "vault" && <Vault />}
        {page === "k4" && <K4AttackDashboard />}
      </main>
    </div>
  );
}
