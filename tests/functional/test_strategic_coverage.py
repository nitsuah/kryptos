"""Tests for strategic coverage analysis."""

from datetime import datetime

from kryptos.analysis.strategic_coverage import (
    CoverageTrend,
    StrategicCoverageAnalyzer,
)
from kryptos.provenance.search_space import SearchSpaceTracker


class TestCoverageTrend:
    """Test coverage trend dataclass."""

    def test_create_trend(self):
        """Test creating a coverage trend."""
        trend = CoverageTrend(
            timestamp=datetime.now(),
            cipher_type="vigenere",
            region_key="length_8",
            coverage_percent=45.5,
            explored_count=1000,
            successful_count=10,
        )

        assert trend.cipher_type == "vigenere"
        assert trend.coverage_percent == 45.5

    def test_trend_to_dict(self):
        """Test converting trend to dictionary."""
        trend = CoverageTrend(
            timestamp=datetime.now(),
            cipher_type="vigenere",
            region_key="length_5",
            coverage_percent=10.0,
            explored_count=100,
            successful_count=5,
        )

        d = trend.to_dict()
        assert "timestamp" in d
        assert d["cipher_type"] == "vigenere"


class TestStrategicCoverageAnalyzer:
    """Test strategic coverage analyzer."""

    def test_initialization(self, tmp_path):
        """Test analyzer initialization."""
        analyzer = StrategicCoverageAnalyzer(history_dir=tmp_path)

        assert analyzer.tracker is not None
        assert analyzer.history_dir == tmp_path
        assert isinstance(analyzer.coverage_history, list)

    def test_record_coverage_snapshot(self, tmp_path):
        """Test recording coverage snapshot."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        # Register and explore
        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=500)

        # Record snapshot
        initial_count = len(analyzer.coverage_history)
        analyzer.record_coverage_snapshot()

        assert len(analyzer.coverage_history) > initial_count

    def test_analyze_saturation(self, tmp_path):
        """Test saturation analysis."""
        tracker = SearchSpaceTracker(cache_dir=tmp_path / "tracker")
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path / "history")

        # Create regions with different coverage
        tracker.register_region("vigenere", "high", {}, 1000)
        tracker.record_exploration("vigenere", "high", count=900)  # 90%

        tracker.register_region("vigenere", "low", {}, 1000)
        tracker.record_exploration("vigenere", "low", count=100)  # 10%

        # Analyze
        saturations = analyzer.analyze_saturation("vigenere", saturation_threshold=80.0)

        assert len(saturations) == 2
        assert any(s.is_saturated for s in saturations)
        assert any(not s.is_saturated for s in saturations)

    def test_saturation_recommendations(self, tmp_path):
        """Test saturation generates recommendations."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        tracker.register_region("vigenere", "saturated", {}, 1000)
        tracker.record_exploration("vigenere", "saturated", count=950)

        saturations = analyzer.analyze_saturation("vigenere")

        for sat in saturations:
            assert sat.recommendation
            assert isinstance(sat.recommendation, str)

    def test_generate_heatmap_json(self, tmp_path):
        """Test generating JSON heatmap."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=500)

        heatmap = analyzer.generate_heatmap_visualization("vigenere", output_format="json")

        assert isinstance(heatmap, dict)
        assert "cipher_type" in heatmap
        assert "regions" in heatmap

    def test_generate_heatmap_html(self, tmp_path):
        """Test generating HTML heatmap."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=500)

        html = analyzer.generate_heatmap_visualization("vigenere", output_format="html")

        assert isinstance(html, str)
        assert "<html>" in html.lower()
        assert "vigenere" in html.lower()

    def test_get_ops_recommendations(self, tmp_path):
        """Test getting OPS recommendations."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        # Create varied regions
        tracker.register_region("vigenere", "saturated", {}, 1000)
        tracker.record_exploration("vigenere", "saturated", count=950, successful=50)

        tracker.register_region("vigenere", "unexplored", {}, 1000)
        tracker.record_exploration("vigenere", "unexplored", count=50)

        recommendations = analyzer.get_ops_recommendations(top_n=5)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "action" in rec
            assert "cipher_type" in rec
            assert "reason" in rec
            assert "suggestion" in rec

    def test_recommendations_prioritized(self, tmp_path):
        """Test recommendations are prioritized."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        tracker.register_region("vigenere", "region1", {}, 1000)
        tracker.record_exploration("vigenere", "region1", count=950)

        recommendations = analyzer.get_ops_recommendations()

        # Should be sorted by priority
        for i in range(len(recommendations) - 1):
            assert recommendations[i]["priority"] <= recommendations[i + 1]["priority"]

    def test_generate_ops_report(self, tmp_path):
        """Test generating comprehensive OPS report."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=500)

        report = analyzer.generate_coverage_report_for_ops()

        assert "timestamp" in report
        assert "overall_status" in report
        assert "saturation_analysis" in report
        assert "recommendations" in report
        assert "trends" in report

    def test_history_persistence(self, tmp_path):
        """Test coverage history persistence."""
        tracker = SearchSpaceTracker()

        # First analyzer
        analyzer1 = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)
        tracker.register_region("vigenere", "length_5", {}, 1000)
        tracker.record_exploration("vigenere", "length_5", count=100)
        analyzer1.record_coverage_snapshot()

        # Second analyzer (should load history)
        analyzer2 = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        assert len(analyzer2.coverage_history) > 0


class TestIntegration:
    """Integration tests for strategic coverage."""

    def test_full_workflow(self, tmp_path):
        """Test complete strategic analysis workflow."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        # Set up regions
        for length in [5, 8, 10]:
            tracker.register_region("vigenere", f"length_{length}", {}, 1000)

        # Simulate exploration
        tracker.record_exploration("vigenere", "length_5", count=900, successful=45)
        tracker.record_exploration("vigenere", "length_8", count=100, successful=2)

        # Record snapshot
        analyzer.record_coverage_snapshot()

        # Analyze saturation
        saturations = analyzer.analyze_saturation("vigenere")
        assert len(saturations) > 0

        # Get recommendations
        recs = analyzer.get_ops_recommendations()
        assert len(recs) > 0

        # Generate report
        report = analyzer.generate_coverage_report_for_ops()
        assert "vigenere" in report["overall_status"]

    def test_time_series_analysis(self, tmp_path):
        """Test time-series trend analysis."""
        tracker = SearchSpaceTracker()
        analyzer = StrategicCoverageAnalyzer(tracker=tracker, history_dir=tmp_path)

        # Register region
        tracker.register_region("vigenere", "length_5", {}, 10000)

        # Simulate progress over time
        for _i in range(5):
            tracker.record_exploration("vigenere", "length_5", count=1000)
            analyzer.record_coverage_snapshot()

        # Should have multiple snapshots
        assert len(analyzer.coverage_history) >= 5

        # Should be able to generate report
        report = analyzer.generate_coverage_report_for_ops()
        assert "trends" in report
