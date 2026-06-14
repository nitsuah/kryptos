import { useEffect, useState } from "react";
import { StatusResponse } from "../api";

function useUtcClock(): string {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now.toISOString().replace("T", " ").slice(0, 19) + " UTC";
}

// Agent pip colour reflects whether the backend / DB is live. Per-agent
// state will come from /api/status once the autonomous loop reports it.
function pipClass(online: boolean, agent: string): string {
  if (!online) return "grey";
  return agent === "Q" ? "purple" : "green";
}

export default function Topbar({ status }: { status: StatusResponse | null }) {
  const clock = useUtcClock();
  const online = status !== null;
  return (
    <div className="topbar">
      <span className="brand">KRYPTOS</span>
      <div className="agent-pips">
        {["SPY", "OPS", "Q"].map((a) => (
          <span className="pip" key={a}>
            <span className={`dot ${pipClass(online, a)}`} />
            {a}
          </span>
        ))}
      </div>
      <span className="clock">{clock}</span>
    </div>
  );
}
