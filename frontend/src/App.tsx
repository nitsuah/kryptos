import { useEffect, useState } from "react";
import { api, StatusResponse } from "./api";
import Topbar from "./components/Topbar";
import OpsCenter from "./pages/OpsCenter";

export default function App() {
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
      <main className="main">
        {error && <div className="banner">API unreachable: {error}</div>}
        {status && !status.db_enabled && (
          <div className="banner">
            DATABASE_URL not configured — run history is empty. Decrypt still works.
          </div>
        )}
        <OpsCenter status={status} />
      </main>
    </div>
  );
}
