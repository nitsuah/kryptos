"""Tests for search space coverage tracking."""

from __future__ import annotations

from kryptos.provenance.search_space import (
    KeySpaceRegion,
    SearchSpaceTracker,
)


class TestKeySpaceRegion:
    """Test key space regions."""

    def test_create_region(self):
        """Test creating a key space region."""
        region = KeySpaceRegion(
            cipher_type="vigenere",
            parameters={"key_length": 8},
            total_size=26**8,
        )

        assert region.cipher_type == "vigenere"
        assert region.total_size == 26**8
        assert region.explored_count == 0

    def test_coverage_percent(self):
        """Test coverage percentage calculation."""
        region = KeySpaceRegion(
            cipher_type="vigenere",
            parameters={"key_length": 5},
            total_size=1000,
            explored_count=250,
        )

        assert region.coverage_percent == 25.0

    def test_success_rate(self):
        """Test success rate calculation."""
        region = KeySpaceRegion(
            cipher_type="vigenere",
            parameters={"key_length": 5},
            total_size=1000,
            explored_count=100,
            successful_count=10,
        )

        assert region.success_rate == 10.0

    def test_zero_explored(self):
        """Test metrics with zero explored."""
        region = KeySpaceRegion(
            cipher_type="vigenere",
            parameters={"key_length": 5},
            total_size=1000,
        )

        assert region.coverage_percent == 0.0
        assert region.success_rate == 0.0

    def test_to_dict(self):
        """Test converting region to dictionary."""
        region = KeySpaceRegion(
            cipher_type="vigenere",
            parameters={"key_length": 5},
            total_size=1000,
            explored_count=100,
        )

        d = region.to_dict()
        assert d["cipher_type"] == "vigenere"
        assert d["total_size"] == 1000
        assert d["coverage_percent"] == 10.0


class TestSearchSpaceTracker:
    """Test search space tracker."""

    def test_initialization(self, tmp_path):
        """Test tracker initialization."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        assert tracker.cache_dir == tmp_path
        assert len(tracker.regions) == 0

    def test_register_region(self, tmp_path):
        """Test registering a key space region."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region(
            cipher_type="vigenere",
            region_key="length_8",
            parameters={"key_length": 8},
            total_size=26**8,
        )

        assert "vigenere" in tracker.regions
        assert "length_8" in tracker.regions["vigenere"]

    def test_record_exploration(self, tmp_path):
        """Test recording exploration."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region(
            cipher_type="vigenere",
            region_key="length_5",
            parameters={"key_length": 5},
            total_size=1000,
        )

        tracker.record_exploration("vigenere", "length_5", count=100, successful=5)

        region = tracker.regions["vigenere"]["length_5"]
        assert region.explored_count == 100
        assert region.successful_count == 5

    def test_auto_register_on_record(self, tmp_path):
        """Test auto-registration when recording."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # Record without registering first
        tracker.record_exploration("vigenere", "length_10", count=50)

        assert "vigenere" in tracker.regions
        assert "length_10" in tracker.regions["vigenere"]

    def test_get_coverage_specific_region(self, tmp_path):
        """Test getting coverage for specific region."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {"key_length": 5}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=250)

        coverage = tracker.get_coverage("vigenere", "length_5")
        assert coverage == 25.0

    def test_get_coverage_aggregate(self, tmp_path):
        """Test aggregate coverage across all regions."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.register_region("vigenere", "length_8", {}, 2000)

        tracker.record_exploration("vigenere", "length_5", count=500)  # 50%
        tracker.record_exploration("vigenere", "length_8", count=500)  # 25%

        # Overall: 1000 explored / 3000 total = 33.33%
        coverage = tracker.get_coverage("vigenere")
        assert 33.0 < coverage < 34.0

    def test_get_coverage_report(self, tmp_path):
        """Test generating coverage report."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {"key_length": 5}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=250, successful=10)

        report = tracker.get_coverage_report("vigenere")

        assert "cipher_types" in report
        assert "vigenere" in report["cipher_types"]
        assert report["cipher_types"]["vigenere"]["total_explored"] == 250

    def test_identify_gaps(self, tmp_path):
        """Test identifying under-explored regions."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # Well explored
        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=800)

        # Under explored
        tracker.register_region("vigenere", "length_8", {}, 1000)
        tracker.record_exploration("vigenere", "length_8", count=100)

        gaps = tracker.identify_gaps("vigenere", min_coverage=50.0)

        assert len(gaps) == 1
        assert gaps[0].parameters.get("key_length") != 5  # Should be length_8

    def test_gaps_sorted_by_coverage(self, tmp_path):
        """Test gaps are sorted by coverage (least first)."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=300)  # 30%

        tracker.register_region("vigenere", "length_8", {}, 1000)
        tracker.record_exploration("vigenere", "length_8", count=100)  # 10%

        gaps = tracker.identify_gaps("vigenere", min_coverage=50.0)

        # Should be sorted: length_8 (10%) before length_5 (30%)
        assert gaps[0].coverage_percent < gaps[1].coverage_percent

    def test_get_recommendations(self, tmp_path):
        """Test getting attack recommendations."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # Create some regions
        for length in [5, 8, 12]:
            tracker.register_region(
                "vigenere",
                f"length_{length}",
                {"key_length": length},
                1000,
            )
            tracker.record_exploration(
                "vigenere",
                f"length_{length}",
                count=100 * length,
                successful=length,
            )

        recommendations = tracker.get_recommendations(top_n=3)

        assert len(recommendations) <= 3
        assert all("cipher_type" in rec for rec in recommendations)
        assert all("priority_score" in rec for rec in recommendations)

    def test_recommendations_sorted_by_priority(self, tmp_path):
        """Test recommendations are sorted by priority."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        for i in range(5):
            tracker.register_region("vigenere", f"region_{i}", {}, 1000)
            tracker.record_exploration("vigenere", f"region_{i}", count=i * 100)

        recs = tracker.get_recommendations(top_n=5)

        # Should be sorted by priority score
        for i in range(len(recs) - 1):
            assert recs[i]["priority_score"] >= recs[i + 1]["priority_score"]

    def test_export_heatmap_data(self, tmp_path):
        """Test exporting heatmap data."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=800)  # 80% - green

        tracker.register_region("vigenere", "length_8", {}, 1000)
        tracker.record_exploration("vigenere", "length_8", count=100)  # 10% - red

        heatmap = tracker.export_heatmap_data("vigenere")

        assert heatmap["cipher_type"] == "vigenere"
        assert len(heatmap["regions"]) == 2
        assert all("color" in region for region in heatmap["regions"])

    def test_heatmap_color_coding(self, tmp_path):
        """Test heatmap color coding based on coverage."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # High coverage (>90%) - green
        tracker.register_region("vigenere", "high", {}, 1000)
        tracker.record_exploration("vigenere", "high", count=950)

        # Medium coverage (50-90%) - orange
        tracker.register_region("vigenere", "medium", {}, 1000)
        tracker.record_exploration("vigenere", "medium", count=700)

        # Low coverage (<10%) - gray
        tracker.register_region("vigenere", "low", {}, 1000)
        tracker.record_exploration("vigenere", "low", count=50)

        heatmap = tracker.export_heatmap_data("vigenere")
        colors = {r["name"]: r["color"] for r in heatmap["regions"]}

        assert colors["high"] == "#2ecc71"  # Green
        assert colors["medium"] == "#f39c12"  # Orange
        assert colors["low"] == "#95a5a6"  # Gray

    def test_persistence(self, tmp_path):
        """Test coverage data persistence."""
        # First session
        tracker1 = SearchSpaceTracker(cache_dir=tmp_path)
        tracker1.register_region("vigenere", "length_5", {"key_length": 5}, 1000)
        tracker1.record_exploration("vigenere", "length_5", count=250)
        # Saving happens automatically on record_exploration

        # Second session
        tracker2 = SearchSpaceTracker(cache_dir=tmp_path)

        # Should load previous data
        assert "vigenere" in tracker2.regions
        assert "length_5" in tracker2.regions["vigenere"]
        assert tracker2.regions["vigenere"]["length_5"].explored_count == 250


class TestIntegration:
    """Integration tests for search space tracking."""

    def test_full_coverage_workflow(self, tmp_path):
        """Test complete coverage tracking workflow."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # Register Vigenère key lengths 1-10
        for length in range(1, 11):
            total_size = min(26**length, 1000000)  # Cap for demo
            tracker.register_region(
                "vigenere",
                f"length_{length}",
                {"key_length": length},
                total_size,
            )

        # Simulate exploration
        tracker.record_exploration("vigenere", "length_5", count=500, successful=25)
        tracker.record_exploration("vigenere", "length_8", count=1000, successful=10)
        tracker.record_exploration("vigenere", "length_3", count=10000, successful=100)

        # Get coverage report
        report = tracker.get_coverage_report("vigenere")
        assert report["cipher_types"]["vigenere"]["total_explored"] > 0

        # Identify gaps
        gaps = tracker.identify_gaps("vigenere", min_coverage=5.0)
        assert len(gaps) > 0

        # Get recommendations
        recs = tracker.get_recommendations(top_n=5)
        assert len(recs) > 0
        assert all("reason" in rec for rec in recs)

        # Export heatmap
        heatmap = tracker.export_heatmap_data("vigenere")
        assert len(heatmap["regions"]) == 10

    def test_multiple_cipher_types(self, tmp_path):
        """Test tracking multiple cipher types."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path)

        # Vigenère
        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=500)

        # Hill
        tracker.register_region("hill", "2x2", {"matrix_size": 2}, 500)
        tracker.record_exploration("hill", "2x2", count=100)

        # Transposition
        tracker.register_region("transposition", "period_10", {"period": 10}, 2000)
        tracker.record_exploration("transposition", "period_10", count=1000)

        # Get overall report
        report = tracker.get_coverage_report()
        assert len(report["cipher_types"]) == 3
        assert "vigenere" in report["cipher_types"]
        assert "hill" in report["cipher_types"]
        assert "transposition" in report["cipher_types"]
