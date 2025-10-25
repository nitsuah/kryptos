"""Attack Generation Engine for systematic K4 cryptanalysis.

Converts research insights (Q-Research hints, coverage gaps, literature analysis)
into executable AttackParameters for OPS Director orchestration.

Philosophy: "Turn every research insight into an actionable attack. No manual
parameter tuning. Let data drive the attack queue."
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kryptos.analysis.strategic_coverage import StrategicCoverageAnalyzer
from kryptos.log_setup import setup_logging
from kryptos.provenance.attack_log import AttackLogger, AttackParameters
from kryptos.research.q_patterns import (
    QResearchAnalyzer,
    TranspositionHint,
    VigenereMetrics,
)


@dataclass
class AttackSpec:
    """Specification for a generated attack with metadata."""

    parameters: AttackParameters
    priority: float  # 0.0-1.0, higher = run first
    source: str  # "q_research", "coverage_gap", "literature"
    rationale: str  # Why this attack was generated
    tags: list[str]

    def fingerprint(self) -> str:
        """Generate fingerprint for deduplication."""
        return self.parameters.fingerprint()


class AttackGenerator:
    """Generate attack parameters from research insights.

    Integrates with:
    - QResearchAnalyzer: Convert cryptanalysis hints to parameters
    - StrategicCoverageAnalyzer: Target uncovered parameter spaces
    - LiteratureGapAnalyzer: Extract parameters from academic papers
    - AttackLogger: Deduplicate attacks

    Workflow:
    1. Analyze ciphertext with Q-Research
    2. Generate attacks from hints (Vigenère key lengths, transposition periods)
    3. Check coverage gaps and generate filling attacks
    4. Deduplicate against AttackLogger
    5. Prioritize by confidence × coverage gap
    6. Return sorted attack queue
    """

    def __init__(
        self,
        attack_logger: AttackLogger | None = None,
        coverage_analyzer: StrategicCoverageAnalyzer | None = None,
        log_level: str = "INFO",
    ):
        """Initialize attack generator.

        Args:
            attack_logger: Logger for deduplication
            coverage_analyzer: Coverage analyzer for gap detection
            log_level: Logging level
        """
        self.attack_logger = attack_logger or AttackLogger()
        self.coverage_analyzer = coverage_analyzer or StrategicCoverageAnalyzer()
        self.q_analyzer = QResearchAnalyzer()
        self.log = setup_logging(level=log_level, logger_name="kryptos.pipeline.attack_generator")

        # Generation statistics
        self.stats = {
            "generated": 0,
            "duplicates_filtered": 0,
            "from_q_hints": 0,
            "from_coverage_gaps": 0,
            "from_literature": 0,
        }

    def generate_from_q_hints(
        self,
        ciphertext: str,
        max_attacks: int = 50,
    ) -> list[AttackSpec]:
        """Generate attacks from Q-Research cryptanalysis hints.

        Args:
            ciphertext: Ciphertext to analyze
            max_attacks: Maximum attacks to generate

        Returns:
            List of attack specifications
        """
        self.log.info("Generating attacks from Q-Research hints")

        attacks = []

        # 1. Vigenère analysis
        vigenere_metrics = self.q_analyzer.vigenere_analysis(ciphertext)
        if vigenere_metrics.confidence > 0.3:
            attacks.extend(self._vigenere_hints_to_attacks(vigenere_metrics, ciphertext))

        # 2. Transposition hints
        transposition_hints = self.q_analyzer.detect_transposition_hints(ciphertext)
        if transposition_hints:
            attacks.extend(self._transposition_hints_to_attacks(transposition_hints, ciphertext))

        # 3. Strategy suggestions
        strategies = self.q_analyzer.suggest_attack_strategies(ciphertext)
        attacks.extend(self._strategies_to_attacks(strategies, ciphertext))

        # Deduplicate and prioritize
        attacks = self._deduplicate_attacks(attacks)
        attacks = sorted(attacks, key=lambda x: x.priority, reverse=True)

        self.stats["from_q_hints"] += len(attacks)
        self.stats["generated"] += len(attacks)
        self.log.info(f"Generated {len(attacks)} attacks from Q-Research hints")

        return attacks[:max_attacks]

    def generate_from_coverage_gaps(
        self,
        cipher_type: str,
        ciphertext: str,
        target_coverage: float = 0.9,
        max_attacks: int = 100,
    ) -> list[AttackSpec]:
        """Generate attacks targeting coverage gaps.

        Args:
            cipher_type: Cipher type to analyze ("vigenere", "transposition", etc.)
            ciphertext: Ciphertext for context
            target_coverage: Target coverage percentage (0.0-1.0)
            max_attacks: Maximum attacks to generate

        Returns:
            List of attack specifications targeting gaps
        """
        self.log.info(f"Generating attacks for {cipher_type} coverage gaps")

        attacks = []

        # Get coverage report
        report = self.coverage_analyzer.tracker.get_coverage_report(cipher_type)

        # Check if we have coverage data
        cipher_data = report.get("cipher_types", {}).get(cipher_type)

        if not cipher_data:
            self.log.warning(f"No coverage data for {cipher_type}, generating seed attacks")
            seed_attacks = self._generate_seed_attacks(cipher_type, ciphertext, max_attacks)
            self.stats["from_coverage_gaps"] += len(seed_attacks)
            self.log.info(f"Generated {len(seed_attacks)} gap-filling attacks")
            return seed_attacks

        # Find under-covered regions
        regions = cipher_data.get("regions", [])

        if not regions:
            # No regions tracked yet, generate seeds
            self.log.warning(f"No regions tracked for {cipher_type}, generating seed attacks")
            seed_attacks = self._generate_seed_attacks(cipher_type, ciphertext, max_attacks)
            self.stats["from_coverage_gaps"] += len(seed_attacks)
            self.log.info(f"Generated {len(seed_attacks)} gap-filling attacks")
            return seed_attacks
        for region_data in regions:
            coverage = region_data.get("coverage_percent", 0.0)
            region_key = region_data.get("region", "")

            if coverage < target_coverage * 100:
                # Generate attacks for this gap
                gap_attacks = self._generate_gap_filling_attacks(
                    cipher_type=cipher_type,
                    region_key=region_key,
                    current_coverage=coverage,
                    ciphertext=ciphertext,
                    max_attacks=20,
                )
                attacks.extend(gap_attacks)

        # Deduplicate
        attacks = self._deduplicate_attacks(attacks)
        attacks = sorted(attacks, key=lambda x: x.priority, reverse=True)

        self.stats["from_coverage_gaps"] += len(attacks)
        self.stats["generated"] += len(attacks)
        self.log.info(f"Generated {len(attacks)} gap-filling attacks")

        return attacks[:max_attacks]

    def generate_from_literature(
        self,
        paper_recommendations: list[dict[str, Any]],
        ciphertext: str,
        max_attacks: int = 30,
    ) -> list[AttackSpec]:
        """Generate attacks from literature recommendations.

        Args:
            paper_recommendations: List of paper analysis results from LiteratureGapAnalyzer
            ciphertext: Ciphertext for context
            max_attacks: Maximum attacks to generate

        Returns:
            List of attack specifications from literature
        """
        self.log.info(f"Generating attacks from {len(paper_recommendations)} literature recommendations")

        attacks = []

        for rec in paper_recommendations:
            # Extract attack parameters from paper recommendation
            lit_attacks = self._literature_to_attacks(rec, ciphertext)
            attacks.extend(lit_attacks)

        # Deduplicate and prioritize
        attacks = self._deduplicate_attacks(attacks)
        attacks = sorted(attacks, key=lambda x: x.priority, reverse=True)

        self.stats["from_literature"] += len(attacks)
        self.stats["generated"] += len(attacks)
        self.log.info(f"Generated {len(attacks)} literature-informed attacks")

        return attacks[:max_attacks]

    def generate_comprehensive_queue(
        self,
        ciphertext: str,
        cipher_types: list[str] | None = None,
        max_total: int = 200,
    ) -> list[AttackSpec]:
        """Generate comprehensive attack queue from all sources.

        Args:
            ciphertext: Ciphertext to attack
            cipher_types: Cipher types to consider (default: all known types)
            max_total: Maximum total attacks

        Returns:
            Prioritized, deduplicated attack queue
        """
        self.log.info("Generating comprehensive attack queue")

        cipher_types = cipher_types or ["vigenere", "transposition", "hill", "hybrid"]

        all_attacks = []

        # 1. Q-Research hints (highest priority)
        q_attacks = self.generate_from_q_hints(ciphertext, max_attacks=50)
        all_attacks.extend(q_attacks)

        # 2. Coverage gaps
        for cipher_type in cipher_types:
            gap_attacks = self.generate_from_coverage_gaps(
                cipher_type=cipher_type,
                ciphertext=ciphertext,
                target_coverage=0.8,
                max_attacks=30,
            )
            all_attacks.extend(gap_attacks)

        # 3. Literature recommendations (if available)
        # This would be integrated when LiteratureGapAnalyzer results are available
        # For now, we'll leave this as a placeholder

        # Final deduplication and prioritization
        all_attacks = self._deduplicate_attacks(all_attacks)
        all_attacks = sorted(all_attacks, key=lambda x: x.priority, reverse=True)

        self.stats["generated"] = len(all_attacks)
        self.log.info(f"Generated {len(all_attacks)} total attacks (deduplicated)")

        return all_attacks[:max_total]

    # ===== CONVERSION HELPERS =====

    def _vigenere_hints_to_attacks(
        self,
        metrics: VigenereMetrics,
        ciphertext: str,
    ) -> list[AttackSpec]:
        """Convert Vigenère metrics to attack specifications."""
        attacks = []

        for key_length in metrics.key_length_candidates[:5]:  # Top 5 candidates
            # Priority based on IC and confidence
            ic_value = metrics.ic_values.get(key_length, 0.0)
            priority = metrics.confidence * 0.6 + min(ic_value / 0.067, 1.0) * 0.4

            params = AttackParameters(
                cipher_type="vigenere",
                key_or_params={"key_length": key_length, "method": "kasiski"},
                additional_params={"ic_value": ic_value},
            )

            attacks.append(
                AttackSpec(
                    parameters=params,
                    priority=priority,
                    source="q_research",
                    rationale=f"Vigenère key length {key_length} from Kasiski/IC analysis (IC={ic_value:.4f})",
                    tags=["vigenere", "q_hint", f"key_len_{key_length}"],
                ),
            )

        return attacks

    def _transposition_hints_to_attacks(
        self,
        hints: list[TranspositionHint],
        ciphertext: str,
    ) -> list[AttackSpec]:
        """Convert transposition hints to attack specifications."""
        attacks = []

        for hint in hints[:10]:  # Top 10 hints
            params = AttackParameters(
                cipher_type="transposition",
                key_or_params={"method": hint.method, "period": hint.period},
                additional_params={"evidence": hint.evidence},
            )

            attacks.append(
                AttackSpec(
                    parameters=params,
                    priority=hint.confidence * 0.9,  # Slightly lower than Vigenère
                    source="q_research",
                    rationale=f"Transposition {hint.method} period {hint.period}: {hint.evidence}",
                    tags=["transposition", "q_hint", hint.method],
                ),
            )

        return attacks

    def _strategies_to_attacks(
        self,
        strategies: dict[str, Any],
        ciphertext: str,
    ) -> list[AttackSpec]:
        """Convert strategy suggestions to attack specifications."""
        attacks = []

        for category, details in strategies.items():
            priority = details.get("priority", 0.0)

            if priority < 0.3:  # Skip low-priority strategies
                continue

            methods = details.get("methods", [])

            for method in methods[:3]:  # Top 3 methods per category
                # Parse method string (e.g., "vigenere_k5" -> key_length=5)
                params = self._parse_strategy_method(category, method, ciphertext)

                if params:
                    # Determine primary cipher tag
                    cipher_tag = params.cipher_type
                    tags = [category, "strategy", method]
                    if cipher_tag not in tags:
                        tags.insert(0, cipher_tag)

                    attacks.append(
                        AttackSpec(
                            parameters=params,
                            priority=priority * 0.8,  # Slightly lower than specific hints
                            source="q_research",
                            rationale=f"Strategy suggestion: {category}/{method}",
                            tags=tags,
                        ),
                    )

        return attacks

    def _parse_strategy_method(
        self,
        category: str,
        method: str,
        ciphertext: str,
    ) -> AttackParameters | None:
        """Parse strategy method string into AttackParameters."""
        if category == "polyalphabetic" and method.startswith("vigenere_k"):
            # Extract key length
            try:
                key_length = int(method.split("_k")[1])
                return AttackParameters(
                    cipher_type="vigenere",
                    key_or_params={"key_length": key_length, "method": "strategy"},
                )
            except (IndexError, ValueError):
                return None

        elif category == "substitution":
            return AttackParameters(
                cipher_type="substitution",
                key_or_params={"method": method},
            )

        elif category == "transposition":
            return AttackParameters(
                cipher_type="transposition",
                key_or_params={"method": method, "period": 0},  # Period will be guessed
            )

        elif category == "hybrid":
            # Parse hybrid methods like "vigenere_then_transpose"
            parts = method.split("_then_")
            if len(parts) == 2:
                return AttackParameters(
                    cipher_type="hybrid",
                    key_or_params={"first": parts[0], "second": parts[1]},
                )

        return None

    def _generate_gap_filling_attacks(
        self,
        cipher_type: str,
        region_key: str,
        current_coverage: float,
        ciphertext: str,
        max_attacks: int = 20,
    ) -> list[AttackSpec]:
        """Generate attacks to fill coverage gap in a specific region."""
        attacks = []

        # Parse region key to extract parameter ranges
        # Region keys are like "key_length_5-10" or "period_8-16"
        params = self._parse_region_key(region_key)

        if not params:
            return attacks

        # Generate attacks across the parameter range
        # Priority inversely proportional to current coverage
        gap_priority = (100.0 - current_coverage) / 100.0

        if cipher_type == "vigenere":
            # Generate Vigenère attacks for key lengths in range
            key_min = params.get("key_min", 2)
            key_max = params.get("key_max", 20)

            for key_length in range(key_min, min(key_max + 1, key_min + max_attacks)):
                attack_params = AttackParameters(
                    cipher_type="vigenere",
                    key_or_params={"key_length": key_length, "method": "gap_filling"},
                )

                attacks.append(
                    AttackSpec(
                        parameters=attack_params,
                        priority=gap_priority * 0.7,  # Lower than Q-hints
                        source="coverage_gap",
                        rationale=f"Fill coverage gap in {region_key} (current: {current_coverage:.1f}%)",
                        tags=["vigenere", "gap_filling", region_key],
                    ),
                )

        elif cipher_type == "transposition":
            # Generate transposition attacks for periods in range
            period_min = params.get("period_min", 2)
            period_max = params.get("period_max", 50)

            for period in range(period_min, min(period_max + 1, period_min + max_attacks)):
                attack_params = AttackParameters(
                    cipher_type="transposition",
                    key_or_params={"method": "columnar", "period": period},
                )

                attacks.append(
                    AttackSpec(
                        parameters=attack_params,
                        priority=gap_priority * 0.65,
                        source="coverage_gap",
                        rationale=f"Fill coverage gap in {region_key} (current: {current_coverage:.1f}%)",
                        tags=["transposition", "gap_filling", region_key],
                    ),
                )

        return attacks

    def _parse_region_key(self, region_key: str) -> dict[str, Any]:
        """Parse region key into parameter dictionary."""
        # Example region keys:
        # "key_length_5-10" -> {"key_min": 5, "key_max": 10}
        # "period_8-16" -> {"period_min": 8, "period_max": 16}

        parts = region_key.split("_")

        if len(parts) < 2:
            return {}

        try:
            if "key_length" in region_key:
                range_str = parts[-1]
                if "-" in range_str:
                    min_val, max_val = map(int, range_str.split("-"))
                    return {"key_min": min_val, "key_max": max_val}

            elif "period" in region_key:
                range_str = parts[-1]
                if "-" in range_str:
                    min_val, max_val = map(int, range_str.split("-"))
                    return {"period_min": min_val, "period_max": max_val}

        except (ValueError, IndexError):
            return {}

        return {}

    def _generate_seed_attacks(
        self,
        cipher_type: str,
        ciphertext: str,
        max_attacks: int = 50,
    ) -> list[AttackSpec]:
        """Generate seed attacks when no coverage data exists."""
        attacks = []

        if cipher_type == "vigenere":
            # Standard Vigenère key lengths (2-20)
            for key_length in range(2, min(21, max_attacks + 2)):
                params = AttackParameters(
                    cipher_type="vigenere",
                    key_or_params={"key_length": key_length, "method": "seed"},
                )

                attacks.append(
                    AttackSpec(
                        parameters=params,
                        priority=0.5,  # Medium priority for seeds
                        source="coverage_gap",
                        rationale=f"Seed attack: Vigenère key length {key_length}",
                        tags=["vigenere", "seed"],
                    ),
                )

        elif cipher_type == "transposition":
            # Common transposition periods
            for period in range(2, min(51, max_attacks + 2)):
                params = AttackParameters(
                    cipher_type="transposition",
                    key_or_params={"method": "columnar", "period": period},
                )

                attacks.append(
                    AttackSpec(
                        parameters=params,
                        priority=0.5,
                        source="coverage_gap",
                        rationale=f"Seed attack: Transposition period {period}",
                        tags=["transposition", "seed"],
                    ),
                )

        return attacks[:max_attacks]

    def _literature_to_attacks(
        self,
        recommendation: dict[str, Any],
        ciphertext: str,
    ) -> list[AttackSpec]:
        """Convert literature recommendation to attack specifications."""
        attacks = []

        # Extract parameters from literature recommendation
        # This would integrate with LiteratureGapAnalyzer output format
        # For now, placeholder implementation

        cipher_type = recommendation.get("cipher_type", "unknown")
        params_dict = recommendation.get("parameters", {})
        confidence = recommendation.get("confidence", 0.5)
        paper_title = recommendation.get("paper_title", "Unknown paper")

        if cipher_type == "unknown":
            return attacks

        params = AttackParameters(
            cipher_type=cipher_type,
            key_or_params=params_dict,
            additional_params={"source_paper": paper_title},
        )

        attacks.append(
            AttackSpec(
                parameters=params,
                priority=confidence * 0.85,  # High priority for literature
                source="literature",
                rationale=f"From paper: {paper_title}",
                tags=["literature", cipher_type, "paper"],
            ),
        )

        return attacks

    # ===== DEDUPLICATION =====

    def _deduplicate_attacks(self, attacks: list[AttackSpec]) -> list[AttackSpec]:
        """Deduplicate attacks using fingerprints and AttackLogger."""
        unique_attacks = []
        seen_fingerprints = set()

        for attack in attacks:
            fingerprint = attack.fingerprint()

            # Check if we've already seen this in the current batch
            if fingerprint in seen_fingerprints:
                self.stats["duplicates_filtered"] += 1
                continue

            # Check if it's been executed before (via AttackLogger)
            if self.attack_logger.is_duplicate(attack.parameters):
                self.stats["duplicates_filtered"] += 1
                self.log.debug(f"Skipping duplicate attack: {attack.rationale}")
                continue

            # New attack
            seen_fingerprints.add(fingerprint)
            unique_attacks.append(attack)

        return unique_attacks

    def get_statistics(self) -> dict[str, Any]:
        """Get generation statistics.

        Returns:
            Dictionary with generation stats
        """
        return {
            **self.stats,
            "deduplication_rate": (
                self.stats["duplicates_filtered"] / max(self.stats["generated"], 1)
                if self.stats["generated"] > 0
                else 0.0
            ),
        }

    def export_queue(self, attacks: list[AttackSpec], output_path: Path) -> None:
        """Export attack queue to JSON for review/audit.

        Args:
            attacks: Attack specifications to export
            output_path: Path to output file
        """
        output_data = {
            "generated_at": str(Path(__file__).parent),
            "total_attacks": len(attacks),
            "statistics": self.get_statistics(),
            "attacks": [
                {
                    "priority": a.priority,
                    "source": a.source,
                    "rationale": a.rationale,
                    "tags": a.tags,
                    "parameters": a.parameters.to_dict(),
                    "fingerprint": a.fingerprint(),
                }
                for a in attacks
            ],
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        self.log.info(f"Exported {len(attacks)} attacks to {output_path}")
