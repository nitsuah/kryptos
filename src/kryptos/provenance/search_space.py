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

from kryptos.paths import get_artifacts_root


@dataclass
class KeySpaceRegion:
    cipher_type: str
    parameters: dict[str, Any]
    total_size: int
    explored_count: int = 0
    successful_count: int = 0

    @property
    def coverage_percent(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.explored_count / self.total_size) * 100

    @property
    def success_rate(self) -> float:
        if self.explored_count == 0:
            return 0.0
        return (self.successful_count / self.explored_count) * 100

    def to_dict(self) -> dict[str, Any]:
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
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or (get_artifacts_root() / "search_space")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.regions: dict[str, dict[str, KeySpaceRegion]] = defaultdict(dict)

        self._tried_keys: dict[str, set[str]] = defaultdict(set)

        self._tried_keys_file = self.cache_dir / "tried_keys.jsonl"

        self._load_cache()
        self._load_tried_keys()

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
        keys: list[str] | None = None,
    ):
        """Record keys explored in a region.

        Args:
            cipher_type: Type of cipher
            region_key: Region identifier
            count: Number of keys explored
            successful: Number that yielded candidates
            keys: Optional list of actual key strings tried
        """
        if region_key not in self.regions[cipher_type]:
            self.register_region(cipher_type, region_key, {}, total_size=0)

        region = self.regions[cipher_type][region_key]
        region.explored_count += count
        region.successful_count += successful

        if keys:
            self._record_tried_keys(cipher_type, keys)

        self._save_cache()

    def already_tried(self, cipher_type: str, key: str) -> bool:
        return key in self._tried_keys[cipher_type]

    def mark_tried(self, cipher_type: str, key: str):
        if key not in self._tried_keys[cipher_type]:
            self._tried_keys[cipher_type].add(key)
            self._append_tried_key(cipher_type, key)

    def get_coverage(self, cipher_type: str, region_key: str | None = None) -> float:
        if cipher_type not in self.regions:
            return 0.0

        if region_key:
            region = self.regions[cipher_type].get(region_key)
            return region.coverage_percent if region else 0.0

        total_space = sum(r.total_size for r in self.regions[cipher_type].values())
        total_explored = sum(r.explored_count for r in self.regions[cipher_type].values())

        if total_space == 0:
            return 0.0
        return (total_explored / total_space) * 100

    def get_coverage_report(self, cipher_type: str | None = None) -> dict[str, Any]:
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
        if cipher_type not in self.regions:
            return []

        gaps = []
        for region in self.regions[cipher_type].values():
            if region.coverage_percent < min_coverage:
                gaps.append(region)

        gaps.sort(key=lambda r: r.coverage_percent)
        return gaps

    def get_recommendations(self, top_n: int = 5) -> list[dict[str, Any]]:
        recommendations = []

        for cipher_type, regions in self.regions.items():
            for region_key, region in regions.items():
                coverage_score = 100 - region.coverage_percent
                success_score = region.success_rate * 0.5
                size_score = min(region.total_size / 10000, 100)

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

        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        return recommendations[:top_n]

    def export_heatmap_data(self, cipher_type: str) -> dict[str, Any]:
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
        if coverage >= 90:
            return "#2ecc71"  # Green (well explored)
        elif coverage >= 50:
            return "#f39c12"  # Orange (partially explored)
        elif coverage >= 10:
            return "#e74c3c"  # Red (barely explored)
        else:
            return "#95a5a6"  # Gray (untouched)

    def _explain_recommendation(self, region: KeySpaceRegion) -> str:
        if region.coverage_percent < 10:
            return f"Unexplored territory ({region.coverage_percent:.1f}% coverage)"
        elif region.success_rate > 1.0:
            return f"Promising area (success rate: {region.success_rate:.1f}%)"
        elif region.coverage_percent < 50:
            return f"Partially explored ({region.coverage_percent:.1f}% coverage)"
        else:
            return f"Filling gaps ({region.coverage_percent:.1f}% coverage)"

    def _load_cache(self):
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
            pass

    def _save_cache(self):
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

    def _load_tried_keys(self):
        if not self._tried_keys_file.exists():
            return

        try:
            with open(self._tried_keys_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    cipher_type = record["cipher_type"]
                    key = record["key"]
                    self._tried_keys[cipher_type].add(key)
        except (json.JSONDecodeError, KeyError, TypeError, OSError):
            pass

    def _record_tried_keys(self, cipher_type: str, keys: list[str]):
        new_keys = []
        for key in keys:
            if key not in self._tried_keys[cipher_type]:
                self._tried_keys[cipher_type].add(key)
                new_keys.append(key)

        if new_keys:
            with open(self._tried_keys_file, "a", encoding="utf-8") as f:
                for key in new_keys:
                    record = {"cipher_type": cipher_type, "key": key}
                    f.write(json.dumps(record) + "\n")

    def _append_tried_key(self, cipher_type: str, key: str):
        record = {"cipher_type": cipher_type, "key": key}
        with open(self._tried_keys_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def demo_search_space_tracker():
    print("=" * 80)
    print("SEARCH SPACE TRACKER DEMO")
    print("=" * 80)
    print()

    tracker = SearchSpaceTracker()

    for length in range(1, 21):
        total_keys = 26**length if length <= 6 else 10000000
        tracker.register_region(
            cipher_type="vigenere",
            region_key=f"length_{length}",
            parameters={"key_length": length},
            total_size=total_keys,
        )

    tracker.record_exploration("vigenere", "length_5", count=1000, successful=15)
    tracker.record_exploration("vigenere", "length_8", count=5000, successful=42)
    tracker.record_exploration("vigenere", "length_14", count=200, successful=1)

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

    print("Recommendations:")
    recs = tracker.get_recommendations(top_n=5)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['cipher_type']} {rec['region']}: {rec['reason']}")


if __name__ == "__main__":
    demo_search_space_tracker()
