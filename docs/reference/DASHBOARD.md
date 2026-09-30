# Dashboard

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

_Last updated: 2026-09-30_

The dashboard is a single-page React app (`frontend/`) over the FastAPI backend. Since 2026-09-30 it is one screen
with no tabs, styled after the user interfaces in *Ghost in the Shell*. It replaced a five-tab SPA (Ops Center,
Decode, Database, Vault, K4 Dashboard) and the unbuilt "Akira" CRT spec (`docs/archive/K4-v2.md`).

Build, run and deploy instructions: [`frontend/README.md`](../../frontend/README.md).

---

## Layout

```text
┌ HUD ─────────────────────────────────────────────────────────────────────────┐
│ (ring dial) KRYPTOS        PROTECTICON ▌▌▌▌ ▌▌▌ SECTION K4     ONLINE  UTC  ◐ │
├ stage ───────────────────────────────────────────────────────────────────────┤
│   ╱ prev ╲   ┌ B.002 ─ KRYPTOS · LG  LEVEL-2 ─────────────── ▌▌▌▌▌ ┐   ╱ next ╲ │
│  │preview│   │ LEDGER                                            │  │preview│ │
│  │ (teal)│   │ ┌ screen (teal, scrolls) ─────────────┐ ┌CAUTION!┐│  │ (teal)│ │
│   ╲     ╱    │ │ module content                      │ │ only if ││   ╲     ╱  │
│              │ └─────────────────────────────────────┘ │ needed  ││             │
│              │ ▮▮▮ ▮▮ ▮ ▮  (ledger meters)      ▦ 0180…  └────────┘│             │
│              └─────────────────────────────────────────────────────┘             │
├ dock ────────────────────────────────────────────────────────────────────────┤
│        OV   LG   AT   JB   RN   CN   DC   VT   SY          ← → or swipe       │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **HUD.** A ring dial whose ticks are the modules (the active one is orange and at the top), the brand, a decorative
  barcode strip, an `ONLINE`/`OFFLINE` arc driven by `/api/status`, a UTC clock, and a theme switch (system → light →
  dark).
- **Stage.** The modules sit on a ring. The active one faces you; the two neighbours are tilted previews at the sides
  that show a few live numbers and open on click. Background rings turn with the carousel.
- **Dock.** One tick per module with its two-letter code. A yellow/black dot marks a module that has a CAUTION.

Switching modules: dock, ring dial, side previews, `←`/`→` (or `[`/`]`) when not typing, or a horizontal swipe. The
active module is kept in the URL hash (`#ledger`), so views can be linked and the back button works.

## Modules

| Code | Module | Shows | Reads |
|------|--------|-------|-------|
| OV | Overview | K4's 97 letters with the four cribs (tap a letter for its position and plaintext), ledger totals, open fronts, clocks (Mengenlehreuhr, UTC, Berlin, Langley) | `/api/k4/ledger` |
| LG | Ledger | Every hypothesis family by tier, searchable, with scope, evidence, module and test | `/api/k4/ledger` |
| AT | Attacks | The P1–P22 queue grouped by phase; each runnable vector can be launched and followed; the earlier attack-vector registry | `/api/k4/attacks/frontier`, `POST /api/k4/attacks/run`, `/api/k4/attacks/jobs/{id}`, `/api/attack-vectors` |
| JB | Jobs | Recent attack jobs with progress, errors, near-miss candidates and summaries | `/api/k4/attacks/jobs` |
| RN | Runs | Campaign run history and candidates (needs `DATABASE_URL`) | `/api/runs`, `/api/runs/{id}/candidates`, `/api/candidates` |
| CN | Console | Ad-hoc decrypt for K1–K4 and the live backend log | `POST /api/decrypt`, `/api/stream/logs` (SSE) |
| DC | Decoder | How K1–K3 were enciphered, animated step by step, checked against the backend | `POST /api/decrypt` |
| VT | Vault | Seal a secret under a keyed Vigenère, unseal once, check a token (needs `DATABASE_URL`) | `/api/vault/*` |
| SY | System | API and database state, every Neon table with its row count, the Physical/Geometric Pivot graph and bearings | `/api/status`, `/api/k4/attacks/pivot-status` |

Modules are registered in `frontend/src/modules/registry.tsx`. Each entry has an id, a code, a title, a one-line
blurb, the component, a `preview` function (the numbers shown on a side face), and an optional `alert` function.

### When the CAUTION tag appears

| Module | Condition |
|--------|-----------|
| Overview | `/api/status` failed (API unreachable) |
| Attacks | Any recent job has status `eureka` |
| Jobs | Any recent job ended in `error` |
| Runs, Vault | The server has no `DATABASE_URL` |

Everything else stays quiet, so the tag only appears when something needs a look.

## Keeping it uncluttered

- **One full module at a time.** Only the active module mounts its component, so its own requests (runs, pivot status,
  the log stream) run only while it is on screen. Side faces render a preview card, and faces further round render
  nothing.
- **Shared polling.** `frontend/src/shell/data.tsx` polls `/api/status` every 10 s, the ledger every 60 s, and jobs
  every 20 s, or every 3 s while a job is running. Polling pauses while the tab is hidden. The ledger refreshes when a
  job finishes.
- **Progressive detail.** Ledger entries, attack vectors and jobs are one line each and expand on demand.
- **Decoration carries no data** except the footer meters, which show the ledger's share by tier. Barcodes, glyph blocks
  and serial numbers are generated deterministically from the module id (`shell/deco.tsx`) and are hidden from
  assistive technology.

## Scaling

| Width | Behaviour |
|-------|-----------|
| ≥ 1100 px | Active face about 68% of the width; neighbours visible as tilted teal previews; dock shows every title; the ledger gets a sidebar |
| 720–1099 px | Active face about 90% of the width; neighbours only glimpse in at the edges; dock shows the active title |
| < 720 px | One face at a time, sliding; no side arrows (swipe or dock); frame decoration, footer and HUD barcode hidden; CAUTION becomes a strip above the screen; description lists stack |
| Height < 560 px | Footer and blurb hidden so the screen keeps its height |

Inside a screen, content uses fluid grids (`repeat(auto-fit, minmax(min(100%, 340px), 1fr))`), tables scroll sideways
inside their own wrapper, and the K4 matrix reflows (`auto-fill`, about 2 rem per letter). The page itself never
scrolls horizontally; each screen scrolls vertically on its own.

`prefers-reduced-motion` turns off the carousel, dial and gauge transitions. The layout uses `100dvh` so mobile browser
chrome doesn't hide the dock, and `env(safe-area-inset-bottom)` for devices with a home indicator.

## Visual language

| Element | Light chassis | Dark chassis |
|---------|---------------|--------------|
| Background | pale paper `#f5f3fb` | near-black `#0d0c12` |
| Linework (rings, frames) | lavender `#ad9de4` | violet `#6353a6` |
| Labels | orange `#d97a06` | orange `#ff9d2e` |
| ONLINE | green `#1f9d4b` | green `#3ed27a` |
| CAUTION | yellow `#f2c200` and black stripes, white card | same |
| Screens | teal `#11504d` → `#0a3836`, scanlines | same |

Screens look the same in both themes, so the data keeps one high-contrast palette: text `#d8f7ee`, tiers green
(eliminated), cyan (statistical), amber (sampled null) and pink (open), cribs green, violet, amber and coral.

Type: Barlow Condensed for labels and titles, Share Tech Mono for data (Google Fonts, with system fallbacks).

## Accessibility

- The stage is a carousel region (`aria-roledescription`), each face a labelled slide. The two side previews are
  buttons ("Open Ledger"); faces further round render nothing and are `aria-hidden`. A polite live region announces
  the active module.
- The ring dial in the header is a pointer shortcut only (hidden from assistive technology); the dock is the
  keyboard-accessible control.
- Every control is a real button with a label; the dock marks the active module with `aria-current`.
- Keyboard: `←`/`→` switch modules unless focus is in a form field; everything else is reachable with Tab.
- Tier and status colours always come with a text label.

## Fixed in the redesign

- The old K4 visualizer highlighted EAST and NORTHEAST one position too high (22 and 26 instead of 21 and 25), the same
  off-by-one fixed in `keystream_validator.K4_CRIBS` on 2026-09-02. Crib positions now live in `frontend/src/k4.ts` and
  match the backend.
- The Database page listed five tables; System now lists every table `/api/status` reports.
- The ledger (`/api/k4/ledger`) and job history (`/api/k4/attacks/jobs`) had no UI; they now have modules.
