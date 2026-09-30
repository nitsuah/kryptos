import DecryptPanel from "../components/DecryptPanel";
import LogTail from "../components/LogTail";

// Ad-hoc decrypt against POST /api/decrypt, and the live backend log
// (SSE, GET /api/stream/logs).
export default function Console() {
  return (
    <div className="grid console-grid">
      <section className="sub">
        <h3>Ad-hoc decrypt</h3>
        <DecryptPanel />
      </section>
      <section className="sub">
        <h3>Live log</h3>
        <LogTail />
      </section>
    </div>
  );
}
