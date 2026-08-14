/**
 * Berlin Clock (Mengenlehreuhr) — live SVG visualization.
 *
 * Rows (top → bottom):
 *   0 — Seconds:     1 lamp, blinks every 2s (ON = even second)
 *   1 — 5-hr lamps:  4 lamps, each = 5 hours (RED when lit)
 *   2 — 1-hr lamps:  4 lamps, each = 1 hour  (RED when lit)
 *   3 — 5-min lamps: 11 lamps, each = 5 min  (YELLOW; 3rd/6th/9th = RED = quarter-hour)
 *   4 — 1-min lamps: 4 lamps, each = 1 min   (YELLOW when lit)
 */
import { useState, useEffect } from "react";

interface ClockState {
  seconds: boolean;        // even = ON
  h5: boolean[];           // 4 lamps
  h1: boolean[];           // 4 lamps
  m5: boolean[];           // 11 lamps
  m1: boolean[];           // 4 lamps
  timeStr: string;
}

function computeClockState(d: Date): ClockState {
  const h = d.getHours();
  const m = d.getMinutes();
  const s = d.getSeconds();
  return {
    seconds: s % 2 === 0,
    h5: Array.from({ length: 4 }, (_, i) => i < Math.floor(h / 5)),
    h1: Array.from({ length: 4 }, (_, i) => i < h % 5),
    m5: Array.from({ length: 11 }, (_, i) => i < Math.floor(m / 5)),
    m1: Array.from({ length: 4 }, (_, i) => i < m % 5),
    timeStr: `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`,
  };
}

/** Pass a static state (e.g. CIA timestamp) to freeze the clock display. */
interface Props {
  staticTime?: string;  // "HH:MM:SS" — if set, shows this time frozen
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

export default function BerlinClock({ staticTime, size = "md", showLabel = true }: Props) {
  const [state, setState] = useState<ClockState>(() => {
    if (staticTime) {
      const [h, m, s] = staticTime.split(":").map(Number);
      const d = new Date();
      d.setHours(h ?? 0, m ?? 0, s ?? 0);
      return computeClockState(d);
    }
    return computeClockState(new Date());
  });

  useEffect(() => {
    if (staticTime) return;
    const id = setInterval(() => setState(computeClockState(new Date())), 500);
    return () => clearInterval(id);
  }, [staticTime]);

  const W = size === "sm" ? 160 : size === "lg" ? 300 : 220;
  const H = Math.round(W * 0.75);
  const pad = W * 0.04;
  const lampW = (W - pad * 2) / 11 - 2;
  const lampH = H * 0.12;
  const rowGap = H * 0.18;
  const r = lampW * 0.35;

  const RED   = "#e74c3c";
  const YELLOW = "#f1c40f";
  const OFF    = "rgba(29,158,117,0.10)";
  const GLOW_RED    = `drop-shadow(0 0 ${r * 0.8}px ${RED})`;
  const GLOW_YELLOW = `drop-shadow(0 0 ${r * 0.8}px ${YELLOW})`;

  function Lamp({ x, y, on, color }: { x: number; y: number; on: boolean; color: string }) {
    return (
      <rect
        x={x} y={y}
        width={lampW} height={lampH}
        rx={r} ry={r}
        fill={on ? color : OFF}
        stroke={on ? color : "rgba(29,158,117,0.2)"}
        strokeWidth={0.5}
        style={{ filter: on ? (color === RED ? GLOW_RED : GLOW_YELLOW) : undefined, transition: "fill 0.15s" }}
      />
    );
  }

  function Row({ lamps, colors, y, count }: { lamps: boolean[]; colors: string[]; y: number; count: number }) {
    const totalW = W - pad * 2;
    const step = totalW / count;
    return (
      <>
        {Array.from({ length: count }, (_, i) => (
          <Lamp
            key={i}
            x={pad + i * step + (step - lampW) / 2}
            y={y}
            on={lamps[i]}
            color={colors[i]}
          />
        ))}
      </>
    );
  }

  const secRadius = lampW * 1.4;
  const secX = W / 2;
  const secY = pad + secRadius;
  const y1 = secY + secRadius + rowGap * 0.3;
  const y2 = y1 + lampH + rowGap * 0.4;
  const y3 = y2 + lampH + rowGap * 0.4;
  const y4 = y3 + lampH + rowGap * 0.4;

  const m5Colors = Array.from({ length: 11 }, (_, i) =>
    (i + 1) % 3 === 0 ? RED : YELLOW
  );

  return (
    <div style={{ display: "inline-block" }}>
      <svg width={W} height={H + pad} viewBox={`0 0 ${W} ${H + pad}`} xmlns="http://www.w3.org/2000/svg">
        {/* Background */}
        <rect width={W} height={H + pad} rx={6} fill="rgba(4,52,44,0.6)" stroke="rgba(29,158,117,0.3)" strokeWidth={0.5} />

        {/* Seconds lamp — circle */}
        <circle
          cx={secX} cy={secY} r={secRadius}
          fill={state.seconds ? YELLOW : OFF}
          stroke={state.seconds ? YELLOW : "rgba(29,158,117,0.2)"}
          strokeWidth={0.5}
          style={{ filter: state.seconds ? GLOW_YELLOW : undefined, transition: "fill 0.1s" }}
        />

        {/* 5-hour row */}
        <Row lamps={state.h5} colors={[RED, RED, RED, RED]} y={y1} count={4} />

        {/* 1-hour row */}
        <Row lamps={state.h1} colors={[RED, RED, RED, RED]} y={y2} count={4} />

        {/* 5-minute row */}
        <Row lamps={state.m5} colors={m5Colors} y={y3} count={11} />

        {/* 1-minute row */}
        <Row lamps={state.m1} colors={[YELLOW, YELLOW, YELLOW, YELLOW]} y={y4} count={4} />
      </svg>
      {showLabel && (
        <div style={{ textAlign: "center", fontSize: size === "sm" ? "10px" : "12px", color: "var(--accent)", letterSpacing: "2px", marginTop: "4px", fontFamily: "var(--mono)" }}>
          {staticTime ?? state.timeStr}
          {staticTime && <span style={{ color: "var(--warning)", marginLeft: "6px", fontSize: "10px" }}>FROZEN</span>}
        </div>
      )}
    </div>
  );
}
