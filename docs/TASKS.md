# Tasks

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · **Tasks** · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

Last Updated: 2026-09-28

---

## In Progress

- _None yet._

## Todo

One of the three primary-source gaps opened 2026-09-01 remains open; the timestamp one closed 2026-09-02, and the World Clock *segment*-sourcing gap (the ~4 of 24 segments with no legible photo) closed 2026-09-02 too — not the complete 146-name city list itself, which stands at 130/146 confirmed (see the [2026 archive](./archive/2026-completed-roadmap-and-tasks.md)). See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed" and "External Developments (2025–2026)" sections for full detail and sourcing rationale. Action items below are split by who actually has to do them — Claude's automatable queue vs. the send that genuinely needs a human.

### Primary-source sourcing (opened 2026-09-01) — 2027 Q1

- [ ] **Source the Kryptos compass rose's actual measured bearing** — per `elonka.com/kryptos/wishlist.html`, this is a still-open community question, not just gapped in this repo. `elonka.com/kryptos/KryptosAerial.html` already has one uncertain secondary estimate (~220°, explicitly flagged "not exact"). 2026-09-02 update: satellite/overhead imagery of the CIA New Headquarters Building courtyard was inspected directly (Google Maps, unblurred) — confirmed insufficient resolution for ground-level engraving detail (building/lot-scale only), ruling out that specific lead; the underlying reason is resolution physics, not a one-off check — resolving a thin engraved line on a ~1m stone to a useful few degrees needs sub-centimeter, near-nadir imagery of that one feature, and no public satellite/aerial/lidar source gets close (best commercial imagery is ~15-30cm/px). A physical on-site GPS/compass measurement isn't a viable alternative either: the courtyard is inside the CIA's secured grounds, not publicly accessible, and a consumer phone compass is only accurate to roughly ±5-10° regardless. External-plaintext note: solvekryptos.com's *reconstructed* plaintext opens "THE COMPASS ROSE IS HERE". That reconstruction is not Sanborn's archival text (Kobek and Byrne haven't released it), so this is consistent with the lead but doesn't confirm it (corrected 2026-09-27). Also, the Weltzeituhr that Sanborn says BERLIN CLOCK refers to stands on its own compass-rose mosaic, so any "compass rose" in the plaintext may not mean the CIA courtyard stone. **[You — the only send]** A FOIA request to CIA (foia.cia.gov) or contacting Elonka Dunin directly (active community liaison to Sanborn/CIA contacts) — both drafted in full below (moved here 2026-09-28 from the retired "Three Open Leads" briefing page). The FOIA draft specifically asks for the original 1990 landscape/installation architectural drawing (which may already have the bearing annotated), not just a photo — a drawing is far more likely to exist and to actually answer the question than commissioning new imagery.
  - Priority: P3
  - Type: Research
  - Draft for Elonka Dunin (email `elonka.codebreaking@gmail.com`; the address listed on her site is the fallback):
    > Subject: One long-shot Kryptos K4 question — the compass rose's bearing
    >
    > Hi Elonka,
    >
    > I've been running an automated attack sweep against K4 (every geometric and keyed-alphabet variant I can generate, all null so far). One physical fact about the site would let me close out the last untested branch, and I can't find it published anywhere, including your own wishlist:
    >
    > Has anyone ever actually measured the compass rose stone's bearing in the CIA courtyard? Your KryptosAerial page flags the ~220 degree figure as inexact. Do you know of a more precise reading, a survey, or an overhead photo detailed enough to measure it myself?
    >
    > No rush; it would close a loop, not open a new one. Thanks for keeping the wishlist alive all these years.
    >
    > [Your name]
  - Draft FOIA request (foia.cia.gov/foia_request/form, or by mail to Information and Privacy Coordinator, Central Intelligence Agency, Washington, DC 20505):
    > Re: Records request — compass-rose bearing, Kryptos sculpture courtyard, CIA New Headquarters Building, Langley, VA
    >
    > Under the Freedom of Information Act, I am requesting copies of any of the following records, if they exist:
    >
    > 1. A survey, blueprint, or as-built drawing showing the compass orientation of the compass-rose paving stone installed near the Kryptos sculpture.
    > 2. A high-resolution overhead or ground-level photograph of that stone sufficient to measure its bearing.
    > 3. Any correspondence describing the stone's intended orientation from the sculpture's 1990 installation records.
    >
    > I am willing to pay reasonable fees up to $[amount]. Please contact me first if fees are expected to exceed this.
    >
    > [Your name, mailing address, phone or email]
- [ ] **Ask CIA Public Affairs whether an authorized research visit exists** — 2026-09-03, checked directly against CIA's own FAQ (`cia.gov/faqs`): public tours are refused ("Security considerations prevent such tours"), but "CIA provides an extremely limited number of visits annually for approved academic and civic groups." Not a gate loophole, not "can I sneak in" — a narrow, honest question to the Office of Public Affairs (CIA's own named public-facing contact point, `cia.gov/about/organization/public-affairs`) about whether an independent researcher studying the publicly documented Kryptos puzzle can be included in an approved visit, or otherwise get authorized escorted access for non-sensitive observation/measurement. **[You — the only send.]** Draft:
  > Subject: Research inquiry — authorized visit access for Kryptos sculpture research
  >
  > Hello,
  >
  > I'm an independent researcher studying the publicly documented Kryptos sculpture at CIA Headquarters — specifically the still-unsolved K4 passage, which is public information CIA itself has written about. I understand Headquarters doesn't offer public tours, but I've read that a limited number of visits happen each year for approved academic and civic groups.
  >
  > Is there an existing mechanism for an independent researcher to be included in one of those visits, or to otherwise request brief, escorted, non-sensitive access to observe and measure the Kryptos sculpture's compass rose for research purposes? Happy to provide more detail on the specific research question if useful.
  >
  > Thank you for your time.
  >
  > [Your name and contact information]
  - Priority: P3
  - Type: Research

### Cryptanalysis (opened 2026-09-27)

- [x] **Scope the "non-periodic key, no transposition" family** — done 2026-09-28 as the P21 crib-constraint engine (`kryptos.k4.crib_constraints`): autokey, linear, progressive, digit and running keys over the sculpture corpus are eliminated over the ranges in `docs/analysis/K4_NEGATIVE_SPACE.md`. Per-position clock/bearing procedures remain open, and depend on the compass-rose bearing.
  - Priority: P3
  - Type: Research + code
- [ ] **Load a real scoring word list** — `data/wordlist.txt` has never existed, so `scoring.wordlist_hit_rate` has always used an 18-word fallback. Load `english-words` (now a dependency) as the fallback, then re-baseline scoring on K1–K3 and synthetic texts before trusting new sweep scores. Expect score changes in tests that pin values.
  - Priority: P2
  - Type: Code + calibration
- [ ] **Quagmire IV and double-periodic keys as constraint checks** — extend `crib_constraints` to two-keyword Quagmire IV (prune dictionary pairs with the per-side Q1/Q2 constraints) and to sums of two periodic keys (e.g. PALIMPSEST + ABSCISSA). See `K4_NEGATIVE_SPACE.md` open items 2–3.
  - Priority: P3
  - Type: Code
- [ ] **K3-style double rotation and transposition + non-periodic key as constraint checks** — open items 4–5 in `K4_NEGATIVE_SPACE.md`.
  - Priority: P3
  - Type: Code

---

## Done

_Completed tasks were moved verbatim to [archive/2026-completed-roadmap-and-tasks.md](./archive/2026-completed-roadmap-and-tasks.md)
in the 2027 planning reset (2026-09-24) and summarized in [FEATURES](./FEATURES.md); per-vector results live in
`docs/analysis/K4_ACTIVE_RESEARCH.md` / `K4_CAPABILITY_TABLE.md`._
