# Sanborn: Statements on the Record

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

**Last Updated:** 2026-09-28
**Purpose:** One cited list of what Jim Sanborn (and Ed Scheidt) have said publicly about K4, so hypotheses start from the record instead of paraphrase. `SANBORN.md` is the research checklist; this is the evidence it points to.

**Sourcing note.** Compiled 2026-09-28 from web-search results. Direct page fetches from these news sites were blocked in the environment used, so each entry records where it was reported rather than a page quote checked in full. The tiers are **Quote** (verbatim wording, reported by the cited outlet) and **Reported** (paraphrase of what he said). Upgrade an entry to "checked" only after reading the primary page.

---

## On the method

| # | Statement | Tier | Where reported | What it implies for this repo |
|---|-----------|------|----------------|-------------------------------|
| 1 | "Who says it is even a math solution?" | Quote | Wikipedia "Kryptos"; PBS NOVA Q&A | Don't assume a purely algebraic cipher. Masking or physical steps are on the table. |
| 2 | "I was fortunate not to understand mathematics, probably in my ability to make the code." | Quote | Wikipedia "Kryptos" / PBS NOVA | The method is hand-executable by a non-mathematician. |
| 3 | Scheidt and Sanborn worked for months in 1989 and settled on "old-school, artisanal" cryptography; in K4, Scheidt deliberately masked the advantage of frequency analysis. | Reported | Wired (2005), as summarised in search results | Consistent with K4's near-random IC (0.0361). Also a reason to test with error tolerance (`crib_constraints.tolerance_study`). |
| 4 | Sanborn used "five or six techniques" across the sculpture. | Quote | Wired, 2005 (already cited in `K4_ACTIVE_RESEARCH.md`) | Multi-layer, but K1–K3 used one or two each. |
| 5 | Both Sanborn and Scheidt have referred to masking in K4 more than once. | Reported | kryptosfan.wordpress.com summaries; Wikipedia | See the `nulls_between_cribs` ledger entry and the open masking items. |
| 6 | K2's ending was corrected in 2006 to "…X LAYER TWO" (a missing X in the original). | Reported | Wikipedia "Kryptos" | He makes, and later acknowledges, errors. Hence the error-tolerant checks. |

## On the cribs

| # | Statement | Tier | Where reported |
|---|-----------|------|----------------|
| 7 | Letters 64–69 (NYPVTT) decrypt to BERLIN. Nov 2010. | Reported | The New York Times; NBC News; PBS NOVA |
| 8 | Letters 70–74 (MZFPK) decrypt to CLOCK. Nov 2014. | Reported | The New York Times; Schneier on Security |
| 9 | Letters 26–34 (QQPRNGKSS) decrypt to NORTHEAST. Jan 2020. | Reported | The New York Times; Smithsonian Magazine |
| 10 | Letters 22–25 (FLRV) decrypt to EAST. Aug 2020. | Reported | Intel Today; Smithsonian Magazine |
| 11 | "BERLIN CLOCK" refers to the Weltzeituhr (World Clock) at Alexanderplatz, not the Mengenlehreuhr. Nov 2025. | Reported | solvekryptos.com; Wikipedia "Mengenlehreuhr" |

Positions above are 1-indexed as published; the repo uses 0-indexed (`keystream_validator.K4_CRIB_RELEASES`).

## On the plaintext

| # | Statement | Tier | Where reported |
|---|-----------|------|----------------|
| 12 | Two events shaped the plaintext he wrote in 1988: his second trip to Egypt (late 1986) and the fall of the Berlin Wall. | Reported | Open letter to the Kryptos community; Scientific American "final clues" |
| 13 | The codes are about "delivering a message". | Quote | Scientific American; Wikipedia |
| 14 | Asked whether you must be on CIA grounds to solve it: "No." He added that the text refers to something he did at the agency and a location on the grounds, which you would find after deciphering. | Quote + reported | NPR interview transcript; cryptography mailing-list archive |

## On the 2025 archive find

| # | Statement | Tier | Where reported |
|---|-----------|------|----------------|
| 15 | The plaintext scraps reached the Smithsonian's Archives of American Art by mistake, while he was in cancer treatment. | Reported | The New York Times, via Scientific American and RR Auction |
| 16 | The Smithsonian sealed his archive until 2075 after the find. | Reported | RR Auction; search summaries |
| 17 | Kobek and Byrne said it is not a cryptographic solve and that they won't publish the plaintext. | Quote (Kobek) | Scientific American; RR Auction |
| 18 | A K5 exists and is to be released once K4 is solved cryptographically. | Reported | The Washington Post, Nov 2025 |
| 19 | The archive sold for $962,500 on 20 Nov 2025. The buyer was reported as anonymous at the time; Paradigm identified itself in June 2026 and runs a $1-per-guess K4 checker. | Reported | RR Auction; Paradigm |

---

## Sources

- [Wikipedia: Kryptos](https://en.wikipedia.org/wiki/Kryptos)
- [PBS NOVA: Kryptos Q&A](https://www.pbs.org/wgbh/nova/article/sanborn-puzzle/)
- [NPR transcript](https://www.npr.org/transcripts/4684720) · [cryptography mailing-list archive](https://diswww.mit.edu/bloom-picayune/crypto/144361)
- [Scientific American: final clues](https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/) · [solution found](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/) · [final secret](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/)
- [Smithsonian Magazine: NORTHEAST clue](https://www.smithsonianmag.com/smart-news/third-and-final-clue-released-ci-sculptures-last-puzzling-passage-180974102/)
- [NBC News: 2010 clue](https://www.nbcnews.com/id/wbna40294019) · [Schneier: 2014 clue](https://www.schneier.com/blog/archives/2014/11/new_kryptos_clu.html) · [Schneier: Oct 2025](https://www.schneier.com/blog/archives/2025/10/part-four-of-the-kryptos-sculpture.html)
- [RR Auction: discovered, not solved](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/) · [RR Auction: sale result](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/)
- [Paradigm: Project Kryptos](https://www.paradigm.xyz/writing/kryptos) · [Kryptos CTF rules](https://paradigm.xyz/kryptos-ctf/rules)
- [Wikipedia: Mengenlehreuhr](https://en.wikipedia.org/wiki/Mengenlehreuhr) · [solvekryptos](https://solvekryptos.com/solution)
