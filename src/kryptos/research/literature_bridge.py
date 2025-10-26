"""Bridge between academic research and attack provenance.

This module connects:
- Academic paper search (arXiv, IACR)
- Attack parameter extraction
- Attack provenance logging

Enables: "What has academia tried that we haven't?"
"""

from __future__ import annotations

from typing import Any

from kryptos.provenance.attack_log import AttackLogger, AttackParameters
from kryptos.research.attack_extractor import AttackExtractor
from kryptos.research.paper_search import PaperSearch


class LiteratureGapAnalyzer:
    def __init__(
        self,
        attack_logger: AttackLogger | None = None,
        paper_searcher: PaperSearch | None = None,
        attack_extractor: AttackExtractor | None = None,
    ):
        """Initialize gap analyzer.

        Args:
            attack_logger: Attack provenance logger
            paper_searcher: Academic paper searcher
            attack_extractor: Attack parameter extractor
        """
        self.attack_logger = attack_logger or AttackLogger()
        self.paper_searcher = paper_searcher or PaperSearch()
        self.attack_extractor = attack_extractor or AttackExtractor()

    def find_literature_gaps(
        self,
        query: str,
        ciphertext: str,
        max_papers: int = 50,
    ) -> dict[str, Any]:
        """Find attacks from literature that we haven't tried.

        Args:
            query: Search query for papers
            ciphertext: Ciphertext we're analyzing
            max_papers: Maximum papers to analyze

        Returns:
            Gap analysis report
        """
        papers = self.paper_searcher.search_combined(query, max_results_per_source=max_papers // 2)

        literature_attacks = self.attack_extractor.extract_from_papers(papers)

        untried_attacks = []
        tried_attacks = []

        for extracted in literature_attacks:
            params_dict = extracted.to_attack_parameters()
            params = AttackParameters(**params_dict)

            if self.attack_logger.is_duplicate(params):
                tried_attacks.append(extracted)
            else:
                untried_attacks.append(extracted)

        return {
            "query": query,
            "papers_analyzed": len(papers),
            "attacks_extracted": len(literature_attacks),
            "already_tried": len(tried_attacks),
            "not_yet_tried": len(untried_attacks),
            "coverage_rate": (len(tried_attacks) / len(literature_attacks) * 100 if literature_attacks else 0.0),
            "untried_attacks": [
                {
                    "cipher_type": a.cipher_type,
                    "attack_method": a.attack_method,
                    "parameters": a.key_parameters,
                    "crib": a.crib_text,
                    "source": a.source_paper,
                    "confidence": a.confidence,
                }
                for a in untried_attacks[:10]
            ],
            "papers": [
                {
                    "paper_id": p.paper_id,
                    "title": p.title,
                    "year": p.year,
                    "relevance": p.relevance_score,
                }
                for p in papers[:10]
            ],
        }

    def get_literature_recommendations(
        self,
        query: str,
        ciphertext: str,
        top_n: int = 5,
    ) -> list[dict[str, Any]]:
        """Get top N attack recommendations from literature.

        Args:
            query: Search query
            ciphertext: Ciphertext
            top_n: Number of recommendations

        Returns:
            Prioritized list of attacks to try
        """
        gap_analysis = self.find_literature_gaps(query, ciphertext)

        untried = gap_analysis["untried_attacks"]
        sorted_attacks = sorted(untried, key=lambda x: x["confidence"], reverse=True)

        return sorted_attacks[:top_n]

    def generate_coverage_report(self, queries: list[str], ciphertext: str) -> dict[str, Any]:
        total_papers = 0
        total_attacks = 0
        total_tried = 0
        all_untried = []

        for query in queries:
            gap_analysis = self.find_literature_gaps(query, ciphertext, max_papers=20)
            total_papers += gap_analysis["papers_analyzed"]
            total_attacks += gap_analysis["attacks_extracted"]
            total_tried += gap_analysis["already_tried"]
            all_untried.extend(gap_analysis["untried_attacks"])

        seen = set()
        unique_untried = []
        for attack in all_untried:
            key = (attack["cipher_type"], attack["attack_method"], str(attack["parameters"]))
            if key not in seen:
                seen.add(key)
                unique_untried.append(attack)

        return {
            "queries": queries,
            "total_papers": total_papers,
            "total_attacks": total_attacks,
            "already_tried": total_tried,
            "unique_untried": len(unique_untried),
            "literature_coverage": (total_tried / total_attacks * 100 if total_attacks else 0.0),
            "top_gaps": sorted(unique_untried, key=lambda x: x["confidence"], reverse=True)[:20],
        }


def demo_literature_gap_analysis():
    print("=" * 80)
    print("LITERATURE GAP ANALYSIS DEMO")
    print("=" * 80)
    print()
    print("Problem: What has academia tried that we haven't?")
    print("Solution: Cross-reference papers with attack provenance log")
    print()

    analyzer = LiteratureGapAnalyzer()

    k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

    print("-" * 80)
    print("1. Search Academic Literature")
    print("-" * 80)

    gap_analysis = analyzer.find_literature_gaps("vigenere cryptanalysis", k4_sample, max_papers=10)

    print(f"Papers analyzed: {gap_analysis['papers_analyzed']}")
    print(f"Attacks extracted: {gap_analysis['attacks_extracted']}")
    print(f"Already tried: {gap_analysis['already_tried']}")
    print(f"Not yet tried: {gap_analysis['not_yet_tried']}")
    print(f"Coverage rate: {gap_analysis['coverage_rate']:.1f}%")
    print()

    print("-" * 80)
    print("2. Untried Attacks from Literature")
    print("-" * 80)

    for i, attack in enumerate(gap_analysis["untried_attacks"][:5], 1):
        print(f"{i}. {attack['cipher_type']} - {attack['attack_method']}")
        print(f"   Parameters: {attack['parameters']}")
        print(f"   Source: {attack['source']}")
        print(f"   Confidence: {attack['confidence']}")
        print()

    print("-" * 80)
    print("3. Literature Recommendations")
    print("-" * 80)

    recommendations = analyzer.get_literature_recommendations("kryptos cryptanalysis", k4_sample, top_n=3)

    print(f"Top {len(recommendations)} attacks to try:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['cipher_type']}: {rec['attack_method']}")
        print(f"   From: {rec['source']}")
    print()

    print("-" * 80)
    print("4. Comprehensive Coverage Report")
    print("-" * 80)

    queries = [
        "vigenere cryptanalysis",
        "transposition cipher",
        "kryptos k4",
    ]

    coverage_report = analyzer.generate_coverage_report(queries, k4_sample)

    print(f"Queries: {', '.join(queries)}")
    print(f"Total papers: {coverage_report['total_papers']}")
    print(f"Total attacks: {coverage_report['total_attacks']}")
    print(f"Literature coverage: {coverage_report['literature_coverage']:.1f}%")
    print(f"Unique gaps identified: {coverage_report['unique_untried']}")
    print()

    print("=" * 80)
    print("SPRINT 4.2: Academic Integration Complete ✓")
    print("=" * 80)
    print()
    print("Can now answer:")
    print("  - What has academia tried? → Extract from papers")
    print("  - Have we tried it? → Cross-ref with provenance log")
    print("  - What should we try next? → Prioritized gap list")


if __name__ == "__main__":
    demo_literature_gap_analysis()
