"""Search space tracking for coverage analysis.

Tracks which portions of key spaces have been explored, enabling coverage
metrics like "% of Vigenère key length 1-20 explored".

Philosophy: "You can't optimize what you don't measure. Show us the map
of explored vs unexplored territory."
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class KeySpaceRegion:
    """A region of key space (e.g., "Vigenère length 8, keys starting with A")."""

    cipher_type: str
    parameters: dict[str, Any]
    total_size: int  # Total number of possible keys
    explored_count: int = 0  # How many keys tried
    successful_count: int = 0  # How many yielded candidates

    @property
    def coverage_percent(self) -> float:
        """Calculate coverage percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.explored_count / self.total_size) * 100

    @property
    def success_rate(self) -> float:
        """Calculate success rate within explored keys."""
        if self.explored_count == 0:
            return 0.0
        return (self.successful_count / self.explored_count) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cipher_type": self.cipher_type,
            "parameters": self.parameters,
            "total_size": self.total_size,
            "explored_count": self.explored_count,
            "successful_count": self.successful_count,
            "coverage_percent": self.coverage_percent,
            "success_rate": self.success_rate,
        }


class SearchSpaceTracker:
    """Track coverage of cryptographic key spaces.

    Provides coverage metrics like:
    - "Vigenère key length 1-20: 67% explored"
    - "Hill 2x2 matrices: 23% explored"
    - "Transposition period 1-30: 89% explored"
    """

    def __init__(self, cache_dir: Path | None = None):
        """Initialize search space tracker.

        Args:
            cache_dir: Directory for caching coverage data
        """
        self.cache_dir = cache_dir or Path("./data/search_space")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track regions: cipher_type -> region_key -> KeySpaceRegion
        self.regions: dict[str, dict[str, KeySpaceRegion]] = defaultdict(dict)

        # Load existing data
        self._load_cache()

    def register_region(
        self,
        cipher_type: str,
        region_key: str,
        parameters: dict[str, Any],
        total_size: int,
    ):
        """Register a key space region for tracking.

        Args:
            cipher_type: Type of cipher (e.g., "vigenere")
            region_key: Unique identifier for region (e.g., "length_8")
            parameters: Region parameters
            total_size: Total number of keys in this region
        """
        if region_key not in self.regions[cipher_type]:
            self.regions[cipher_type][region_key] = KeySpaceRegion(
                cipher_type=cipher_type,
                parameters=parameters,
                total_size=total_size,
            )
            self._save_cache()

    def record_exploration(
        self,
        cipher_type: str,
        region_key: str,
        count: int = 1,
        successful: int = 0,
    ):
        """Record keys explored in a region.

        Args:
            cipher_type: Type of cipher
            region_key: Region identifier
            count: Number of keys explored
            successful: Number that yielded candidates
        """
        if region_key not in self.regions[cipher_type]:
            # Auto-register with unknown size
            self.register_region(cipher_type, region_key, {}, total_size=0)

        region = self.regions[cipher_type][region_key]
        region.explored_count += count
        region.successful_count += successful

        # Save cache after updates
        self._save_cache()

    def get_coverage(self, cipher_type: str, region_key: str | None = None) -> float:
        """Get coverage percentage for a cipher type or specific region.

        Args:
            cipher_type: Type of cipher
            region_key: Optional specific region

        Returns:
            Coverage percentage (0-100)
        """
        if cipher_type not in self.regions:
            return 0.0

        if region_key:
            region = self.regions[cipher_type].get(region_key)
            return region.coverage_percent if region else 0.0

        # Aggregate across all regions
        total_space = sum(r.total_size for r in self.regions[cipher_type].values())
        total_explored = sum(r.explored_count for r in self.regions[cipher_type].values())

        if total_space == 0:
            return 0.0
        return (total_explored / total_space) * 100

    def get_coverage_report(self, cipher_type: str | None = None) -> dict[str, Any]:
        """Generate coverage report.

        Args:
            cipher_type: Optional filter by cipher type

        Returns:
            Coverage report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "cipher_types": {},
        }

        cipher_types = [cipher_type] if cipher_type else list(self.regions.keys())

        for ct in cipher_types:
            if ct not in self.regions:
                continue

            regions_data = []
            total_explored = 0
            total_size = 0

            for region_key, region in self.regions[ct].items():
                regions_data.append(
                    {
                        "region": region_key,
                        **region.to_dict(),
                    },
                )
                total_explored += region.explored_count
                total_size += region.total_size

            overall_coverage = (total_explored / total_size * 100) if total_size > 0 else 0.0

            report["cipher_types"][ct] = {
                "overall_coverage": overall_coverage,
                "total_explored": total_explored,
                "total_size": total_size,
                "regions": regions_data,
            }

        return report

    def identify_gaps(self, cipher_type: str, min_coverage: float = 50.0) -> list[KeySpaceRegion]:
        """Identify under-explored regions (gaps in coverage).

        Args:
            cipher_type: Type of cipher
            min_coverage: Minimum coverage to not be considered a gap

        Returns:
            List of under-explored regions
        """
        if cipher_type not in self.regions:
            return []

        gaps = []
        for region in self.regions[cipher_type].values():
            if region.coverage_percent < min_coverage:
                gaps.append(region)

        # Sort by coverage (least explored first)
        gaps.sort(key=lambda r: r.coverage_percent)
        return gaps

    def get_recommendations(self, top_n: int = 5) -> list[dict[str, Any]]:
        """Get recommendations for next attack targets.

        Prioritizes:
        - Under-explored regions
        - Regions with some success
        - Cipher types with low overall coverage

        Args:
            top_n: Number of recommendations

        Returns:
            List of recommended attack targets
        """
        recommendations = []

        for cipher_type, regions in self.regions.items():
            for region_key, region in regions.items():
                # Score based on: low coverage + some success + reasonable size
                coverage_score = 100 - region.coverage_percent  # Higher = less explored
                success_score = region.success_rate * 0.5  # Bonus for past success
                size_score = min(region.total_size / 10000, 100)  # Prefer manageable sizes

                total_score = coverage_score + success_score + size_score

                recommendations.append(
                    {
                        "cipher_type": cipher_type,
                        "region": region_key,
                        "parameters": region.parameters,
                        "coverage": region.coverage_percent,
                        "success_rate": region.success_rate,
                        "priority_score": total_score,
                        "reason": self._explain_recommendation(region),
                    },
                )

        # Sort by priority score
        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        return recommendations[:top_n]

    def export_heatmap_data(self, cipher_type: str) -> dict[str, Any]:
        """Export data for heatmap visualization.

        Args:
            cipher_type: Type of cipher

        Returns:
            Data structure for visualization
        """
        if cipher_type not in self.regions:
            return {}

        heatmap = {
            "cipher_type": cipher_type,
            "regions": [],
        }

        for region_key, region in self.regions[cipher_type].items():
            heatmap["regions"].append(
                {
                    "name": region_key,
                    "coverage": region.coverage_percent,
                    "explored": region.explored_count,
                    "total": region.total_size,
                    "color": self._coverage_to_color(region.coverage_percent),
                },
            )

        return heatmap

    def _coverage_to_color(self, coverage: float) -> str:
        """Map coverage percentage to color for heatmap."""
        if coverage >= 90:
            return "#2ecc71"  # Green (well explored)
        elif coverage >= 50:
            return "#f39c12"  # Orange (partially explored)
        elif coverage >= 10:
            return "#e74c3c"  # Red (barely explored)
        else:
            return "#95a5a6"  # Gray (untouched)

    def _explain_recommendation(self, region: KeySpaceRegion) -> str:
        """Generate human-readable explanation for recommendation."""
        if region.coverage_percent < 10:
            return f"Unexplored territory ({region.coverage_percent:.1f}% coverage)"
        elif region.success_rate > 1.0:
            return f"Promising area (success rate: {region.success_rate:.1f}%)"
        elif region.coverage_percent < 50:
            return f"Partially explored ({region.coverage_percent:.1f}% coverage)"
        else:
            return f"Filling gaps ({region.coverage_percent:.1f}% coverage)"

    def _load_cache(self):
        """Load cached coverage data."""
        cache_file = self.cache_dir / "search_space.json"
        if not cache_file.exists():
            return

        try:
            with open(cache_file, encoding="utf-8") as f:
                data = json.load(f)

            for cipher_type, regions_data in data.items():
                for region_key, region_dict in regions_data.items():
                    self.regions[cipher_type][region_key] = KeySpaceRegion(**region_dict)
        except (json.JSONDecodeError, KeyError, TypeError):
            # Start fresh if cache corrupted
            pass

    def _save_cache(self):
        """Save coverage data to cache."""
        cache_file = self.cache_dir / "search_space.json"

        data = {}
        for cipher_type, regions in self.regions.items():
            data[cipher_type] = {
                region_key: {
                    "cipher_type": region.cipher_type,
                    "parameters": region.parameters,
                    "total_size": region.total_size,
                    "explored_count": region.explored_count,
                    "successful_count": region.successful_count,
                }
                for region_key, region in regions.items()
            }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def demo_search_space_tracker():
    """Demonstrate search space tracker."""
    print("=" * 80)
    print("SEARCH SPACE TRACKER DEMO")
    print("=" * 80)
    print()

    tracker = SearchSpaceTracker()

    # Register some key space regions
    for length in range(1, 21):
        # Vigenère key length N has 26^N possible keys
        total_keys = 26**length if length <= 6 else 10000000  # Cap for demo
        tracker.register_region(
            cipher_type="vigenere",
            region_key=f"length_{length}",
            parameters={"key_length": length},
            total_size=total_keys,
        )

    # Simulate some exploration
    tracker.record_exploration("vigenere", "length_5", count=1000, successful=15)
    tracker.record_exploration("vigenere", "length_8", count=5000, successful=42)
    tracker.record_exploration("vigenere", "length_14", count=200, successful=1)

    # Get coverage
    print("Coverage Report:")
    report = tracker.get_coverage_report("vigenere")
    print(f"Overall coverage: {report['cipher_types']['vigenere']['overall_coverage']:.4f}%")
    print()

    print("Regions:")
    for region in report['cipher_types']['vigenere']['regions'][:10]:
        print(
            f"({region['region']}: {region['coverage_percent']:.4f}%)\n"
            f"({region['explored_count']}/{region['total_size']})",
        )
    print()

    # Get recommendations
    print("Recommendations:")
    recs = tracker.get_recommendations(top_n=5)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['cipher_type']} {rec['region']}: {rec['reason']}")


if __name__ == "__main__":
    demo_search_space_tracker()
