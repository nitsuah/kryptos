// Decorative pieces for the Ghost in the Shell look: barcodes, glyph blocks,
// the background rings and the CAUTION tag. Everything is derived
// deterministically from a seed string, so the same module always draws the
// same barcode, and nothing here carries data the user needs to read.

import { ReactNode, useMemo } from "react";

// Small deterministic PRNG (mulberry32) seeded from a string hash.
function rng(seed: string): () => number {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  let a = h >>> 0;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function Barcode({ seed, bars = 36, className = "" }: { seed: string; bars?: number; className?: string }) {
  const rects = useMemo(() => {
    const r = rng(seed);
    const out: { x: number; w: number }[] = [];
    let x = 0;
    for (let i = 0; i < bars; i++) {
      const w = 1 + Math.floor(r() * 3);
      if (r() > 0.35) out.push({ x, w });
      x += w + 1;
    }
    return { out, width: x };
  }, [seed, bars]);
  return (
    <svg
      className={`barcode ${className}`}
      viewBox={`0 0 ${rects.width} 10`}
      preserveAspectRatio="none"
      aria-hidden="true"
      focusable="false"
    >
      {rects.out.map((b, i) => (
        <rect key={i} x={b.x} y={0} width={b.w} height={10} />
      ))}
    </svg>
  );
}

export function Glyph({ seed, size = 9, className = "" }: { seed: string; size?: number; className?: string }) {
  const cells = useMemo(() => {
    const r = rng(`glyph:${seed}`);
    const out: [number, number][] = [];
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        // Solid 3×3 "finder" blocks in three corners, noise elsewhere.
        const finder = (x < 3 && y < 3) || (x >= size - 3 && y < 3) || (x < 3 && y >= size - 3);
        const corner = (x <= 3 && y <= 3) || (x >= size - 4 && y <= 3) || (x <= 3 && y >= size - 4);
        const gutter = corner && !finder;
        if (finder || (!gutter && r() > 0.52)) out.push([x, y]);
      }
    }
    return out;
  }, [seed, size]);
  return (
    <svg className={`glyph ${className}`} viewBox={`0 0 ${size} ${size}`} aria-hidden="true" focusable="false">
      {cells.map(([x, y]) => (
        <rect key={`${x}-${y}`} x={x} y={y} width={1.02} height={1.02} />
      ))}
    </svg>
  );
}

// Hex-ish serial line under the barcodes, e.g. "0180230-0180180101".
export function serial(seed: string): string {
  const r = rng(`serial:${seed}`);
  const digits = (n: number) => Array.from({ length: n }, () => (r() > 0.5 ? "1" : "0") + "").join("");
  return `0${Math.floor(r() * 900000 + 100000)}-${digits(10)}`;
}

// Concentric rings behind the stage. `turn` rotates the tick ring so that
// switching modules visibly turns the dial.
export function Rings({ turn }: { turn: number }) {
  const ticks = Array.from({ length: 72 }, (_, i) => i);
  return (
    <svg className="rings" viewBox="-500 -500 1000 1000" aria-hidden="true" focusable="false">
      <g className="rings-static">
        <circle r={470} className="ring thin" />
        <circle r={430} className="ring" />
        <circle r={300} className="ring thin dashed" />
        <path d="M -470 0 L -380 0 M 380 0 L 470 0 M 0 -470 L 0 -380 M 0 380 L 0 470" className="ring" />
      </g>
      <g className="rings-turn" style={{ transform: `rotate(${turn}deg)` }}>
        {ticks.map((i) => (
          <line
            key={i}
            x1={0}
            y1={-452}
            x2={0}
            y2={i % 6 === 0 ? -408 : -440}
            className={i % 6 === 0 ? "tick major" : "tick"}
            transform={`rotate(${i * 5})`}
          />
        ))}
        <path d="M -140 -380 A 405 405 0 0 1 140 -380" className="ring arc-accent" />
      </g>
    </svg>
  );
}

// "ONLINE" / "OFFLINE" set along an arc, as on the reference panels.
export function OnlineArc({ online }: { online: boolean }) {
  return (
    <svg className={`online-arc ${online ? "on" : "off"}`} viewBox="0 0 140 44" role="img" aria-label={online ? "API online" : "API offline"}>
      <defs>
        <path id="online-arc-path" d="M 8 40 Q 70 -6 132 40" />
      </defs>
      <text>
        <textPath href="#online-arc-path" startOffset="50%" textAnchor="middle">
          {online ? "ONLINE" : "OFFLINE"}
        </textPath>
      </text>
    </svg>
  );
}

// Yellow/black hazard-striped tag. Shown only when a module has something
// that needs attention (API down, no database, an errored job, a Eureka).
export function Caution({ title = "CAUTION!", children, seed }: { title?: string; children: ReactNode; seed: string }) {
  return (
    <aside className="caution" role="note">
      <div className="caution-card">
        <div className="caution-title">{title}</div>
        <div className="caution-body">{children}</div>
        <div className="caution-foot">
          <Barcode seed={`caution:${seed}`} bars={28} />
          <span className="caution-file">DATA FILE</span>
          <Glyph seed={`caution:${seed}`} size={7} />
        </div>
      </div>
    </aside>
  );
}
