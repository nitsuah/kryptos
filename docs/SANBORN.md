# Jim Sanborn — notes and research pointers

This note collects what is publicly known or widely reported about Jim Sanborn (the sculptor who
created the Kryptos piece), the kinds of clues he has given publicly, and pragmatic next steps for
researching artist-level hints that might inform K4 hypotheses.

Use this as an operational checklist rather than an authoritative biography. Always verify anything
you plan to treat as a crib or hard constraint against a primary source (interview transcript,
museum statement, archived press release, or Sanborn's own website).

## High-level, well-established facts

- Jim Sanborn is the artist who created the Kryptos sculpture. The sculpture is installed at the CIA
  headquarters grounds in Langley, Virginia.
- Kryptos is an art piece that intentionally incorporates encrypted text and layered puzzles.
  Several sections (commonly labelled K1–K3) have been solved publicly; one section (K4) remains
  widely reported as unsolved.
- Over the years Sanborn has answered questions and given limited clues or clarifications in public
  interviews, artist statements, and correspondence with the community. He has also been careful
  about what he releases publicly — many clues are partial and intended to nudge rather than hand
  over the solution.

## Characteristics of artist-level clues (what to look for)

- The artist often frames context in terms of geography, time, and artifact metaphor: place names,
  clocks/time references, and directional words appear in the sculpture's plaintext and in reported
  cribs.
- Deliberate misspellings and orthographic anomalies appear in solved sections; these are likely
  part of Sanborn's design language and may repeat as a theme (e.g., nonstandard spellings preserved
  rather than corrected).
- Sanborn's public remarks can be terse and poetic; a seemingly throwaway phrase in an interview may
  be meant as a hint rather than pure commentary.

## Research sources to collect (priority order)

1. Sanborn's own website, gallery listings, or artist statements — primary and preferred. 2.
Contemporary press coverage and exhibition notes from the time of installation (press releases,
museum/CIA publications). 3. Transcripts and recordings of interviews with Sanborn where he
discusses Kryptos; pay attention to offhand details about sources, inspirations, or words he
repeats. 4. Archive threads and community-sourced timelines (Kryptos Wiki pages, well-documented
blog posts). Use these as pointers but verify primary claims before treating them as cribs. 5.
Scholarly or journalistic treatments that analyze the sculpture's iconography and references — these
sometimes surface overlooked contextual clues.

## Practical hypotheses to prioritize for K4 (how artist clues map to cipher hypotheses)

- Time-based keying: any mention of clocks, temporal events, or numerically-encoded times suggests
  testing key-streams derived from clock encodings (e.g., Berlin Clock / Mengenlehreuhr patterns,
  historical timestamps).
- Geographic and directional anchors: repeated place names (cities, cardinal directions) suggest
  positional crib bonuses and multi-crib positional transposition stages — prioritize cribs that
  align to reported indices.
- Intentional misspellings: treat misspellings and anomalies as canonical plaintext rather than
  noise when scoring and when building crib constraints.
- Artist-supplied words or phrases: when Sanborn mentions words he used in the piece (even in
  passing), treat those as high-priority cribs but validate their start indices before hard-
  constraining.

## Suggested next steps (actionable, reproducible)

1. Build a short timeline of Sanborn statements about Kryptos (date, medium, exact quoted text,
source URL/archive). Store this as `docs/sources/sanborn_timeline.md` for reproducibility. 2.
Extract candidate one- or two-word cribs that appear in those statements and add them to
`config/crubs_candidates.txt` (or equivalent). Treat them as soft cribs first (score boosts), not
hard constraints. 3. Run targeted scoring passes that boost candidates containing those words
(positional and non-positional). Compare rank shifts and surface candidates for manual review. 4.
For any mention of dates or times, enumerate small key-stream families derived from time encodings
(e.g., 24-hour/12-hour, Berlin-clock lamp patterns) and sweep them with the Berlin-clock stage in a
small budget run. 5. Cross-check artist themes against the sculpture text: if an interview
emphasizes a theme (e.g., geography, time, espionage jargon), prioritize scoring features sensitive
to those themes (wordlist filters, domain-specific vocabularies).

## Safety and provenance notes

- Do not treat community posts or hearsay as authoritative. Always link a claim to a verifiable
  primary source before hard-wiring it into the pipeline.
- Maintain provenance for any crib added from Sanborn statements: record the quote, source URL, and
  timestamp so the decision can be audited later.

## If you want, I can

- Pull together a first-pass timeline of public Sanborn remarks (I can fetch and summarize sources
  if you want me to search the web).
- Generate a crib candidate file from that timeline and run a small scoring sweep with the Berlin-
  clock and multi-crib transposition stages.

Decide whether you want me to fetch primary sources and build the timeline automatically (I can do
that next), or if you prefer to review sources manually and I hook them into the pipeline
afterwards.
