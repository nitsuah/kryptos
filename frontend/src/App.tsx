// Single-page dashboard shell (docs/reference/DASHBOARD.md).
//
// One screen, no tabs: the modules sit on a ring. The active module fills the
// stage; its neighbours stay visible at the sides as tilted previews on wide
// screens and slide in from the edges on narrow ones. Switch with the dock,
// the ring dial, the side previews, ←/→ keys, or a horizontal swipe. The
// active module is mirrored in the URL hash (#ledger) so views can be linked.
//
// Only the active module mounts its full component, so a module's own
// fetches run only while it is on screen. Previews read the shared data
// provider, which polls a handful of cheap endpoints.

import { CSSProperties, PointerEvent as ReactPointerEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { MODULES, ModuleDef } from "./modules/registry";
import { DashboardData, DashboardDataProvider, useDashboard } from "./shell/data";
import { Barcode, Caution, Glyph, OnlineArc, Rings, serial } from "./shell/deco";
import { NavContext } from "./shell/nav";
import { LEDGER_TIERS } from "./api";
import { TIER_LABEL } from "./k4";

const N = MODULES.length;
const STEP = 360 / N;

// Links from the nine-module layout (before 2026-09-30) still land somewhere sensible.
const HASH_ALIASES: Record<string, string> = {
  overview: "k4",
  jobs: "attacks",
  runs: "system",
  console: "system",
  decoder: "lab",
  vault: "lab",
};

function indexFromHash(): number {
  const raw = window.location.hash.replace(/^#/, "");
  const id = HASH_ALIASES[raw] ?? raw;
  const i = MODULES.findIndex((m) => m.id === id);
  return i >= 0 ? i : 0;
}

// Signed ring distance from the active face, in [-floor(N/2), floor(N/2)].
function ringOffset(i: number, active: number): number {
  const half = Math.floor(N / 2);
  return ((i - active + N + half) % N) - half;
}

function isTyping(el: EventTarget | null): boolean {
  if (!(el instanceof HTMLElement)) return false;
  return el.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName);
}

type ThemePref = "system" | "light" | "dark";

function useThemePref(): [ThemePref, () => void] {
  const [pref, setPref] = useState<ThemePref>(() => {
    try {
      const v = localStorage.getItem("kryptos-theme");
      return v === "light" || v === "dark" ? v : "system";
    } catch {
      return "system";
    }
  });
  useEffect(() => {
    const root = document.documentElement;
    if (pref === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", pref);
    try {
      if (pref === "system") localStorage.removeItem("kryptos-theme");
      else localStorage.setItem("kryptos-theme", pref);
    } catch {
      /* storage unavailable: the choice lasts for this page only */
    }
  }, [pref]);
  const cycle = useCallback(() => setPref((p) => (p === "system" ? "light" : p === "light" ? "dark" : "system")), []);
  return [pref, cycle];
}

function useUtc(): string {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now.toISOString().slice(11, 19);
}

function RingDial({ active, onPick }: { active: number; onPick: (i: number) => void }) {
  return (
    // Pointer shortcut only; the dock below is the keyboard-accessible control.
    <svg className="ring-dial" viewBox="-50 -50 100 100" aria-hidden="true" focusable="false">
      <circle r={44} className="rd-outer" />
      <circle r={30} className="rd-inner" />
      <g style={{ transform: `rotate(${-active * STEP}deg)` }} className="rd-turn">
        {MODULES.map((m, i) => (
          <g key={m.id} transform={`rotate(${i * STEP})`}>
            <line
              y1={-44}
              y2={-33}
              className={i === active ? "rd-tick on" : "rd-tick"}
              onClick={() => onPick(i)}
            >
              <title>{m.title}</title>
            </line>
          </g>
        ))}
      </g>
      <text y={4} className="rd-num" textAnchor="middle">
        {String(active + 1).padStart(2, "0")}
      </text>
    </svg>
  );
}

function Meters({ data }: { data: DashboardData }) {
  const counts = data.ledger?.counts;
  const total = counts ? LEDGER_TIERS.reduce((s, t) => s + counts[t], 0) : 0;
  return (
    <ul className="meters" aria-label="Ledger share by tier">
      {LEDGER_TIERS.map((t) => (
        <li key={t} title={`${TIER_LABEL[t]}: ${counts ? counts[t] : "–"}`}>
          <span className={`meter tier-${t}`}>
            <span style={{ width: total ? `${(counts![t] / total) * 100}%` : "0%" }} />
          </span>
        </li>
      ))}
    </ul>
  );
}

function Preview({ mod, data, onOpen }: { mod: ModuleDef; data: DashboardData; onOpen: () => void }) {
  return (
    <button type="button" className="preview" onClick={onOpen} aria-label={`Open ${mod.title}`}>
      <span className="preview-code">{mod.code}</span>
      <span className="preview-title">{mod.title}</span>
      <span className="preview-blurb">{mod.blurb}</span>
      <dl className="preview-stats">
        {mod.preview(data).map(([k, v]) => (
          <div key={k}>
            <dt>{k}</dt>
            <dd>{v}</dd>
          </div>
        ))}
      </dl>
    </button>
  );
}

function Face({ mod, index, data }: { mod: ModuleDef; index: number; data: DashboardData }) {
  const alert = mod.alert?.(data) ?? null;
  const Body = mod.Component;
  return (
    <div className="frame">
      <header className="frame-head">
        <span className="frame-code" aria-hidden="true">
          B.{String(index + 1).padStart(3, "0")}
        </span>
        <div className="frame-titles">
          <span className="kicker">
            KRYPTOS · {mod.code} <span className="kicker-level">LEVEL-{index + 1}</span>
          </span>
          <h2 id={`mod-${mod.id}-title`}>{mod.title}</h2>
          <span className="frame-blurb">{mod.blurb}</span>
        </div>
        <div className="frame-tags" aria-hidden="true">
          <Barcode seed={mod.id} className="frame-barcode" />
          <div className="frame-tags-row">
            <Meters data={data} />
            <Glyph seed={mod.id} className="frame-glyph" />
          </div>
          <span className="frame-serial">{serial(mod.id)}</span>
        </div>
      </header>
      <div className={`frame-main${alert ? " has-alert" : ""}`}>
        <div className="screen">
          <div className="screen-scroll">
            <Body />
          </div>
        </div>
        {alert && <Caution seed={mod.id}>{alert}</Caution>}
      </div>
    </div>
  );
}

function Shell() {
  const data = useDashboard();
  const [active, setActive] = useState(indexFromHash);
  const [theme, cycleTheme] = useThemePref();
  const utc = useUtc();
  const stageRef = useRef<HTMLDivElement | null>(null);
  const swipe = useRef<{ x: number; y: number; id: number } | null>(null);

  const go = useCallback((i: number) => setActive(((i % N) + N) % N), []);
  const next = useCallback(() => setActive((a) => (a + 1) % N), []);
  const prev = useCallback(() => setActive((a) => (a - 1 + N) % N), []);
  const nav = useMemo(
    () => ({
      go: (id: string) => {
        const i = MODULES.findIndex((m) => m.id === id);
        if (i >= 0) setActive(i);
      },
    }),
    [],
  );

  // Hash ⇄ active module.
  useEffect(() => {
    const want = `#${MODULES[active].id}`;
    if (window.location.hash !== want) window.history.replaceState(null, "", want);
    document.title = `${MODULES[active].title} · KRYPTOS`;
  }, [active]);
  useEffect(() => {
    const onHash = () => setActive(indexFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  // ←/→ (and [ / ]) switch modules unless focus is in a form field or inside a module.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || isTyping(e.target)) return;
      // Inside a module, arrow keys belong to whatever has focus there (lists, the
      // cipher matrix, buttons); switching modules would unmount it mid-use.
      if (e.target instanceof HTMLElement && e.target.closest(".screen, .cm-grid")) return;
      if (e.key === "ArrowRight" || e.key === "]") {
        e.preventDefault();
        next();
      } else if (e.key === "ArrowLeft" || e.key === "[") {
        e.preventDefault();
        prev();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, prev]);

  // Horizontal swipe on touch/pen, ignored inside things that scroll sideways.
  const onPointerDown = (e: ReactPointerEvent) => {
    if (e.pointerType === "mouse") return;
    const t = e.target as HTMLElement;
    if (t.closest(".table-wrap, pre, input, textarea, select, .cm-grid, .logtail-body, .no-swipe")) return;
    swipe.current = { x: e.clientX, y: e.clientY, id: e.pointerId };
  };
  const onPointerUp = (e: ReactPointerEvent) => {
    const s = swipe.current;
    swipe.current = null;
    if (!s || s.id !== e.pointerId) return;
    const dx = e.clientX - s.x;
    const dy = e.clientY - s.y;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) {
      if (dx < 0) next();
      else prev();
    }
  };

  const mod = MODULES[active];

  return (
    <NavContext.Provider value={nav}>
      <div className="shell">
        <header className="hud">
          <div className="hud-left">
            <RingDial active={active} onPick={go} />
            <div className="brand">
              <span className="brand-name">KRYPTOS</span>
              <span className="brand-sub">K4 workstation</span>
            </div>
          </div>
          <div className="hud-center" aria-hidden="true">
            <span className="hud-tag">PROTECTICON</span>
            <Barcode seed="kryptos-hud" bars={44} className="hud-barcode" />
            <span className="hud-level">SECTION K4</span>
          </div>
          <div className="hud-right">
            <OnlineArc online={data.online} />
            <span className="hud-clock" aria-label="UTC time">
              {utc} <small>UTC</small>
            </span>
            <button
              type="button"
              className="theme-btn"
              onClick={cycleTheme}
              aria-label={`Colour theme: ${theme}. Click to change.`}
              title={`Theme: ${theme}`}
            >
              {theme === "system" ? "◐" : theme === "light" ? "○" : "●"}
            </button>
          </div>
        </header>

        <main
          className="stage"
          ref={stageRef}
          aria-roledescription="carousel"
          aria-label="Dashboard modules"
          onPointerDown={onPointerDown}
          onPointerUp={onPointerUp}
          onPointerCancel={() => (swipe.current = null)}
        >
          <Rings turn={-active * STEP} />
          {MODULES.map((m, i) => {
            const d = ringOffset(i, active);
            const ad = Math.abs(d);
            return (
              <section
                key={m.id}
                className={`face${d === 0 ? " is-active" : ad === 1 ? " is-near" : " is-far"}`}
                style={{ "--d": d, "--ad": ad } as CSSProperties}
                data-side={d < 0 ? "left" : d > 0 ? "right" : "center"}
                aria-roledescription="slide"
                aria-label={`${m.title}, ${i + 1} of ${N}`}
                aria-hidden={ad > 1}
              >
                {d === 0 ? (
                  <Face mod={m} index={i} data={data} />
                ) : ad === 1 ? (
                  <Preview mod={m} data={data} onOpen={() => go(i)} />
                ) : null}
              </section>
            );
          })}
          <button type="button" className="stage-arrow left" onClick={prev} aria-label="Previous module">
            ‹
          </button>
          <button type="button" className="stage-arrow right" onClick={next} aria-label="Next module">
            ›
          </button>
        </main>

        <nav className="dock" aria-label="Modules">
          <ol className="dock-ring">
            {MODULES.map((m, i) => (
              <li key={m.id}>
                <button
                  type="button"
                  className="dock-btn"
                  aria-current={i === active ? "true" : undefined}
                  onClick={() => go(i)}
                  title={`${m.title} — ${m.blurb}`}
                >
                  <span className="dock-bar" aria-hidden="true" />
                  <span className="dock-code">{m.code}</span>
                  <span className="dock-title">{m.title}</span>
                  {m.alert?.(data) ? <span className="dock-alert" aria-label="needs attention" /> : null}
                </button>
              </li>
            ))}
          </ol>
          <span className="dock-hint" aria-hidden="true">
            ← → or swipe
          </span>
        </nav>

        <div className="sr-only" aria-live="polite">
          {mod.title} module, {active + 1} of {N}
        </div>
      </div>
    </NavContext.Provider>
  );
}

export default function App() {
  return (
    <DashboardDataProvider>
      <Shell />
    </DashboardDataProvider>
  );
}
