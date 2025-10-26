"""SPY Agent: Pattern Recognition Specialist for K4 Cryptanalysis.

The SPY agent analyzes candidate plaintexts for hidden patterns, linguistic
anomalies, and structural features that may indicate correct decryption.
Acts as an expert pattern recognizer to surface insights that automated
scoring might miss.

Version 2.0: Enhanced with NLP capabilities (NER, POS tagging, dependency
parsing, semantic analysis) to identify linguistic structures beyond pattern
matching.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

try:
    from .spy_nlp import SPACY_AVAILABLE, WORDNET_AVAILABLE, NLPInsight, SpyNLP
except ImportError:
    SPACY_AVAILABLE = False
    WORDNET_AVAILABLE = False
    SpyNLP = None
    NLPInsight = None


@dataclass
class PatternInsight:
    category: str
    description: str
    evidence: str
    confidence: float
    position: int | None = None


class SpyAgent:
    def __init__(self, cribs: list[str] | None = None):
        self.cribs = cribs or ['BERLIN', 'CLOCK', 'KRYPTOS', 'EAST', 'NORTH', 'PALIMPSEST']

        self.nlp = None
        self.nlp_available = False
        if SPACY_AVAILABLE and SpyNLP:
            try:
                self.nlp = SpyNLP()
                self.nlp_available = True
            except Exception:
                pass

    def analyze_candidate(self, plaintext: str, candidate_id: str = '') -> dict[str, Any]:
        seq = ''.join(c for c in plaintext.upper() if c.isalpha())

        insights = []

        insights.extend(self._find_repeats(seq))

        insights.extend(self._find_palindromes(seq))

        insights.extend(self._find_cribs(seq))

        insights.extend(self._detect_words(seq))

        insights.extend(self._check_acrostics(seq))

        insights.extend(self._frequency_anomalies(seq))

        insights.extend(self._find_anagrams(seq))

        insights.extend(self._spacing_patterns(seq))

        if self.nlp_available:
            plaintext_readable = plaintext.lower().strip()
            nlp_insights = self.nlp.analyze(plaintext_readable)

            for nlp_insight in nlp_insights:
                confidence_boost = {
                    'entity': 0.3,
                    'dependency': 0.2,
                    'pos': 0.15,
                    'semantic': 0.15,
                }.get(nlp_insight.category, 0.1)

                adjusted_confidence = min(1.0, nlp_insight.confidence + confidence_boost)

                insights.append(
                    PatternInsight(
                        category=f'nlp_{nlp_insight.category}',
                        description=f"[NLP] {nlp_insight.description}",
                        evidence=nlp_insight.evidence,
                        confidence=adjusted_confidence,
                        position=nlp_insight.position,
                    ),
                )

        return {
            'candidate_id': candidate_id,
            'plaintext': plaintext,
            'insights': insights,
            'insight_count': len(insights),
            'high_confidence_insights': [i for i in insights if i.confidence >= 0.7],
            'crib_matches': [i for i in insights if i.category == 'crib'],
            'nlp_insights': [i for i in insights if i.category.startswith('nlp_')],
            'pattern_score': self._compute_pattern_score(insights),
            'nlp_enabled': self.nlp_available,
        }

    def _find_repeats(self, text: str, min_length: int = 3, min_count: int = 2) -> list[PatternInsight]:
        insights = []
        seen_patterns = set()

        for length in range(min_length, min(11, len(text) // 2 + 1)):
            for i in range(len(text) - length + 1):
                substring = text[i : i + length]

                if substring in seen_patterns:
                    continue

                positions = []
                pos = 0
                while True:
                    pos = text.find(substring, pos)
                    if pos == -1:
                        break
                    positions.append(pos)
                    pos += 1

                if len(positions) >= min_count:
                    seen_patterns.add(substring)

                    gaps = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
                    avg_gap = sum(gaps) / len(gaps) if gaps else 0

                    confidence = min(1.0, (len(positions) - 1) * 0.2 + length * 0.05)

                    insights.append(
                        PatternInsight(
                            category='repeat',
                            description=f"'{substring}' repeats {len(positions)} times (avg gap: {avg_gap:.1f})",
                            evidence=f"Positions: {positions[:5]}{'...' if len(positions) > 5 else ''}",
                            confidence=confidence,
                            position=positions[0],
                        ),
                    )

        return insights

    def _find_palindromes(self, text: str, min_length: int = 5) -> list[PatternInsight]:
        insights = []

        for length in range(min_length, min(16, len(text) + 1)):
            for i in range(len(text) - length + 1):
                substring = text[i : i + length]
                if substring == substring[::-1]:
                    confidence = min(1.0, length * 0.1)

                    insights.append(
                        PatternInsight(
                            category='palindrome',
                            description=f"Palindrome of length {length}: '{substring}'",
                            evidence=f"Position {i}",
                            confidence=confidence,
                            position=i,
                        ),
                    )

        return insights

    def _find_cribs(self, text: str) -> list[PatternInsight]:
        insights = []

        for crib in self.cribs:
            crib_upper = crib.upper()
            pos = text.find(crib_upper)

            if pos != -1:
                insights.append(
                    PatternInsight(
                        category='crib',
                        description=f"CRIB MATCH: '{crib_upper}' found!",
                        evidence=f"Position {pos}",
                        confidence=0.95,
                        position=pos,
                    ),
                )

            if len(crib_upper) >= 4:
                for i in range(len(text) - 3):
                    window = text[i : i + 4]
                    if window in crib_upper:
                        insights.append(
                            PatternInsight(
                                category='crib_partial',
                                description=f"Partial crib match: '{window}' (from '{crib_upper}')",
                                evidence=f"Position {i}",
                                confidence=0.4,
                                position=i,
                            ),
                        )

        return insights

    def _detect_words(self, text: str) -> list[PatternInsight]:
        insights = []

        common_words = {
            'THE',
            'AND',
            'FOR',
            'ARE',
            'BUT',
            'NOT',
            'YOU',
            'ALL',
            'CAN',
            'HAD',
            'HER',
            'WAS',
            'ONE',
            'OUR',
            'OUT',
            'HAS',
            'HIS',
            'HOW',
            'ITS',
            'MAY',
        }

        found_words = []
        for word in common_words:
            pos = text.find(word)
            if pos != -1:
                found_words.append((word, pos))

        if found_words:
            insights.append(
                PatternInsight(
                    category='words',
                    description=f"Found {len(found_words)} common words",
                    evidence=', '.join(f"{w}@{p}" for w, p in found_words[:5]),
                    confidence=min(1.0, len(found_words) * 0.15),
                ),
            )

        return insights

    def _check_acrostics(self, text: str) -> list[PatternInsight]:
        insights = []

        for block_size in [3, 4, 5, 6]:
            if len(text) < block_size * 2:
                continue

            acrostic = ''
            for i in range(0, len(text), block_size):
                if i < len(text):
                    acrostic += text[i]

            for crib in self.cribs:
                if crib.upper() in acrostic:
                    insights.append(
                        PatternInsight(
                            category='acrostic',
                            description=f"Acrostic (block={block_size}) contains '{crib.upper()}'",
                            evidence=f"Acrostic: {acrostic}",
                            confidence=0.6,
                        ),
                    )

        return insights

    def _frequency_anomalies(self, text: str) -> list[PatternInsight]:
        insights = []

        if len(text) < 10:
            return insights

        freq = Counter(text)
        total = len(text)

        for letter, count in freq.most_common(5):
            ratio = count / total
            if ratio > 0.20:
                insights.append(
                    PatternInsight(
                        category='frequency_anomaly',
                        description=f"Letter '{letter}' appears {ratio * 100:.1f}% (unusually high)",
                        evidence=f"{count} out of {total} chars",
                        confidence=min(1.0, (ratio - 0.15) * 2),
                    ),
                )

        common_missing = []
        for letter in 'ETAOIN':
            if letter not in freq:
                common_missing.append(letter)

        if common_missing:
            insights.append(
                PatternInsight(
                    category='frequency_anomaly',
                    description=f"Common letters missing: {', '.join(common_missing)}",
                    evidence="Expected in English text",
                    confidence=0.5,
                ),
            )

        return insights

    def _find_anagrams(self, text: str) -> list[PatternInsight]:
        insights = []

        for crib in self.cribs:
            crib_sorted = ''.join(sorted(crib.upper()))

            for i in range(len(text) - len(crib) + 1):
                window = text[i : i + len(crib)]
                window_sorted = ''.join(sorted(window))

                if window_sorted == crib_sorted:
                    insights.append(
                        PatternInsight(
                            category='anagram',
                            description=f"Anagram of '{crib}' found: '{window}'",
                            evidence=f"Position {i}",
                            confidence=0.7,
                            position=i,
                        ),
                    )

        return insights

    def _spacing_patterns(self, text: str) -> list[PatternInsight]:
        insights = []

        for period in range(2, min(15, len(text) // 4 + 1)):
            extracted = ''.join(text[i] for i in range(0, len(text), period))

            for crib in self.cribs:
                if len(crib) >= 4 and crib.upper() in extracted:
                    insights.append(
                        PatternInsight(
                            category='spacing_pattern',
                            description=f"Every {period}th char contains '{crib.upper()}'",
                            evidence=f"Extracted: {extracted}",
                            confidence=0.8,
                        ),
                    )

        return insights

    def _compute_pattern_score(self, insights: list[PatternInsight]) -> float:
        if not insights:
            return 0.0

        category_weights = {
            'crib': 10.0,
            'crib_partial': 3.0,
            'repeat': 2.0,
            'words': 4.0,
            'palindrome': 1.5,
            'acrostic': 5.0,
            'anagram': 6.0,
            'spacing_pattern': 7.0,
            'frequency_anomaly': -1.0,
        }

        total_score = 0.0
        for insight in insights:
            weight = category_weights.get(insight.category, 1.0)
            total_score += insight.confidence * weight

        return total_score

    def rank_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        analyzed = []

        for cand in candidates:
            plaintext = cand.get('plaintext', '')
            cand_id = cand.get('id', '')

            analysis = self.analyze_candidate(plaintext, cand_id)
            cand['spy_analysis'] = analysis
            cand['pattern_score'] = analysis['pattern_score']

            analyzed.append(cand)

        analyzed.sort(key=lambda c: c['pattern_score'], reverse=True)

        return analyzed


def quick_spy_analysis(plaintext: str, cribs: list[str] | None = None) -> dict[str, Any]:
    spy = SpyAgent(cribs=cribs)
    return spy.analyze_candidate(plaintext)


def spy_report(plaintext: str, cribs: list[str] | None = None) -> str:
    analysis = quick_spy_analysis(plaintext, cribs)

    report = []
    report.append("=" * 80)
    report.append("SPY AGENT PATTERN ANALYSIS")
    report.append("=" * 80)
    report.append(f"Plaintext: {analysis['plaintext'][:74]}")
    report.append(f"Insights found: {analysis['insight_count']}")
    report.append(f"Pattern score: {analysis['pattern_score']:.2f}")
    report.append("")

    if analysis['crib_matches']:
        report.append("🎯 CRIB MATCHES:")
        for insight in analysis['crib_matches']:
            report.append(f"  - {insight.description} (confidence: {insight.confidence:.2f})")
        report.append("")

    high_conf = analysis['high_confidence_insights']
    if high_conf:
        report.append("⭐ HIGH-CONFIDENCE PATTERNS:")
        for insight in high_conf:
            report.append(f"  - [{insight.category}] {insight.description}")
            report.append(f"    Evidence: {insight.evidence} (confidence: {insight.confidence:.2f})")
        report.append("")

    all_insights = analysis['insights']
    if all_insights:
        report.append("📊 ALL PATTERNS:")
        for insight in all_insights:
            report.append(f"  - [{insight.category}] {insight.description} ({insight.confidence:.2f})")

    report.append("=" * 80)

    return '\n'.join(report)
