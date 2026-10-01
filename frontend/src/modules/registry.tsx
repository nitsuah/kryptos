import { ComponentType, ReactNode } from "react";
import { DashboardData } from "../shell/data";
import Attacks from "./Attacks";
import Lab from "./Lab";
import Ledger from "./Ledger";
import Overview from "./Overview";
import System from "./System";

export interface ModuleDef {
  id: string;
  /** Two-letter code on the dock. */
  code: string;
  title: string;
  /** One line under the title. */
  blurb: string;
  Component: ComponentType;
  /** Key numbers shown when this module is a side preview. */
  preview: (d: DashboardData) => [string, string][];
  /** Content for the CAUTION tag, or null when there's nothing to flag. */
  alert?: (d: DashboardData) => ReactNode | null;
}

const n = (v: number | undefined | null) => (v == null ? "–" : v.toLocaleString());

const activeJobs = (d: DashboardData) => d.jobs.filter((j) => j.status === "queued" || j.status === "running");

export const MODULES: ModuleDef[] = [
  {
    id: "k4",
    code: "K4",
    title: "K4",
    blurb: "Ciphertext, known letters, what's open, and the World Clock",
    Component: Overview,
    preview: (d) => [
      ["Known letters", "24 / 97"],
      ["Eliminated", n(d.ledger?.counts.eliminated)],
      ["Open", n(d.ledger?.counts.open)],
    ],
    alert: (d) =>
      d.online ? null : (
        <>
          The API is not answering{d.statusError ? `: ${d.statusError}` : "."} Live data returns when it does.
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
    blurb: "The P1–P22 queue, runs and recent jobs",
    Component: Attacks,
    preview: (d) => [
      ["Vectors", n(d.vectors.length)],
      ["Running", n(activeJobs(d).length)],
      ["Recent jobs", n(d.jobs.length)],
    ],
    alert: (d) => {
      const eureka = d.jobs.find((j) => j.status === "eureka");
      if (eureka) {
        return (
          <>
            <b>EUREKA</b> from {eureka.attack_id} (job {eureka.job_id.slice(0, 8)}). All four cribs matched. Check the
            snapshot first.
          </>
        );
      }
      const errs = d.jobs.filter((j) => j.status === "error");
      return errs.length ? (
        <>
          {errs.length} job{errs.length === 1 ? "" : "s"} ended in an error. Latest: {errs[0].attack_id}
          {errs[0].error ? ` — ${errs[0].error.slice(0, 100)}` : ""}.
        </>
      ) : null;
    },
  },
  {
    id: "lab",
    code: "LB",
    title: "Lab",
    blurb: "K1–K3 decoder, ad-hoc decrypt and the vault",
    Component: Lab,
    preview: () => [
      ["K1", "PALIMPSEST"],
      ["K2", "ABSCISSA"],
      ["K3", "double rotation"],
    ],
  },
  {
    id: "system",
    code: "SY",
    title: "System",
    blurb: "API and database, run history, live log, geometric pivot",
    Component: System,
    preview: (d) => [
      ["API", d.online ? "online" : "offline"],
      ["Database", d.status ? (d.status.db_enabled ? "connected" : "none") : "–"],
    ],
    alert: (d) =>
      d.status && !d.status.db_enabled ? (
        <>No DATABASE_URL: run history, job persistence and the vault are off. Everything else works.</>
      ) : null,
  },
];
