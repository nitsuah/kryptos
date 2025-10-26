"""Strategic coverage analysis and visualization.

Integrates coverage tracking with strategic decision-making:
1. Generate heatmap visualizations of key space coverage
2. Provide OPS Director with data-driven recommendations
3. Detect saturation points for strategic pivoting
4. Time-series analysis of coverage progress
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from kryptos.paths import get_artifacts_root
from kryptos.provenance.search_space import SearchSpaceTracker


@dataclass
class CoverageTrend:
    """Time-series data point for coverage tracking."""

    timestamp: datetime
    cipher_type: str
    region_key: str
    coverage_percent: float
    explored_count: int
    successful_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SaturationAnalysis:
    """Analysis of whether a region is saturated."""

    cipher_type: str
    region_key: str
    is_saturated: bool
    coverage_percent: float
    exploration_rate: float  # Keys/hour or similar
    estimated_completion_hours: float | None
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class StrategicCoverageAnalyzer:
    """Analyze coverage strategically for OPS Director integration."""

    def __init__(
        self,
        tracker: SearchSpaceTracker | None = None,
        history_dir: Path | None = None,
    ):
        """Initialize strategic analyzer.

        Args:
            tracker: Search space tracker
            history_dir: Directory for storing coverage history
        """
        self.tracker = tracker or SearchSpaceTracker()
        self.history_dir = history_dir or (get_artifacts_root() / "coverage_history")
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self.coverage_history: list[CoverageTrend] = []
        self._load_history()

    def record_coverage_snapshot(self):
        """Record current coverage state for time-series analysis."""
        timestamp = datetime.now()

        for cipher_type, regions in self.tracker.regions.items():
            for region_key, region in regions.items():
                trend = CoverageTrend(
                    timestamp=timestamp,
                    cipher_type=cipher_type,
                    region_key=region_key,
                    coverage_percent=region.coverage_percent,
                    explored_count=region.explored_count,
                    successful_count=region.successful_count,
                )
                self.coverage_history.append(trend)

        self._save_history()

    def analyze_saturation(
        self,
        cipher_type: str,
        saturation_threshold: float = 80.0,
        min_samples: int = 3,
    ) -> list[SaturationAnalysis]:
        """Analyze which regions are saturated and recommend pivoting.

        Args:
            cipher_type: Cipher type to analyze
            saturation_threshold: Coverage % to consider saturated
            min_samples: Minimum historical samples for rate calculation

        Returns:
            List of saturation analyses
        """
        if cipher_type not in self.tracker.regions:
            return []

        analyses = []

        for region_key, region in self.tracker.regions[cipher_type].items():
            # Get historical data for this region
            region_history = [
                t for t in self.coverage_history if t.cipher_type == cipher_type and t.region_key == region_key
            ]

            # Calculate exploration rate
            exploration_rate = 0.0
            if len(region_history) >= min_samples:
                first = region_history[-min_samples]
                last = region_history[-1]
                time_diff = (last.timestamp - first.timestamp).total_seconds() / 3600
                if time_diff > 0:
                    explored_diff = last.explored_count - first.explored_count
                    exploration_rate = explored_diff / time_diff

            # Estimate completion time
            estimated_hours = None
            if exploration_rate > 0 and region.total_size > 0:
                remaining = region.total_size - region.explored_count
                estimated_hours = remaining / exploration_rate

            # Determine saturation status
            is_saturated = region.coverage_percent >= saturation_threshold

            # Generate recommendation
            if is_saturated:
                recommendation = (
                    f"PIVOT: Region {saturation_threshold}%+ explored. "
                    f"Consider moving to under-explored regions or hybrid attacks."
                )
            elif exploration_rate > 0 and estimated_hours and estimated_hours < 24:
                recommendation = f"CONTINUE: ~{estimated_hours:.1f}h to completion at current rate."
            elif region.success_rate > 10.0:
                recommendation = (
                    f"INTENSIFY: {region.success_rate:.1f}% success rate suggests "
                    f"promising region. Increase resources."
                )
            else:
                recommendation = f"EXPLORE: Low coverage ({region.coverage_percent:.2f}%). " f"Continue exploration."

            analysis = SaturationAnalysis(
                cipher_type=cipher_type,
                region_key=region_key,
                is_saturated=is_saturated,
                coverage_percent=region.coverage_percent,
                exploration_rate=exploration_rate,
                estimated_completion_hours=estimated_hours,
                recommendation=recommendation,
            )
            analyses.append(analysis)

        return analyses

    def generate_heatmap_visualization(
        self,
        cipher_type: str,
        output_format: str = "json",
    ) -> dict[str, Any] | str:
        """Generate heatmap data for visualization.

        Args:
            cipher_type: Cipher type
            output_format: "json" or "html"

        Returns:
            Heatmap data or HTML
        """
        heatmap_data = self.tracker.export_heatmap_data(cipher_type)

        if output_format == "json":
            return heatmap_data

        elif output_format == "html":
            return self._generate_html_heatmap(heatmap_data)

        return heatmap_data

    def get_ops_recommendations(
        self,
        top_n: int = 5,
        min_coverage: float = 90.0,
    ) -> list[dict[str, Any]]:
        """Generate strategic recommendations for OPS Director.

        Args:
            top_n: Number of recommendations
            min_coverage: Saturation threshold

        Returns:
            Prioritized recommendations
        """
        recommendations = []

        for cipher_type in self.tracker.regions.keys():
            # Analyze saturation
            saturations = self.analyze_saturation(cipher_type, min_coverage)

            # Find saturated regions (need to pivot away)
            saturated = [s for s in saturations if s.is_saturated]

            # Find promising regions (high success rate)
            promising = [
                s
                for s in saturations
                if not s.is_saturated and self.tracker.regions[cipher_type][s.region_key].success_rate > 5.0
            ]

            # Find unexplored regions
            unexplored = [s for s in saturations if s.coverage_percent < 10.0]

            # Generate recommendations
            if saturated:
                recommendations.append(
                    {
                        "priority": 1,
                        "action": "PIVOT_AWAY",
                        "cipher_type": cipher_type,
                        "regions": [s.region_key for s in saturated],
                        "reason": f"{len(saturated)} regions saturated (>{min_coverage}%)",
                        "suggestion": "Shift resources to hybrid attacks or different cipher types",
                    },
                )

            if promising:
                recommendations.append(
                    {
                        "priority": 2,
                        "action": "INTENSIFY",
                        "cipher_type": cipher_type,
                        "regions": [s.region_key for s in promising],
                        "reason": f"{len(promising)} regions with >5% success rate",
                        "suggestion": "Allocate more resources to promising regions",
                    },
                )

            if unexplored:
                recommendations.append(
                    {
                        "priority": 3,
                        "action": "EXPLORE",
                        "cipher_type": cipher_type,
                        "regions": [s.region_key for s in unexplored[:3]],
                        "reason": f"{len(unexplored)} regions <10% explored",
                        "suggestion": "Begin systematic exploration",
                    },
                )

        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        return recommendations[:top_n]

    def generate_coverage_report_for_ops(self) -> dict[str, Any]:
        """Generate comprehensive report for OPS Director.

        Returns:
            Strategic coverage report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": {},
            "saturation_analysis": {},
            "recommendations": self.get_ops_recommendations(top_n=10),
            "trends": self._analyze_trends(),
        }

        # Overall status per cipher type
        for cipher_type in self.tracker.regions.keys():
            coverage = self.tracker.get_coverage(cipher_type)
            total_regions = len(self.tracker.regions[cipher_type])
            saturated = len([r for r in self.tracker.regions[cipher_type].values() if r.coverage_percent >= 80.0])

            report["overall_status"][cipher_type] = {
                "coverage_percent": coverage,
                "total_regions": total_regions,
                "saturated_regions": saturated,
                "saturation_rate": saturated / total_regions * 100 if total_regions else 0,
            }

            # Saturation analysis
            report["saturation_analysis"][cipher_type] = [s.to_dict() for s in self.analyze_saturation(cipher_type)]

        return report

    def _analyze_trends(self) -> dict[str, Any]:
        """Analyze coverage trends over time."""
        if len(self.coverage_history) < 2:
            return {"status": "insufficient_data"}

        # Group by cipher type
        trends = {}
        for cipher_type in self.tracker.regions.keys():
            cipher_history = [t for t in self.coverage_history if t.cipher_type == cipher_type]

            if len(cipher_history) < 2:
                continue

            first = cipher_history[0]
            last = cipher_history[-1]

            time_span_hours = (last.timestamp - first.timestamp).total_seconds() / 3600

            trends[cipher_type] = {
                "coverage_increase": last.coverage_percent - first.coverage_percent,
                "time_span_hours": time_span_hours,
                "average_rate": (
                    (last.explored_count - first.explored_count) / time_span_hours if time_span_hours > 0 else 0
                ),
            }

        return trends

    def _generate_html_heatmap(self, heatmap_data: dict[str, Any]) -> str:
        """Generate HTML heatmap visualization."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Heatmap - {cipher_type}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .heatmap {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }}
        .region {{ padding: 20px; border-radius: 5px; text-align: center; }}
        .region-name {{ font-weight: bold; margin-bottom: 10px; }}
        .region-stats {{ font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Coverage Heatmap: {cipher_type}</h1>
    <div class="heatmap">
""".format(cipher_type=heatmap_data.get("cipher_type", "Unknown"))

        for region in heatmap_data.get("regions", []):
            html += """
        <div class="region" style="background-color: {color};">
            <div class="region-name">{name}</div>
            <div class="region-stats">
                Coverage: {coverage:.2f}%<br>
                Explored: {explored:,}<br>
                Total: {total:,}
            </div>
        </div>
""".format(
                color=region["color"],
                name=region["name"],
                coverage=region["coverage"],
                explored=region["explored"],
                total=region["total"],
            )

        html += """
    </div>
</body>
</html>
"""
        return html

    def _load_history(self):
        """Load coverage history from disk."""
        history_file = self.history_dir / "coverage_history.json"
        if not history_file.exists():
            return

        try:
            with open(history_file, encoding="utf-8") as f:
                data = json.load(f)
                self.coverage_history = [
                    CoverageTrend(
                        timestamp=datetime.fromisoformat(t["timestamp"]),
                        cipher_type=t["cipher_type"],
                        region_key=t["region_key"],
                        coverage_percent=t["coverage_percent"],
                        explored_count=t["explored_count"],
                        successful_count=t["successful_count"],
                    )
                    for t in data
                ]
        except (json.JSONDecodeError, KeyError, ValueError):
            self.coverage_history = []

    def _save_history(self):
        """Save coverage history to disk."""
        history_file = self.history_dir / "coverage_history.json"
        data = [t.to_dict() for t in self.coverage_history]
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def demo_strategic_coverage():
    """Demonstrate strategic coverage analysis."""
    print("=" * 80)
    print("STRATEGIC COVERAGE ANALYSIS DEMO")
    print("=" * 80)
    print()

    from kryptos.provenance.search_space import SearchSpaceTracker

    tracker = SearchSpaceTracker()
    analyzer = StrategicCoverageAnalyzer(tracker=tracker)

    # Set up some regions
    for length in range(1, 11):
        tracker.register_region(
            "vigenere",
            f"length_{length}",
            {"key_length": length},
            min(26**length, 1000000),
        )

    # Simulate exploration
    tracker.record_exploration("vigenere", "length_3", count=15000, successful=100)
    tracker.record_exploration("vigenere", "length_5", count=8000, successful=40)
    tracker.record_exploration("vigenere", "length_8", count=1000, successful=2)

    # Record snapshot
    analyzer.record_coverage_snapshot()

    print("-" * 80)
    print("1. Saturation Analysis")
    print("-" * 80)

    saturations = analyzer.analyze_saturation("vigenere", saturation_threshold=50.0)
    for sat in saturations[:5]:
        print(f"{sat.region_key}:")
        print(f"  Coverage: {sat.coverage_percent:.2f}%")
        print(f"  Saturated: {sat.is_saturated}")
        print(f"  {sat.recommendation}")
        print()

    print("-" * 80)
    print("2. OPS Director Recommendations")
    print("-" * 80)

    recommendations = analyzer.get_ops_recommendations(top_n=5, min_coverage=70.0)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['action']} - {rec['cipher_type']}")
        print(f"   Regions: {', '.join(rec['regions'][:3])}")
        print(f"   Reason: {rec['reason']}")
        print(f"   → {rec['suggestion']}")
        print()

    print("-" * 80)
    print("3. Generate Heatmap")
    print("-" * 80)

    heatmap = analyzer.generate_heatmap_visualization("vigenere")
    print(f"Generated heatmap with {len(heatmap['regions'])} regions")
    print("\nSample regions:")
    for region in heatmap["regions"][:3]:
        print(f"  - {region['name']}: {region['coverage']:.2f}% ({region['color']})")
    print()

    print("=" * 80)
    print("SPRINT 4.3: Strategic Coverage Analysis Complete ✓")
    print("=" * 80)


if __name__ == "__main__":
    demo_strategic_coverage()
