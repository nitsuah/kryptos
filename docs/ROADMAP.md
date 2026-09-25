# Kryptos Roadmap

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · **Roadmap** · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

Last Updated: 2026-09-24
Next Review: 2026-10-24

> 2027 planning reset (2026-09-24): completed Phases 1–4, 6 and 7 (all null — every code-executable direction
> identified so far) and Phase 8's two closed leads were moved verbatim to
> [archive/2026-completed-roadmap-and-tasks.md](./archive/2026-completed-roadmap-and-tasks.md) and summarized in
> [FEATURES](./FEATURES.md). What remains open is carried into 2027 Q1 below.

---

## Current Status

**K4 attack phase:** Phases 6 and 7 (Physical/Geometric Pivot, then the shape-changing transpose family + shadow-angle primitives + city-list keywords + cross-vector consensus scoring) are both complete — every code-executable direction identified so far, including the shape-changing transpose family and both readings of the "shadow of the word" hypothesis, has been implemented, executed against real K4, and returned null. Phase 8 (active) is sourcing three primary-source gaps that no further code can close on its own — see below.

**Architecture:** Confirmed substitution → transposition → K4. The substitution key is not derivable from any standard Berlin Clock row value (shifts at EAST/NORTHEAST reach 17, 20, 25 — exceeding the maximum clock row output of 11). The transposition is not a standard rectangular grid in any simple reading order, including both the shape-preserving and shape-changing 24-column geometric families. At minimum one un-parameterized step remains — the most concrete remaining candidate is a genuinely physical fact this repo cannot fully source on its own: the Kryptos compass rose's exact bearing, still unmeasured by anyone as far as any source checked shows. (The World Clock city list, the other primary-source gap this line used to cite, closed 2026-09-02 at 130 of 146 names — see Phase 8.) A precisely-timed historical moment was found 2026-09-02 (see Phase 8).

---

## 2027 Q1 — Phase 8: Primary-Source Sourcing (Active — opened 2026-09-01)

Everything code-derivable from current sourcing has been tried (Phases 1–7, all null). What's left needs new source material, not new code. Of the three gaps opened 2026-09-01, two closed 2026-09-02 (World Clock city list at 130/146; sub-minute Nov 9 1989 timestamp). One remains:

- [ ] **The Kryptos compass rose's actual measured bearing.** Confirmed via `elonka.com`'s own wishlist to be a still-open *community-wide* question, not just a gap in this repo. One uncertain secondary estimate exists (~220°, explicitly flagged inexact). 2026-09-02: satellite imagery of the CIA courtyard was inspected directly (Google Maps, unblurred) and ruled out — resolution is building/lot-scale, not fine enough for a ground-level stone engraving. Remaining leads: a CIA FOIA/public-affairs request, or contacting Elonka Dunin directly. Outreach drafts for both (the questions to ask Elonka, and the FOIA request text) are ready — see `docs/TASKS.md`.
- [ ] **Send the three outreach drafts** — FOIA request (foia.cia.gov, asking for the 1990 landscape/installation drawing), Elonka Dunin, and CIA Public Affairs (authorized research visit). All three are drafted in `docs/TASKS.md`; each needs a human send.

If none of these surface, this is genuinely paused — inventing more sweep variants over the same structural assumptions (grids, reflections, rotations, clock states) is not expected to move this forward (see Phase 7's zero cross-vector consensus result).

**External developments (2025–2026):** Sanborn's 1990 archival papers were found by independent researchers (Sept 2025, not a cryptographic solve); a Sanborn-confirmed K5 exists; a third-party reconstruction (solvekryptos.com) aligns with all four confirmed crib anchors after this repo's own `K4_CRIBS` off-by-one bug was fixed. Its mechanism is not published in enough detail to reproduce. The recovered opening line, "THE COMPASS ROSE IS HERE," is independent support for the compass-rose lead. Follow-up rounds 1–3 (2026-09-03) were all null. Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External Developments" sections.

---

## Standing — Phase 5: Post-Solution (conditional on a solve)

- [ ] Solution documentation — full attack path, key insights, solution narrative
- [ ] README update — reflect solution and cryptanalytic implications
- [ ] Archive all null-result artifacts with parameter provenance

---

## Key References

| Document | Purpose |
|----------|---------|
| `docs/archive/K4_ATTACK_LANDSCAPE.md` | Archived — full 3D fingerprint with evidence basis, historical reference only |
| `docs/analysis/K4_ACTIVE_RESEARCH.md` | Living null-result log and confirmed facts |
| `docs/analysis/K4_CAPABILITY_TABLE.md` | Every attack vector/component, status, real candidate count — one scannable table |
| `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` | Derived shift sequences at all 4 crib windows |
| `docs/TASKS.md` | Implementation backlog with specific next steps |
| `frontend/` + Docker | `docker compose -f config/docker-compose.yml up -d` → http://localhost:8000 |
| `docs/archive/2026-completed-roadmap-and-tasks.md` | Verbatim archive of completed Phases 1–4/6/7 and TASKS Done (2026-09-24 reset) |
