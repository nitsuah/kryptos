# Dashboard

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

_Last updated: 2026-09-30_

The dashboard is a single-page React app (`frontend/`) over the FastAPI backend, styled after the user interfaces in
*Ghost in the Shell*. It is one fixed-height screen: five modules on a ring, each laid out to fit the viewport, with no
page scrolling. It replaced a five-tab SPA and the unbuilt "Akira" CRT spec (`docs/archive/K4-v2.md`).

Build, run and deploy instructions: [`frontend/README.md`](../../frontend/README.md).

---

## Layout

```text
┌ HUD ─────────────────────────────────────────────────────────────────────────┐
│ (ring dial) KRYPTOS        PROTECTICON ▌▌▌▌ ▌▌▌ SECTION K4     ONLINE  UTC  ◐ │
├ stage ───────────────────────────────────────────────────────────────────────┤
│  preview  ┌ B.001 ─ KRYPTOS · K4  LEVEL-1 ──────────── ▌▌▌▌ ▮▮▮▮ ▦ ┐  preview │
│  (Sys)    │ K4                                                     │  (Ledger)│
│           │ ┌ screen (white, lavender frame) ───────────┐ ┌CAUTION┐│          │
│           │ │ panels laid out to fit; lists scroll       │ │only if ││          │
│           │ │ inside their own panel                     │ │needed  ││          │
│           │ └────────────────────────────────────────────┘ └───────┘│          │
│           └──────────────────────────────────────────────────────────┘          │
├ dock ────────────────────────────────────────────────────────────────────────┤
│                 K4     LG     AT     LB     SY          ← → or swipe          │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **HUD.** A ring dial whose ticks are the modules, the brand, a decorative barcode strip, an `ONLINE`/`OFFLINE` arc
  driven by `/api/status`, a UTC clock, and a theme switch (system → light → dark).
- **Stage.** The active module faces you; its two neighbours are tilted previews at the sides that show a few live
  numbers and open on click. Background rings turn with the carousel.
- **Module header.** Code, title, one-line description, and on the right a barcode, the ledger meters (share of
  families per tier, the only decoration that carries data) and a glyph block.
- **Dock.** One tick per module. A yellow/black dot marks a module with a CAUTION.

Switching modules: dock, ring dial, side previews, `←`/`→` (or `[`/`]`) when focus isn't inside the module, or a
horizontal swipe. The
active module is in the URL hash (`#ledger`). Links from the earlier nine-module layout redirect: `#overview` → K4,
`#jobs` → Attacks, `#decoder`/`#vault` → Lab, `#runs`/`#console` → System.

## Modules

| Code | Module | Panels | Reads |
|------|--------|--------|-------|
| K4 | K4 | Ciphertext matrix with the four cribs (tap a letter for position and plaintext) · ledger gauge · what's still open · the Weltzeituhr | `/api/k4/ledger` |
| LG | Ledger | Tier filters, search and the family list · the selected family's scope, evidence, module and test | `/api/k4/ledger` |
| AT | Attacks | P1–P22 list · the selected vector with its run controls and live progress · recent jobs | `/api/k4/attacks/frontier`, `POST /api/k4/attacks/run`, `/api/k4/attacks/jobs[/{id}]` |
| LB | Lab | K1–K3 decoder, animated · one tool at a time: ad-hoc decrypt, seal, unseal, check a vault token | `POST /api/decrypt`, `/api/vault/*` |
| SY | System | API and database with every table's row count · live log · run history · the Physical/Geometric Pivot | `/api/status`, `/api/stream/logs`, `/api/runs`, `/api/candidates`, `/api/k4/attacks/pivot-status` |

Modules are registered in `frontend/src/modules/registry.tsx`: id, code, title, blurb, component, a `preview` function
(numbers on a side face) and an optional `alert` function.

### The Weltzeituhr

Sanborn said in 2025 that BERLIN CLOCK in K4 means the Weltzeituhr (Urania World Clock) at Alexanderplatz, not the
Mengenlehreuhr, so the K4 module draws that clock (`frontend/src/components/WorldClock.tsx`):

- **Topper.** The solar-system sculpture, turning once a minute as the real one does.
- **Drum.** 24 panels, one per hour zone, in perspective. Each shows its UTC offset and the engraved city names in the
  clock's own spellings (KIEW, PRESSBURG, PJÖNGJANG…). Berlin's panel is outlined in orange. Panels with no plates
  read yet say so.
- **Hour ring.** Each panel's current standard time, updated live.
- **Wind rose.** The mosaic the clock stands on.

The drum starts on Berlin and turns with the ◀ ▶ buttons or by clicking a panel.

The names come from `src/kryptos/k4/world_clock_cities.py` (130 of 146 plates read from photographs). They are grouped
here by each city's standard UTC offset. The real drum's plate-to-panel layout is only partly recorded, so the grouping
is an approximation, not a transcription. Photographing the whole ring (TASKS, Phase 8) would fix it.

### When the CAUTION tag appears

| Module | Condition |
|--------|-----------|
| K4 | `/api/status` failed (API unreachable) |
| Attacks | A recent job has status `eureka`, or ended in `error` |
| System | The server has no `DATABASE_URL` (run history, job persistence and the vault are off) |

## Fitting the screen

- The shell is `100dvh`. Header, stage and dock are fixed rows, and the page never scrolls.
- Each module is a CSS grid of panels sized with `minmax(0, 1fr)`. Only lists and tables scroll: ledger families,
  attack vectors, jobs, table rows and the log, each inside its own panel.
- **Screens under 820 px tall** (laptops): the module description, the header decoration and the dock titles are
  hidden, and the gauges shrink.
- **Under 720 px wide, or under 560 px tall:** panels stack in one column and the module's screen scrolls. There is no
  way to fit a whole module on a phone. Side previews, arrows and header decoration are hidden, and swipe or the dock
  switches modules.
- **720–1099 px wide:** the K4 module moves to two columns (ciphertext on top, ledger and open fronts beside the clock).

Checked at 1600×950, 1280×760 and 1024×768: no page scroll and no screen overflow in any module.

Only the active module mounts its component, so its requests (pivot status, run history, the log stream) run only
while it is on screen. `frontend/src/shell/data.tsx` polls `/api/status` every 10 s, the ledger every 60 s, and jobs
every 20 s, or every 3 s while one is running. Polling pauses while the tab is hidden.

## Visual language

| Element | Light | Dark |
|---------|-------|------|
| Chassis | paper `#f5f3fb` | near-black `#0d0c12` |
| Screens and panels | white, lavender frame | `#121019` / `#17151f`, violet frame |
| Linework | lavender `#ad9de4` | violet `#6353a6` |
| Labels and panel titles | orange `#c96f00` | orange `#ff9d2e` |
| ONLINE | green `#1f9d4b` | green `#3ed27a` |
| CAUTION | yellow `#f2c200` and black stripes, white card | same |
| Tiers | green / blue / amber / pink, darker shades on white | brighter shades |

Type: Barlow Condensed for labels and titles, Share Tech Mono for data (Google Fonts, with system fallbacks). Buttons
are black-outlined and turn orange on hover.

## Accessibility

- The stage is a carousel region (`aria-roledescription`), each face a labelled slide. The two side previews are
  buttons ("Open Ledger"); faces further round render nothing and are `aria-hidden`. A polite live region announces
  the active module.
- The ring dial in the header is a pointer shortcut only (hidden from assistive technology); the dock is the
  keyboard-accessible control.
- Keyboard: `←`/`→` switch modules unless focus is in a form field or anywhere inside the module's screen (lists,
  buttons, the cipher matrix), so the module in use is never unmounted by an arrow key; everything else is reachable
  with Tab.
- Tier and status colours always come with a text label. `prefers-reduced-motion` stops the carousel, dial, gauge and
  clock-topper animation.
