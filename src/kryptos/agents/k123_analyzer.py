"""K1-K3 Pattern Analysis: Extract Sanborn's "Fingerprint" for K4 Attacks.

Kryptos K1-K3 contain valuable clues about Sanborn's methods and mindset.
This module analyzes solved sections to discover patterns that might apply to K4.

Key Questions:
1. Word length patterns - Does Sanborn favor certain word lengths?
2. Thematic vocabulary - What topics/themes recur?
3. Structural quirks - Spelling errors ("IQLUSION", "UNDERGRUUND")?
4. Artistic choices - Poetry, meter, symbolism?
5. Cipher complexity progression - Does K4 follow a pattern?

Hypothesis: K4 is NOT random - it reflects Sanborn's artistic vision.
Understanding his style narrow the search space dramatically.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Known K1-K3 plaintexts (from CIA/Sanborn confirmations)
K1_PLAINTEXT = """Between subtle shading and the absence of light lies the nuance of iqlusion"""

K2_PLAINTEXT = """It was totally invisible hows that possible they used the earths magnetic field x
the information was gathered and transmitted undergruund to an unknown location x does langley
know about this they should its buried out there somewhere x who knows the exact location only ww
this was his last message x thirtyeight degrees fiftyseven minutes sixpointfive seconds north
seventyseven degrees eight minutes fortyfour seconds west x layer two"""

K3_PLAINTEXT = """Slowly desparatly slowly the remains of passage debris that encumbered the lower
part of the doorway was removed with trembling hands i made a tiny breach in the upper left hand
corner and then widening the hole a little i inserted the candle and peered in the hot air escaping
from the chamber caused the flame to flicker but presently details of the room within emerged from
the mist x can you see anything q"""


@dataclass
class SanbornPattern:
    """A pattern discovered in K1-K3 that might apply to K4."""

    category: str  # 'spelling', 'theme', 'structure', 'artistic', 'cipher'
    description: str
    evidence: list[str]
    k4_hypothesis: str  # How this might apply to K4
    confidence: float


class K123Analyzer:
    """Analyze K1-K3 for patterns that inform K4 attacks."""

    def __init__(self):
        """Initialize analyzer with known plaintexts."""
        self.k1 = self._normalize(K1_PLAINTEXT)
        self.k2 = self._normalize(K2_PLAINTEXT)
        self.k3 = self._normalize(K3_PLAINTEXT)

        self.all_text = f"{self.k1} {self.k2} {self.k3}"
        self.patterns: list[SanbornPattern] = []

    def analyze_all(self) -> list[SanbornPattern]:
        """Run all pattern analyses."""
        self.patterns = []

        self.patterns.extend(self._analyze_spelling_quirks())
        self.patterns.extend(self._analyze_themes())
        self.patterns.extend(self._analyze_word_lengths())
        self.patterns.extend(self._analyze_artistic_choices())
        self.patterns.extend(self._analyze_structural_markers())
        self.patterns.extend(self._analyze_cipher_progression())

        return self.patterns

    def _analyze_spelling_quirks(self) -> list[SanbornPattern]:
        """Find intentional misspellings - these are GOLD for K4."""
        patterns = []

        # Known misspellings
        quirks = {
            "iqlusion": "illusion (I→Q substitution)",
            "undergruund": "underground (O→U substitution)",
            "desparatly": "desperately (E missing)",
        }

        evidence = []
        for wrong, correct in quirks.items():
            if wrong in self.all_text.lower():
                evidence.append(f"'{wrong}' instead of {correct}")

        if evidence:
            patterns.append(
                SanbornPattern(
                    category="spelling",
                    description="Intentional misspellings/substitutions",
                    evidence=evidence,
                    k4_hypothesis="K4 likely contains similar spelling quirks. "
                    "Q↔I, U↔O substitutions may be intentional. "
                    "Look for words that are 'almost' English.",
                    confidence=0.95,
                ),
            )

        return patterns

    def _analyze_themes(self) -> list[SanbornPattern]:
        """Identify recurring themes."""
        patterns = []

        # Thematic word groups
        themes = {
            "secrecy": ["invisible", "buried", "hidden", "secret", "unknown"],
            "location": ["north", "south", "east", "west", "coordinates", "degrees", "minutes", "seconds"],
            "discovery": ["slowly", "emerged", "breach", "peered", "see", "found"],
            "communication": ["message", "transmitted", "information", "gathered"],
            "archaeology": ["debris", "doorway", "chamber", "remains", "passage"],  # K3 is King Tut's tomb!
        }

        for theme_name, keywords in themes.items():
            found = [word for word in keywords if word in self.all_text.lower()]
            if found:
                patterns.append(
                    SanbornPattern(
                        category="theme",
                        description=f"Theme: {theme_name}",
                        evidence=found,
                        k4_hypothesis=f"K4 may continue {theme_name} theme. "
                        f"Try these as cribs: {', '.join(found[:5])}",
                        confidence=0.7 + len(found) * 0.05,
                    ),
                )

        return patterns

    def _analyze_word_lengths(self) -> list[SanbornPattern]:
        """Analyze word length distribution."""
        words = [w for w in self.all_text.split() if w.isalpha()]
        lengths = [len(w) for w in words]
        length_dist = Counter(lengths)

        patterns = []

        # Most common word lengths
        common_lengths = length_dist.most_common(5)
        top_two = f"{common_lengths[0][0]}-{common_lengths[1][0]}"

        patterns.append(
            SanbornPattern(
                category="structure",
                description=f"Preferred word lengths: {', '.join(str(length) for length, _ in common_lengths)}",
                evidence=[f"{length}-letter words: {count} times" for length, count in common_lengths],
                k4_hypothesis=(
                    f"K4 likely has similar word length distribution. "
                    f"When testing transpositions, favor plaintext with {top_two} letter words."
                ),
                confidence=0.75,
            ),
        )

        return patterns

    def _analyze_artistic_choices(self) -> list[SanbornPattern]:
        """Detect artistic/poetic elements."""
        patterns = []

        # K1 has poetic language
        k1_poetic = ["subtle", "shading", "absence", "light", "nuance", "iqlusion"]
        patterns.append(
            SanbornPattern(
                category="artistic",
                description="K1 uses poetic, artistic language",
                evidence=k1_poetic,
                k4_hypothesis="K4 may be poetic or philosophical. "
                "Sanborn is an artist - expect metaphor, symbolism, beauty. "
                "SPY's poetry detection (rhyme, meter, alliteration) will be crucial.",
                confidence=0.85,
            ),
        )

        # K3 is Howard Carter discovering King Tut's tomb
        patterns.append(
            SanbornPattern(
                category="artistic",
                description="K3 quotes historical event (King Tut discovery, 1922)",
                evidence=["slowly desparatly", "chamber", "candle", "mist", "can you see anything"],
                k4_hypothesis="K4 might quote another historical event, literary work, or famous text. "
                "Check cryptography history, CIA history, Cold War events. "
                "The 'WW' in K2 might be Wolfgang Weber or another real person.",
                confidence=0.80,
            ),
        )

        return patterns

    def _analyze_structural_markers(self) -> list[SanbornPattern]:
        """Find structural elements (X markers, coordinates, etc.)."""
        patterns = []

        # X as separator in K2
        x_count = self.k2.lower().count(" x ")
        if x_count > 0:
            patterns.append(
                SanbornPattern(
                    category="structure",
                    description=f"'X' used as separator/delimiter ({x_count} times in K2)",
                    evidence=["X marks section breaks", "Separates distinct ideas"],
                    k4_hypothesis="K4 might use X or other symbols as delimiters. "
                    "Don't treat X as normal letter - it could mark boundaries, layers, or metadata.",
                    confidence=0.90,
                ),
            )

        # Coordinates in K2
        if "degrees" in self.k2.lower():
            patterns.append(
                SanbornPattern(
                    category="structure",
                    description="Geographic coordinates embedded in plaintext",
                    evidence=["38°57'6.5\"N, 77°8'44\"W - CIA headquarters location"],
                    k4_hypothesis="K4 might contain coordinates, dates, or other numeric encodings. "
                    "Look for number patterns, especially related to Kryptos location or key dates.",
                    confidence=0.85,
                ),
            )

        return patterns

    def _analyze_cipher_progression(self) -> list[SanbornPattern]:
        """Analyze cipher complexity progression K1→K2→K3."""
        patterns = []

        patterns.append(
            SanbornPattern(
                category="cipher",
                description="Increasing cipher complexity across sections",
                evidence=[
                    "K1: Modified Vigenère with keyword",
                    "K2: Vigenère with key + coordinate encoding",
                    "K3: Keyed-alphabet transposition",
                    "K4: ???",
                ],
                k4_hypothesis="K4 is likely MOST complex. Expect: "
                "1. Combination of previous techniques (polyalphabetic + transposition) "
                "2. Novel twist we haven't seen "
                "3. Possible 'supercipher' using K1-K3 as keys/tables "
                "4. Layered encryption (decode once, then again)",
                confidence=0.90,
            ),
        )

        # NORTHEAST clue suggests K4 uses different alphabet
        patterns.append(
            SanbornPattern(
                category="cipher",
                description="'NORTHEAST' clue (2020) - characters 26-34",
                evidence=["Sanborn confirmed 'NORTHEAST' appears in K4"],
                k4_hypothesis="Known plaintext: chars 26-34 = 'NORTHEAST'. "
                "This gives us a known-plaintext attack anchor point. "
                "Combined with 'BERLIN' theme from K3, suggests Cold War espionage angle. "
                "Try ciphers where we can lock in NORTHEAST and work outward.",
                confidence=1.0,  # This is confirmed!
            ),
        )

        return patterns

    def generate_report(self) -> str:
        """Generate detailed report of all patterns."""
        if not self.patterns:
            self.analyze_all()

        lines = [
            "# K1-K3 PATTERN ANALYSIS REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            f"Analyzed {len(self.patterns)} patterns across K1, K2, and K3.",
            "These patterns inform our K4 attack strategy.",
            "",
        ]

        # Group by category
        by_category = {}
        for pattern in sorted(self.patterns, key=lambda p: p.confidence, reverse=True):
            if pattern.category not in by_category:
                by_category[pattern.category] = []
            by_category[pattern.category].append(pattern)

        for category, patterns in by_category.items():
            lines.extend([f"## {category.upper()} PATTERNS", ""])

            for pattern in patterns:
                lines.extend(
                    [
                        f"### {pattern.description}",
                        f"**Confidence:** {pattern.confidence:.2f}",
                        "",
                        "**Evidence:**",
                    ],
                )
                for evidence in pattern.evidence:
                    lines.append(f"- {evidence}")

                lines.extend(["", "**K4 Hypothesis:**", f"{pattern.k4_hypothesis}", ""])

        # Strategic recommendations
        lines.extend(
            [
                "## STRATEGIC RECOMMENDATIONS FOR K4",
                "",
                "Based on K1-K3 analysis, prioritize:",
                "",
                "1. **Known-plaintext attacks** using 'NORTHEAST' (chars 26-34)",
                "2. **Spelling-aware search** - expect Q↔I, U↔O substitutions",
                "3. **Thematic cribs** - Try 'BERLIN', 'CLOCK', Cold War terms",
                "4. **Poetry/artistic validation** - SPY NLP to detect Sanborn's style",
                "5. **Supercipher hypothesis** - K4 might use K1-K3 as keys",
                "6. **Historical quotes** - K3 is King Tut, K4 might quote something similar",
                "",
            ],
        )

        return "\n".join(lines)

    def _normalize(self, text: str) -> str:
        """Normalize plaintext."""
        # Remove newlines but keep spaces
        text = " ".join(text.split())
        return text


def main():
    """Generate K1-K3 pattern analysis report."""
    analyzer = K123Analyzer()
    patterns = analyzer.analyze_all()

    print("=" * 80)
    print("K1-K3 PATTERN ANALYSIS")
    print("=" * 80)
    print(f"\nFound {len(patterns)} patterns")
    print()

    for pattern in sorted(patterns, key=lambda p: p.confidence, reverse=True):
        print(f"[{pattern.category.upper():12s}] {pattern.description}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  K4 Impact: {pattern.k4_hypothesis[:100]}...")
        print()

    # Save report
    report = analyzer.generate_report()
    report_path = Path("docs/K123_PATTERN_ANALYSIS.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    main()
