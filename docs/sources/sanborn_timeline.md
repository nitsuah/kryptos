# Sanborn timeline (working)
This file is a working timeline of public statements, interviews, and primary sources where Jim Sanborn discusses Kryptos. Fill entries with a short quote, date, and source URL. Use the helper script `scripts/tools/collect_sanborn_sources.py` to fetch and generate entries automatically from a list of URLs.

Format (one entry per section):

- Date: YYYY-MM-DD
- Source: URL
- Title: Page title or interview name
If you prefer automatic collection, place a newline-separated list of URLs in `scripts/sources_urls.txt` and run:

```bash
python scripts/tools/collect_sanborn_sources.py scripts/sources_urls.txt docs/sources/sanborn_timeline.md
```
- Excerpt: Short quoted excerpt (1-2 sentences)
- Notes: Why this may be relevant to K4 (crib candidate, theme, time clue, directional hint, etc.)

Example

---

- Date: 1990-10-01
- Source: https://example.org/interview
- Title: "Artist on Kryptos"
- Excerpt: "I used a clock pattern to order some of the shifts..."
- Notes: Mentions 'clock' explicitly — candidate for Berlin-clock derived key streams.

---

Automatic collection

If you prefer automatic collection, place a newline-separated list of URLs in `scripts/sources_urls.txt` and run:

```bash
python scripts/tools/collect_sanborn_sources.py scripts/sources_urls.txt docs/sources/sanborn_timeline.md
```

The script will fetch each URL, extract the title and first paragraph, and append an entry to the timeline. Always manually verify quoted excerpts against the original page before using any crib as a hard constraint.

---

- Date: 2025-08-14
- Source: [https://en.wikipedia.org/wiki/Jim_Sanborn](https://en.wikipedia.org/wiki/Jim_Sanborn)
- Title: "Jim Sanborn — Wikipedia"
- Excerpt: "Herbert James Sanborn, Jr. (born November 14, 1945) is an American sculptor. He is best known for creating the encrypted Kryptos sculpture at CIA headquarters in Langley, Virginia."
- Notes: Canonical biographical summary and links to primary sources (Smithsonian Archives; interviews). Useful to seed artist-derived crib candidates (e.g., 'BERLIN', 'MAGNETIC', 'PALIMPSEST') and provenance dates. Verify any quoted clue text against the original interviews linked in the references.

---

- Date: 2025-10-21
- Source: [https://en.wikipedia.org/wiki/Kryptos](https://en.wikipedia.org/wiki/Kryptos)
- Title: "Kryptos — Wikipedia"
- Excerpt: "The sculpture comprises four large copper plates... The main sculpture contains four separate enigmatic messages, three of which have been deciphered. The fourth remains one of the world's more famous unsolved codes."
- Notes: Comprehensive summary of the four encrypted passages, published clues (2010 "BERLIN" clue, 2014 "CLOCK" clue, 2020/2023 NORTHEAST/EAST letters). Highly relevant for crib extraction: coordinates mentioned in passage 2, references to Berlin clock (Mengenlehreuhr), and the keyword hints (PALIMPSEST, ABSCISSA, KRYPTOS).

---

- Date: 2025-08-08
- Source: [https://jimsanborn.net/](https://jimsanborn.net/)
- Title: "Jim Sanborn Studio (official)"
- Excerpt: "Public spaces, installations, projections, photos, videos, KRYPTOS — an overview of Sanborn's major public works including Kryptos and related cryptographic pieces."
- Notes: Official artist site and archive links. Good source for context on Sanborn's intent and the broader set of cryptographic motifs he uses (magnetism, clocks, transposition). Use to expand crib candidate set (words appearing across works and exhibition notes).

---

- Date: 2003-06-20
- Source: [http://www.elonka.com/kryptos/sanborn.html](http://www.elonka.com/kryptos/sanborn.html)
- Title: "Jim Sanborn: Sculptor, Photographer, Artist (Elonka Dunin)"
- Excerpt: "Sanborn is probably best known for the 'Kryptos' sculpture installed at CIA Headquarters in 1990, which displays encrypted messages which continue to stump code-breakers to this day."
- Notes: Fan-curated archive with biographical notes, selected works, and pointers to original interviews and images (useful for provenance and material references like lodestones and Cyrillic Projector).

---

- Date: 2005-01-20
- Source: [https://www.wired.com/2005/01/questions-for-kryptos-creator/](https://www.wired.com/2005/01/questions-for-kryptos-creator/)
- Title: "Questions for Kryptos' Creator — Wired" (Kim Zetter interview)
- Excerpt: "In part of the code that's been deciphered, I refer to an act that took place when I was at the agency and a location that's on the grounds of the agency. So ... you have to decipher the piece and then go to the agency and find that place. There are, for example, longitude and latitude coordinates on the piece, which refer to locations of the agency."
- Notes: Direct confirmation that the text contains coordinates and references to a specific act/location Sanborn associated with the CIA grounds — strong evidence that geographic/coordinate-derived cribs or place-names are relevant.

---

- Date: 2005-01-20
- Source: [https://www.wired.com/2005/01/questions-for-kryptos-creator/](https://www.wired.com/2005/01/questions-for-kryptos-creator/)
- Title: "Questions for Kryptos' Creator — Wired" (Kim Zetter interview)
- Excerpt: "I made reference in the encoded text to something I could have carried out."
- Notes: Sanborn acknowledges that a referenced 'act' in the text could have been carried out by him — implies literal actions described on the sculpture may map to instructions or positional clues (useful for interpreting verbs/commands in K4).

---

- Date: 2005-01-20
- Source: [https://www.wired.com/2005/01/questions-for-kryptos-creator/](https://www.wired.com/2005/01/questions-for-kryptos-creator/)
- Title: "Questions for Kryptos' Creator — Wired" (Kim Zetter interview)
- Excerpt: "I would think five or six." (asked how many cryptographic techniques he used)
- Notes: Sanborn's estimate of the number of techniques ("five or six") is a confirmed clue about cipher complexity — suggests K4 combines multiple layered encipherment strategies.

---

- Date: 1990-11-03
- Source: [https://www.cia.gov/legacy/headquarters/kryptos-sculpture/](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/)
- Title: "\"Kryptos\" Sculpture — CIA"
- Excerpt: "James Sanborn once said, 'They will be able to read what I wrote, but what I wrote is a mystery itself.'"
- Notes: Direct artist quotation published in the agency's official description — confirms Sanborn's intent to create layered ambiguity and supports cautious use of literal-sense cribs (surface-readable phrases may be metaphorical).

---

- Date: 1990-11-03
- Source: [https://www.cia.gov/legacy/headquarters/kryptos-sculpture/](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/)
- Title: "\"Kryptos\" Sculpture — CIA"
- Excerpt: "I gave it to William Webster at the dedication ceremony with a wax seal on it, but in fact I really didn't tell him the whole story. I definitely didn't give him the last section, which has never been deciphered."
- Notes: Sanborn's admission about the dedication envelope and deliberately withholding K4 confirms there is a canonical solution record and that the final section was intentionally kept secret from the Agency director — reinforces that verification rests with the artist and that certain referents (e.g., 'WW' -> William Webster) are authoritatively confirmed.

- Date: 1990-11-03
- Source: [https://www.cia.gov/legacy/headquarters/kryptos-sculpture/](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/)
- Title: "\"Kryptos\" Sculpture — CIA"
- Excerpt: "The theme of this sculpture is 'intelligence gathering.' It was dedicated on Nov. 3, 1990... The copperplate screen has exactly 1,735 alphabetic letters cut into it."
- Notes: Official agency page describing materials (petrified wood, lodestone, copper), the intention (intelligence gathering), and public history. Good for surface-level provenance and the Agency's account of solved passages.

---

- Date: 2005-01-20
- Source: [https://www.wired.com/2005/01/questions-for-kryptos-creator/](https://www.wired.com/2005/01/questions-for-kryptos-creator/)
- Title: "Questions for Kryptos' Creator — Wired"
- Excerpt: "For the student of cryptography it's always helpful to gather as much information as possible when zeroing in on and encoding a system... I made reference in the encoded text to something I could have carried out."
- Notes: Interview transcript with Jim Sanborn (Kim Zetter). Contains several first-person statements about intent, use of lodestones, references to coordinate clues and staged difficulty across the courtyard pieces — high-value for crib/context generation.

---

- Date: 2009-07-14
- Source: https://www.aaa.si.edu/collections/interviews/oral-history-interview-jim-sanborn-15700
- Title: "Oral history interview with Jim Sanborn, 2009 Jul 14-16"
- Excerpt: Transcript available from the Archives of American Art (Avis Berman interview). Usage conditions apply; the transcript contains first-person recollections about the commissioning and conceptualization of Kryptos and related public commissions.
- Notes: Primary-source oral-history transcript — consult the Archives of American Art transcript for direct quotes (downloadable PDF). This record supports adding historically-grounded crib candidates but the transcript has usage restrictions; only metadata added here.
