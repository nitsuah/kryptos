# Tasks

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · **Tasks** · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

Last Updated: 2026-09-30

---

## In Progress

- _None._

## Todo

Two queues: code that can be built here (Phase 9 and platform), and sourcing that needs a person (Phase 8). The ranked
rationale for the code items is in [`docs/analysis/K4_NEGATIVE_SPACE.md`](./analysis/K4_NEGATIVE_SPACE.md#open-ranked).

### Cryptanalysis frontier — code (Phase 9)

Each item needs exact search or shuffled-ciphertext controls, a positive-control test, and a ledger entry with the
right tier (see `docs/GOVERN.md`).

- [ ] **Irregular transpositions + periodic key** — Myszkowski, disrupted/incomplete columnar, keyed route ciphers and turning grilles, both layer orders. Extend `frontier_checks._columnar_backtrack` to keyed variants.
  - Priority: P2
  - Type: Code
- [ ] **Length-changing masking** — letters inserted or dropped inside words, the way K1–K3 carry misspellings. Build a crib alignment that allows gaps and test it against shuffled controls.
  - Priority: P2
  - Type: Code
- [ ] **Two non-periodic layers** — autokey or running key on top of a wide or irregular transposition. Today columnar + autokey stops at width 7 and columnar + English running key at width 8.
  - Priority: P3
  - Type: Code
- [ ] **Named running-key sources under transposition** — the K1–K3 ciphertexts, the K0 Morse text and the Cyrillic Projector as running keys after a columnar or geometric transposition.
  - Priority: P3
  - Type: Code
- [ ] **Hill 6×6+ with partial blocks** — combine with a transposition hypothesis or use partial crib blocks.
  - Priority: P4
  - Type: Code
- [ ] **Per-letter Weltzeituhr lookup keys** — blocked on the photographs below.
  - Priority: P3
  - Type: Code (blocked)

### Platform

- [ ] **"Try a hypothesis" endpoint** — `POST /api/k4/hypothesis` taking a family and parameters and returning the crib verdict and a decryption; a dashboard module on top.
  - Priority: P3
  - Type: Code
- [ ] **Candidate submission gate** — before any $1 Paradigm guess, run every crib and ledger check and require the candidate to reproduce from its stated method. Also needs a written policy from the owner.
  - Priority: P3
  - Type: Code + policy
- [ ] **Re-score stored candidates** — anything in `candidates` ranked before 2026-09-28 used the placeholder n-gram tables.
  - Priority: P4
  - Type: Code

### Primary-source sourcing — needs you (Phase 8)

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
- [ ] **Photograph the Weltzeituhr** — close-ups of every face of the city ring (16 of 146 city plates are still unread; `kryptos.k4.world_clock_cities`), the International Date Line plate, and the wind-rose mosaic from above with a straight edge in frame so its orientation can be measured. This is the only input that blocks the per-letter lookup keys in Phase 9 (a city, time zone or hour per letter). Anyone in Berlin with a phone can do it in about 30 minutes; Wikimedia Commons photos already cover most plates but not the ring order or the mosaic orientation.
  - Priority: P2
  - Type: Research (physical)
- [ ] **Check Sanborn's quotes against the primary pages** — `docs/sources/SANBORN_QUOTES.md` gives each quote a confidence tier; several source pages blocked automated fetches. A manual read of those pages would firm up the "masking" and "not a math solution" statements the open fronts lean on.
  - Priority: P4
  - Type: Research

---

## Done

- **2026-09-30 — Single-page dashboard.** Tabs replaced by one fixed-height screen: five modules (K4, Ledger, Attacks, Lab, System) on a ring, each fitting the viewport without page scrolling; a drawing of the Weltzeituhr replaces the Mengenlehreuhr lamp clock; paper-and-lavender styling instead of teal screens; ledger and job history now have UI (`docs/reference/DASHBOARD.md`).
- **2026-09-30 — Docs pass.** README rewritten around where K4 stands; ROADMAP, TASKS, INDEX, FEATURES, METRICS, GOVERN and the analysis docs brought up to date; the unbuilt Akira spec archived.
- **2026-09-28 — Frontier checks (P22)** in `kryptos.k4.frontier_checks`: recurrence keys, periodic key + arbitrary mixed alphabet, dial keys, bearing routes and Hill 4×4 eliminated; wide columnar widths 10–14 by exact search; running keys from any English text and Hill 5×5 statistical; the full-plaintext reconstruction fits no tested family.
- **2026-09-28 — Main scorer on real n-gram tables.** `scoring` loads `data/ngrams/english_{2,3,4}grams.tsv` (the old tables held about ten entries each). English vs shuffled English on 97 letters: Cohen's d 4.2 → 9.4, overlap 30/300 → 0 (`test_k4_ngram_calibration.py`). Score thresholds that depended on the old scale were recalibrated: the pipeline's partial-score pruning floor (-560 over 40 letters), the hypothesis pruning floor (-420 over 30 letters), and the composite Eureka snapshot floor (-1300; the old 80 could never be reached). `EurekaSignal` itself is crib-based and unchanged. Stored top candidates from earlier sweeps were ranked with the old tables.
- **2026-09-28 — Crib-constraint engine (P21)** in `kryptos.k4.crib_constraints`: autokey, linear, progressive, digit and sculpture-corpus running keys; dictionary Quagmire I–III (231,933 alphabets); columnar (2–9) and geometric transposition × periodic key.
- **2026-09-28 — Structural checks** in `kryptos.k4.structural_checks`: double periodic keys (p1 + p2 ≤ 24), Quagmire IV (vocabulary × dictionary and dictionary × dictionary), K3-style double rotation, columnar + autokey/running key, nulls, Hill 2×2/3×3, output-alphabet eliminations, Chaocipher (sampled), error-tolerant scans against 15 shuffled controls.
- **2026-09-28 — Real scoring word list**: 261k words (`english-words`), English/random separation 1.55 → 1.91.
- **2026-09-28 — Persistence**: crib-constraint runs in `k4_constraint_runs`, attack jobs in `k4_attack_jobs`.

_Earlier completed tasks were moved verbatim to [archive/2026-completed-roadmap-and-tasks.md](./archive/2026-completed-roadmap-and-tasks.md)
in the 2027 planning reset (2026-09-24) and summarized in [FEATURES](./FEATURES.md); per-vector results live in
`docs/analysis/K4_ACTIVE_RESEARCH.md` / `K4_CAPABILITY_TABLE.md`._
