import { ComponentType, ReactNode } from "react";
import { DashboardData } from "../shell/data";
import Attacks from "./Attacks";
import Console from "./Console";
import Decoder from "./Decoder";
import Jobs from "./Jobs";
import Ledger from "./Ledger";
import Overview from "./Overview";
import Runs from "./Runs";
import System from "./System";
import Vault from "./Vault";

export interface ModuleDef {
  id: string;
  /** Two-letter code on the dock. */
  code: string;
  title: string;
  /** One line under the title. */
  blurb: string;
  Component: ComponentType;
  /** Key numbers shown when this module is a side preview or on the dock tooltip. */
  preview: (d: DashboardData) => [string, string][];
  /** Content for the CAUTION tag, or null when there's nothing to flag. */
  alert?: (d: DashboardData) => ReactNode | null;
}

const n = (v: number | undefined | null) => (v == null ? "–" : v.toLocaleString());

const activeJobs = (d: DashboardData) => d.jobs.filter((j) => j.status === "queued" || j.status === "running");

export const MODULES: ModuleDef[] = [
  {
    id: "overview",
    code: "OV",
    title: "Overview",
    blurb: "K4 ciphertext, known letters, ledger totals and clocks",
    Component: Overview,
    preview: (d) => [
      ["Known letters", "24 / 97"],
      ["Eliminated", n(d.ledger?.counts.eliminated)],
      ["Open", n(d.ledger?.counts.open)],
    ],
    alert: (d) =>
      d.online ? null : (
        <>
          The API is not answering{d.statusError ? `: ${d.statusError}` : "."} Live data will return when it does.
        </>
      ),
  },
  {
    id: "ledger",
    code: "LG",
    title: "Ledger",
    blurb: "Every cipher family: eliminated, statistical, sampled or open",
    Component: Ledger,
    preview: (d) => [
      ["Families", n(d.ledger?.entries.length)],
      ["Statistical", n(d.ledger?.counts.statistical)],
      ["Sampled null", n(d.ledger?.counts.sampled_null)],
    ],
  },
  {
    id: "attacks",
    code: "AT",
    title: "Attacks",
    blurb: "P1–P22 attack queue; run any runnable vector",
    Component: Attacks,
    preview: (d) => [
      ["Vectors", n(d.vectors.length)],
      ["Runnable", n(d.vectors.filter((v) => v.runnable).length)],
      ["Running", n(activeJobs(d).length)],
    ],
    alert: (d) => {
      const eureka = d.jobs.find((j) => j.status === "eureka");
      return eureka ? (
        <>
          <b>EUREKA</b> from {eureka.attack_id} (job {eureka.job_id.slice(0, 8)}). All four cribs matched. Check the
          snapshot before anything else.
        </>
      ) : null;
    },
  },
  {
    id: "jobs",
    code: "JB",
    title: "Jobs",
    blurb: "Recent attack jobs, progress and results",
    Component: Jobs,
    preview: (d) => [
      ["Recent", n(d.jobs.length)],
      ["Running", n(activeJobs(d).length)],
      ["Errors", n(d.jobs.filter((j) => j.status === "error").length)],
    ],
    alert: (d) => {
      const errs = d.jobs.filter((j) => j.status === "error");
      return errs.length ? (
        <>
          {errs.length} job{errs.length === 1 ? "" : "s"} ended in an error. Latest: {errs[0].attack_id}
          {errs[0].error ? ` — ${errs[0].error.slice(0, 120)}` : ""}.
        </>
      ) : null;
    },
  },
  {
    id: "runs",
    code: "RN",
    title: "Runs",
    blurb: "Campaign run history and top candidates",
    Component: Runs,
    preview: (d) => [
      ["Runs", d.status?.db_enabled ? n(d.status.table_counts.campaign_runs) : "no DB"],
      ["Candidates", d.status?.db_enabled ? n(d.status.table_counts.candidates) : "–"],
    ],
    alert: (d) =>
      d.status && !d.status.db_enabled ? <>No DATABASE_URL on this server, so there is no run history to show.</> : null,
  },
  {
    id: "console",
    code: "CN",
    title: "Console",
    blurb: "Ad-hoc decrypt and the live backend log",
    Component: Console,
    preview: () => [
      ["Decrypt", "K1–K4"],
      ["Log", "live SSE"],
    ],
  },
  {
    id: "decoder",
    code: "DC",
    title: "Decoder",
    blurb: "How K1–K3 were enciphered, step by step",
    Component: Decoder,
    preview: () => [
      ["K1", "PALIMPSEST"],
      ["K2", "ABSCISSA"],
      ["K3", "double rotation"],
    ],
  },
  {
    id: "vault",
    code: "VT",
    title: "Vault",
    blurb: "Seal a secret under a keyed Vigenère; unseal once",
    Component: Vault,
    preview: (d) => [["Status", d.status?.db_enabled ? "available" : "needs DB"]],
    alert: (d) =>
      d.status && !d.status.db_enabled ? <>The vault stores sealed text in Neon; without DATABASE_URL it returns 503.</> : null,
  },
  {
    id: "system",
    code: "SY",
    title: "System",
    blurb: "API, database tables and the geometric pivot",
    Component: System,
    preview: (d) => [
      ["API", d.online ? "online" : "offline"],
      ["Database", d.status ? (d.status.db_enabled ? "connected" : "none") : "–"],
    ],
  },
];
