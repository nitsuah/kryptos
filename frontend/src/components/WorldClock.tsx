// The Weltzeituhr at Alexanderplatz: the clock Sanborn says BERLIN CLOCK in
// K4 refers to. Drawn as the real thing is built: a solar-system topper that
// turns once a minute, a 24-sided drum of city panels (one per hour zone),
// a ring of hours beneath it, and the wind-rose mosaic it stands on.
//
// The drum starts centred on Berlin's panel. It turns with the arrow
// buttons or by clicking a panel; the hour ring always shows each panel's
// current standard time.

import { useEffect, useRef, useState } from "react";
import { BERLIN_FACE, WORLD_CLOCK_FACES, faceHour, offsetLabel } from "../worldclock";

const N = WORLD_CLOCK_FACES.length; // 24
const STEP = (2 * Math.PI) / N;
const CX = 300;
const R = 272; // drum radius
const RY = 30; // vertical radius of the drum's top and bottom ellipses
const TOP = 196; // y of the drum's top rim (front)
const H = 238; // drum height
const LINE = 11.2; // line height of the engraved names
// The view is cropped to the front of the drum so the panels are legible;
// the drum's sides fade out at the crop edges.
const VIEW = { x: 84, y: 22, w: 432, h: 582 };

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}

function useTicker(ms: number): Date {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), ms);
    return () => clearInterval(id);
  }, [ms]);
  return now;
}

// Eases the drum's rotation toward the target panel index (shortest way round).
function useDrumRotation(target: number): number {
  const [rot, setRot] = useState(target);
  const rotRef = useRef(rot);
  useEffect(() => {
    if (prefersReducedMotion()) {
      rotRef.current = target;
      setRot(target);
      return;
    }
    let raf = 0;
    const tick = () => {
      const cur = rotRef.current;
      let delta = target - cur;
      delta = ((delta + N / 2) % N + N) % N - N / 2;
      if (Math.abs(delta) < 0.002) {
        rotRef.current = target;
        setRot(target);
        return;
      }
      rotRef.current = cur + delta * 0.14;
      setRot(rotRef.current);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target]);
  return rot;
}

const rimX = (a: number) => CX + R * Math.sin(a);
const rimY = (a: number, y0: number) => y0 + RY * Math.cos(a);

function Topper({ now }: { now: Date }) {
  // One revolution per minute, per the clock's own mechanism.
  const t = prefersReducedMotion() ? 0 : (now.getUTCSeconds() + now.getUTCMilliseconds() / 1000) / 60;
  const orbits = [
    { rx: 96, ry: 20, speed: 1, r: 5 },
    { rx: 70, ry: 15, speed: 2, r: 4 },
    { rx: 46, ry: 10, speed: 3, r: 3.2 },
    { rx: 24, ry: 5.5, speed: 5, r: 2.4 },
  ];
  const cy = 74;
  return (
    <g className="wc-topper">
      <line x1={CX} y1={cy + 8} x2={CX} y2={TOP - RY - 2} className="wc-stem" />
      {orbits.map((o, i) => {
        const a = 2 * Math.PI * (t * o.speed + i * 0.23);
        return (
          <g key={i} transform={`rotate(-8 ${CX} ${cy})`}>
            <ellipse cx={CX} cy={cy} rx={o.rx} ry={o.ry} className="wc-orbit" />
            <circle cx={CX + o.rx * Math.cos(a)} cy={cy + o.ry * Math.sin(a)} r={o.r} className="wc-planet" />
          </g>
        );
      })}
      <circle cx={CX} cy={cy} r={9} className="wc-sun" />
    </g>
  );
}

function WindRose() {
  const cy = 556;
  const rx = 250;
  const ry = 44;
  const pts: string[] = [];
  for (let i = 0; i < 32; i++) {
    const a = (i * Math.PI) / 16;
    const long = i % 4 === 0 ? 1 : i % 2 === 0 ? 0.62 : 0.4;
    const r = i % 2 === 0 ? long : 0.16;
    pts.push(`${CX + rx * r * Math.sin(a)},${cy - ry * r * Math.cos(a)}`);
  }
  return (
    <g className="wc-rose">
      <ellipse cx={CX} cy={cy} rx={rx} ry={ry} className="wc-rose-ring" />
      <ellipse cx={CX} cy={cy} rx={rx * 0.78} ry={ry * 0.78} className="wc-rose-ring thin" />
      <polygon points={pts.join(" ")} className="wc-rose-star" />
      <text x={CX + 12} y={cy - ry + 14} className="wc-rose-n">
        N
      </text>
    </g>
  );
}

export default function WorldClock() {
  const now = useTicker(prefersReducedMotion() ? 10_000 : 150);
  const [target, setTarget] = useState(BERLIN_FACE);
  const rot = useDrumRotation(target);
  const centred = WORLD_CLOCK_FACES[((Math.round(rot) % N) + N) % N];

  // Faces sorted back to front so nearer panels paint over farther ones.
  const faces = WORLD_CLOCK_FACES.map((f, i) => {
    let d = i - rot;
    d = ((d + N / 2) % N + N) % N - N / 2;
    return { f, i, a: d * STEP };
  })
    .filter(({ a }) => Math.cos(a) > -0.02)
    .sort((p, q) => Math.cos(p.a) - Math.cos(q.a));

  return (
    <figure className="world-clock">
      <svg
        viewBox={`${VIEW.x} ${VIEW.y} ${VIEW.w} ${VIEW.h}`}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label={`World Clock turned to ${offsetLabel(centred.offset)}`}
      >
        <defs>
          <linearGradient id="wc-fade" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor="#fff" stopOpacity="0" />
            <stop offset="0.12" stopColor="#fff" stopOpacity="1" />
            <stop offset="0.88" stopColor="#fff" stopOpacity="1" />
            <stop offset="1" stopColor="#fff" stopOpacity="0" />
          </linearGradient>
          <mask id="wc-mask" maskUnits="userSpaceOnUse" x={VIEW.x} y={VIEW.y} width={VIEW.w} height={VIEW.h}>
            <rect x={VIEW.x} y={VIEW.y} width={VIEW.w} height={VIEW.h} fill="url(#wc-fade)" />
          </mask>
        </defs>
        <Topper now={now} />
        <g mask="url(#wc-mask)">

        {/* drum top cap */}
        <ellipse cx={CX} cy={TOP} rx={R} ry={RY} className="wc-cap" />
        <ellipse cx={CX} cy={TOP} rx={R * 0.9} ry={RY * 0.9} className="wc-cap-inner" />

        {faces.map(({ f, i, a }) => {
          const a0 = a - STEP / 2;
          const a1 = a + STEP / 2;
          const x0 = rimX(Math.max(a0, -Math.PI / 2));
          const x1 = rimX(Math.min(a1, Math.PI / 2));
          const lit = Math.max(0, Math.cos(a));
          if (x1 - x0 < 1.5) return null;
          const y0t = rimY(Math.max(a0, -Math.PI / 2), TOP);
          const y1t = rimY(Math.min(a1, Math.PI / 2), TOP);
          const poly = `${x0},${y0t} ${x1},${y1t} ${x1},${y1t + H} ${x0},${y0t + H}`;
          const mid = rimX(a);
          const midTop = rimY(a, TOP);
          const isBerlin = i === BERLIN_FACE;
          const clipId = `wc-clip-${i}`;
          const hour = faceHour(now, f.offset);
          return (
            <g
              key={f.offset}
              className={`wc-face${isBerlin ? " berlin" : ""}${f.cities.length === 0 ? " blank" : ""}`}
              onClick={() => setTarget(i)}
              style={{ opacity: 0.35 + 0.65 * lit }}
            >
              <title>{`${offsetLabel(f.offset)} · ${f.cities.length ? f.cities.join(", ") : "no plates read yet"}`}</title>
              <clipPath id={clipId}>
                <polygon points={poly} />
              </clipPath>
              <polygon points={poly} className="wc-panel" />
              <g clipPath={`url(#${clipId})`}>
                <g transform={`translate(${mid} ${midTop + 20}) scale(${Math.max(lit, 0.05)} 1)`}>
                  <text y={-2} className="wc-offset" textAnchor="middle">
                    {offsetLabel(f.offset)}
                  </text>
                  {f.cities.slice(0, 20).map((c, k) => (
                    <text key={c} y={15 + k * LINE} className={c === "BERLIN" ? "wc-city berlin" : "wc-city"} textAnchor="middle">
                      {c}
                    </text>
                  ))}
                  {f.cities.length === 0 && (
                    <text y={60} className="wc-city unread" textAnchor="middle">
                      · not read ·
                    </text>
                  )}
                </g>
              </g>
              {/* hour ring beneath the drum */}
              <g transform={`translate(${mid} ${midTop + H + 22}) scale(${Math.max(lit, 0.05)} 1)`}>
                <text className="wc-hour" textAnchor="middle">
                  {String(hour).padStart(2, "0")}
                </text>
              </g>
            </g>
          );
        })}

        {/* drum bottom rim and hour band */}
        <path
          d={`M ${CX - R} ${TOP + H} A ${R} ${RY} 0 0 0 ${CX + R} ${TOP + H}`}
          className="wc-rim"
        />
        <path
          d={`M ${CX - R} ${TOP + H + 32} A ${R} ${RY} 0 0 0 ${CX + R} ${TOP + H + 32}`}
          className="wc-rim thin"
        />
        </g>
        <line x1={CX} y1={TOP + H + RY + 34} x2={CX} y2={512} className="wc-stem" />
        <WindRose />
      </svg>
      <figcaption className="wc-caption">
        <button type="button" onClick={() => setTarget((t) => (t - 1 + N) % N)} aria-label="Turn the drum west">
          ◀
        </button>
        <span className="wc-readout">
          <b>{offsetLabel(centred.offset)}</b>{" "}
          <span className="wc-time">
            {String(faceHour(now, centred.offset)).padStart(2, "0")}:{String(now.getUTCMinutes()).padStart(2, "0")}
          </span>{" "}
          <span className="muted">
            {centred.cities.length ? `${centred.cities.length} plates` : "no plates read"}
          </span>
        </span>
        <button type="button" onClick={() => setTarget((t) => (t + 1) % N)} aria-label="Turn the drum east">
          ▶
        </button>
        {target !== BERLIN_FACE && (
          <button type="button" className="link-button" onClick={() => setTarget(BERLIN_FACE)}>
            Berlin
          </button>
        )}
      </figcaption>
    </figure>
  );
}
