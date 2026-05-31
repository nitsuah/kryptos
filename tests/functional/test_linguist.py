"""Tests for LINGUIST neural NLP agent."""

import pytest

from kryptos.agents.linguist import (
    LinguistAgent,
    LinguisticScore,
    SanbornCorpusAnalysis,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory."""
    return tmp_path / "linguist_cache"


@pytest.fixture
def linguist(temp_cache_dir):
    """Create LINGUIST agent."""
    return LinguistAgent(
        model_name="distilbert-base-uncased",
        device="cpu",
        cache_dir=temp_cache_dir,
    )


class TestLinguistInitialization:
    """Test LINGUIST agent initialization."""

    def test_initialization(self, linguist, temp_cache_dir):
        """Should initialize with correct parameters."""
        assert linguist.model_name == "distilbert-base-uncased"
        assert linguist.device == "cpu"
        assert linguist.cache_dir == temp_cache_dir
        assert linguist.cache_dir.exists()

    def test_sanborn_corpus_loaded(self, linguist):
        """Should load Sanborn corpus."""
        assert "vocabulary" in linguist.sanborn_corpus
        assert "themes" in linguist.sanborn_corpus
        assert len(linguist.sanborn_corpus["vocabulary"]) > 0

    def test_sanborn_themes(self, linguist):
        """Should have expected themes."""
        themes = linguist.sanborn_corpus["themes"]
        assert "location" in themes
        assert "mystery" in themes
        assert "archaeology" in themes
        assert "light" in themes


class TestCandidateValidation:
    """Test candidate validation."""

    def test_validate_real_k1_text(self, linguist):
        """K1 plaintext should score high."""
        k1_text = "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT"
        score = linguist.validate_candidate(k1_text)

        assert isinstance(score, LinguisticScore)
        assert score.text == k1_text
        assert score.confidence > 0.5  # Should be reasonably confident
        assert score.perplexity > 0
        assert 0 <= score.coherence <= 1
        assert 0 <= score.grammar_score <= 1

    def test_validate_gibberish(self, linguist):
        """Gibberish should score low."""
        gibberish = "XQZMWPVUTRSLKJIHGFEDCBA"
        score = linguist.validate_candidate(gibberish)

        assert score.confidence < 0.5  # Should be low confidence
        assert score.perplexity > 100  # High perplexity

    def test_validate_repetitive_text(self, linguist):
        """Repetitive text should score lower than natural text."""
        repetitive = "AAA BBB CCC DDD EEE FFF GGG"
        score = linguist.validate_candidate(repetitive)

        # Unique ratio is 1.0 (all different), but still not great coherence
        assert score.coherence < 0.75  # Should be lower than natural text

    def test_validate_plausible_text(self, linguist):
        """Plausible English text should score reasonably."""
        text = "THE CLOCK IS HIDDEN IN BERLIN NEAR THE WALL"
        score = linguist.validate_candidate(text)

        assert score.confidence > 0.4
        assert score.coherence > 0.5
        assert score.grammar_score > 0.5

    def test_validate_short_text(self, linguist):
        """Short text should get lower scores."""
        short = "ABC"
        score = linguist.validate_candidate(short)

        assert score.confidence < 0.5


class TestScoreCaching:
    """Test score caching."""

    def test_cache_stores_results(self, linguist):
        """Should cache validation results."""
        text = "TEST TEXT FOR CACHING"

        assert len(linguist.score_cache) == 0

        linguist.validate_candidate(text)
        assert len(linguist.score_cache) == 1

    def test_cache_retrieves_cached(self, linguist):
        """Should retrieve from cache on second call."""
        text = "ANOTHER TEST TEXT"

        score1 = linguist.validate_candidate(text)
        score2 = linguist.validate_candidate(text)

        # Should be same object (from cache)
        assert score1 is score2
        assert score1.timestamp == score2.timestamp


class TestSanbornAnalysis:
    """Test Sanborn corpus analysis."""

    def test_analyze_k1_style(self, linguist):
        """K1 text should match Sanborn style."""
        k1_text = "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT"
        analysis = linguist.analyze_sanborn_style(k1_text)

        assert isinstance(analysis, SanbornCorpusAnalysis)
        assert analysis.vocabulary_match > 0.5
        assert "light" in analysis.themes_detected
        assert analysis.confidence > 0.3

    def test_analyze_k2_style(self, linguist):
        """K2 text should match Sanborn style."""
        k2_snippet = "DOES LANGLEY KNOW ABOUT THIS BURIED OUT THERE"
        analysis = linguist.analyze_sanborn_style(k2_snippet)

        assert analysis.vocabulary_match > 0.3
        assert "mystery" in analysis.themes_detected

    def test_analyze_k3_style(self, linguist):
        """K3 text should match Sanborn style."""
        k3_snippet = "SLOWLY DESPERATELY SLOWLY THE REMAINS OF PASSAGE"
        analysis = linguist.analyze_sanborn_style(k3_snippet)

        assert analysis.vocabulary_match > 0.4
        assert "archaeology" in analysis.themes_detected

    def test_analyze_non_sanborn_text(self, linguist):
        """Non-Sanborn text should score lower."""
        modern_text = "I WENT TO THE STORE TO BUY GROCERIES TODAY"
        analysis = linguist.analyze_sanborn_style(modern_text)

        assert analysis.confidence < 0.5
        assert len(analysis.themes_detected) == 0

    def test_vocabulary_match_calculation(self, linguist):
        """Should calculate vocabulary match correctly."""
        # All words in Sanborn corpus
        text = "SLOWLY INVISIBLE UNKNOWN"
        analysis = linguist.analyze_sanborn_style(text)
        assert analysis.vocabulary_match > 0.8

        # No words in Sanborn corpus
        text = "PIZZA COMPUTER SMARTPHONE"
        analysis = linguist.analyze_sanborn_style(text)
        assert analysis.vocabulary_match < 0.2


class TestBatchValidation:
    """Test batch validation."""

    def test_batch_validate_returns_top_k(self, linguist):
        """Should return top-k candidates."""
        candidates = [
            "BETWEEN SUBTLE SHADING AND THE ABSENCE",
            "THE CLOCK IS HIDDEN IN BERLIN",
            "XQZMWPVUTRSLKJIHGFEDCBA",
            "AAA BBB CCC DDD EEE",
            "SLOWLY DESPERATELY SLOWLY",
        ]

        top_3 = linguist.batch_validate(candidates, threshold=0.3, top_k=3)

        assert len(top_3) <= 3
        assert all(isinstance(item, tuple) for item in top_3)
        assert all(isinstance(item[1], LinguisticScore) for item in top_3)

    def test_batch_validate_sorted_by_confidence(self, linguist):
        """Should sort by confidence descending."""
        candidates = [
            "GIBBERISH XQZMWP",
            "SLOWLY DESPERATELY SLOWLY THE REMAINS",
            "ANOTHER PLAUSIBLE TEXT HERE",
        ]

        top_candidates = linguist.batch_validate(candidates, threshold=0.0, top_k=10)

        # Check sorted descending
        confidences = [score.confidence for _, score in top_candidates]
        assert confidences == sorted(confidences, reverse=True)

    def test_batch_validate_filters_by_threshold(self, linguist):
        """Should filter candidates below threshold."""
        candidates = [
            "GOOD ENGLISH TEXT HERE",
            "XQZMWPVUTRSLKJIHGFEDCBA",
            "ANOTHER GOOD TEXT",
        ]

        high_threshold = linguist.batch_validate(candidates, threshold=0.9, top_k=10)
        low_threshold = linguist.batch_validate(candidates, threshold=0.2, top_k=10)

        # High threshold should filter more
        assert len(high_threshold) <= len(low_threshold)


class TestCrossValidation:
    """Test cross-validation with SPY."""

    def test_cross_validate_with_spy(self, linguist):
        """Should cross-validate with SPY scores."""
        text = "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT"
        spy_score = 0.85
        spy_features = {"rhyme": True, "entities": ["LIGHT"]}

        result = linguist.cross_validate_with_spy(text, spy_score, spy_features)

        assert "text" in result
        assert "spy_score" in result
        assert "linguist_score" in result
        assert "agreement" in result
        assert "combined_score" in result
        assert "recommendation" in result

    def test_high_agreement_scores(self, linguist):
        """High agreement should give strong recommendation."""
        text = "GOOD TEXT THAT BOTH AGREE ON"
        spy_score = 0.80

        result = linguist.cross_validate_with_spy(text, spy_score, {})

        # If both scores are similar, agreement should be high
        if abs(spy_score - result["linguist_score"]) < 0.2:
            assert result["agreement"] > 0.8

    def test_low_agreement_needs_review(self, linguist):
        """Low agreement should flag for review."""
        text = "AMBIGUOUS TEXT"
        spy_score = 0.90  # SPY thinks it's great

        result = linguist.cross_validate_with_spy(text, spy_score, {})

        # If linguist disagrees strongly, should need review
        if abs(spy_score - result["linguist_score"]) > 0.3:
            assert result["recommendation"] == "REVIEW_NEEDED"

    def test_combined_score_is_average(self, linguist):
        """Combined score should be average of both."""
        text = "TEST TEXT"
        spy_score = 0.60

        result = linguist.cross_validate_with_spy(text, spy_score, {})

        expected_combined = (spy_score + result["linguist_score"]) / 2
        assert abs(result["combined_score"] - expected_combined) < 0.01


class TestPerplexityCalculation:
    """Test perplexity calculation."""

    def test_heuristic_perplexity_english(self, linguist):
        """English text should have lower perplexity."""
        english = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        perplexity = linguist._heuristic_perplexity(english)

        assert perplexity < 200  # Reasonable for English

    def test_heuristic_perplexity_gibberish(self, linguist):
        """Gibberish should have high perplexity."""
        gibberish = "ZZZZQQQQXXXXWWWWVVVVUUUU"
        perplexity = linguist._heuristic_perplexity(gibberish)

        assert perplexity > 200  # High for gibberish

    def test_empty_text_perplexity(self, linguist):
        """Empty text should return high perplexity."""
        perplexity = linguist._heuristic_perplexity("")
        assert perplexity >= 1000


class TestCoherenceCalculation:
    """Test coherence calculation."""

    def test_coherence_normal_text(self, linguist):
        """Normal text should have decent coherence."""
        text = "THE CAT SAT ON THE MAT WITH A HAT"
        coherence = linguist._calculate_coherence(text)

        assert 0.4 < coherence < 0.9

    def test_coherence_repetitive(self, linguist):
        """Repetitive text should have lower coherence."""
        text = "THE THE THE THE THE THE"
        coherence = linguist._calculate_coherence(text)

        # Heavy penalty for low uniqueness (1/6 = 0.167)
        assert coherence < 0.6

    def test_coherence_short_text(self, linguist):
        """Short text should have lower coherence."""
        text = "AB"
        coherence = linguist._calculate_coherence(text)

        assert coherence < 0.5


class TestGrammarScore:
    """Test grammar scoring."""

    def test_grammar_capitalized_sentences(self, linguist):
        """Properly capitalized text should score higher."""
        proper = "The cat sat. The dog ran."
        improper = "the cat sat. the dog ran."

        proper_score = linguist._calculate_grammar_score(proper)
        improper_score = linguist._calculate_grammar_score(improper)

        assert proper_score > improper_score

    def test_grammar_balanced_punctuation(self, linguist):
        """Balanced punctuation should score better."""
        balanced = "The (cat) sat [here] today."
        unbalanced = "The (cat sat [here today."

        balanced_score = linguist._calculate_grammar_score(balanced)
        unbalanced_score = linguist._calculate_grammar_score(unbalanced)

        assert balanced_score > unbalanced_score


class TestScorePersistence:
    """Test score saving/loading."""

    def test_save_scores(self, linguist, temp_cache_dir):
        """Should save scores to file."""
        linguist.validate_candidate("TEST TEXT ONE")
        linguist.validate_candidate("TEST TEXT TWO")

        output_file = temp_cache_dir / "test_scores.json"
        linguist.save_scores(output_file)

        assert output_file.exists()

        # Check file contents
        import json

        with open(output_file) as f:
            data = json.load(f)
            assert len(data) == 2
            assert all("text" in item for item in data)
            assert all("confidence" in item for item in data)


@pytest.mark.integration
class TestLinguistIntegration:
    """Integration tests for LINGUIST agent."""

    def test_full_validation_pipeline(self, linguist):
        """Test full validation pipeline."""
        candidates = [
            "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE",
            "XQZMWPVUTRSLKJIHGFEDCBA RANDOM GIBBERISH",
            "THE SECRET IS HIDDEN SOMEWHERE IN THE NORTHEAST CORNER",
        ]

        # Batch validate
        results = linguist.batch_validate(candidates, threshold=0.4, top_k=10)

        # Should have some results
        assert len(results) > 0

        # Top result should be reasonable
        top_text, top_score = results[0]
        assert top_score.confidence > 0.4

        # Analyze top candidate against Sanborn
        sanborn_analysis = linguist.analyze_sanborn_style(top_text)
        assert sanborn_analysis.confidence >= 0.0

    def test_cross_validation_workflow(self, linguist):
        """Test cross-validation with SPY workflow."""
        text = "SLOWLY DESPERATELY SLOWLY THE REMAINS OF PASSAGE DEBRIS"

        # Simulate SPY analysis
        spy_score = 0.75
        spy_features = {"entities": ["PASSAGE"], "poetic": True}

        # Cross-validate
        result = linguist.cross_validate_with_spy(text, spy_score, spy_features)

        assert result["combined_score"] > 0.5
        assert result["recommendation"] in ["STRONG_CANDIDATE", "REVIEW_NEEDED"]
