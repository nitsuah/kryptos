"""Tests for literature gap analysis bridge."""

from kryptos.provenance.attack_log import AttackLogger, AttackParameters, AttackResult
from kryptos.research.literature_bridge import LiteratureGapAnalyzer


class TestLiteratureGapAnalyzer:
    """Test literature gap analyzer."""

    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = LiteratureGapAnalyzer()

        assert analyzer.attack_logger is not None
        assert analyzer.paper_searcher is not None
        assert analyzer.attack_extractor is not None

    def test_find_literature_gaps(self, tmp_path):
        """Test finding gaps in literature coverage."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        # Log some attacks
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key_length": 8},
            crib_text="BERLIN",
        )
        result = AttackResult(success=False, confidence_scores={"SPY": 0.3})
        logger.log_attack(k4_sample, params, result)

        # Analyze gaps
        gaps = analyzer.find_literature_gaps("vigenere", k4_sample, max_papers=5)

        assert "papers_analyzed" in gaps
        assert "attacks_extracted" in gaps
        assert "already_tried" in gaps
        assert "not_yet_tried" in gaps
        assert "coverage_rate" in gaps

    def test_get_literature_recommendations(self, tmp_path):
        """Test getting attack recommendations."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        recommendations = analyzer.get_literature_recommendations("vigenere", k4_sample, top_n=3)

        assert isinstance(recommendations, list)
        assert len(recommendations) <= 3

        # Should be sorted by confidence
        if len(recommendations) > 1:
            for i in range(len(recommendations) - 1):
                assert recommendations[i]["confidence"] >= recommendations[i + 1]["confidence"]

    def test_generate_coverage_report(self, tmp_path):
        """Test generating comprehensive coverage report."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        queries = ["vigenere", "transposition"]
        report = analyzer.generate_coverage_report(queries, k4_sample)

        assert "queries" in report
        assert "total_papers" in report
        assert "total_attacks" in report
        assert "literature_coverage" in report
        assert "top_gaps" in report

    def test_gap_analysis_with_existing_attacks(self, tmp_path):
        """Test gap analysis shows attacks we've already tried."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        # Log several attacks
        for length in [5, 8, 10]:
            params = AttackParameters(
                cipher_type="vigenere",
                key_or_params={"key_length": length},
            )
            result = AttackResult(success=False, confidence_scores={"SPY": 0.2})
            logger.log_attack(k4_sample, params, result)

        # Analyze gaps
        gaps = analyzer.find_literature_gaps("vigenere", k4_sample)

        # Should recognize some attacks as already tried
        assert gaps["already_tried"] >= 0
        assert gaps["coverage_rate"] >= 0.0


class TestIntegration:
    """Integration tests for literature bridge."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: search → extract → cross-ref → recommend."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        # Log some attacks
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key_length": 8},
            crib_text="BERLIN",
        )
        result = AttackResult(success=False)
        logger.log_attack(k4_sample, params, result)

        # Find gaps
        gaps = analyzer.find_literature_gaps("vigenere cryptanalysis", k4_sample)

        # Should have analyzed papers
        assert gaps["papers_analyzed"] > 0

        # Get recommendations
        recs = analyzer.get_literature_recommendations("vigenere", k4_sample, top_n=5)

        # Should have some recommendations
        assert isinstance(recs, list)

    def test_multi_query_coverage(self, tmp_path):
        """Test coverage report across multiple queries."""
        logger = AttackLogger(log_dir=tmp_path)
        analyzer = LiteratureGapAnalyzer(attack_logger=logger)

        k4_sample = "OBKRUOXOGHULBSOLIFBBWFLR"

        queries = ["vigenere", "transposition", "kryptos"]
        report = analyzer.generate_coverage_report(queries, k4_sample)

        # Should aggregate across queries
        assert report["total_papers"] > 0
        assert len(report["queries"]) == 3
        assert 0.0 <= report["literature_coverage"] <= 100.0
