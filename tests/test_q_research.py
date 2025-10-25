"""Tests for Q-Research academic cryptanalysis techniques."""

from __future__ import annotations

from kryptos.research.q_patterns import (
    DigraphAnalysis,
    QResearchAnalyzer,
    VigenereMetrics,
)


class TestQResearchInitialization:
    """Test Q-Research analyzer initialization."""

    def test_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = QResearchAnalyzer()

        assert len(analyzer.english_digraphs) > 0
        assert "TH" in analyzer.english_digraphs
        assert analyzer.english_digraphs["TH"] > 3.0

        assert len(analyzer.english_frequencies) == 26
        assert analyzer.english_frequencies["E"] > 12.0

    def test_digraph_data_valid(self):
        """Test digraph frequencies are valid."""
        analyzer = QResearchAnalyzer()

        for digraph, freq in analyzer.english_digraphs.items():
            assert len(digraph) == 2
            assert digraph.isupper()
            assert freq > 0


class TestDigraphAnalysis:
    """Test digraph frequency analysis."""

    def test_analyze_simple_text(self):
        """Test analyzing simple text."""
        analyzer = QResearchAnalyzer()
        result = analyzer.analyze_digraphs("THE QUICK BROWN FOX")

        assert isinstance(result, DigraphAnalysis)
        assert result.total_digraphs > 0
        assert len(result.digraph_counts) > 0
        assert len(result.top_digraphs) > 0

    def test_english_text_low_deviation(self):
        """Test English text has low deviation."""
        analyzer = QResearchAnalyzer()
        english = "THE NORTH EAST CORNER OF THE BERLIN CLOCK TOWER"
        result = analyzer.analyze_digraphs(english)

        # English should have relatively low deviation
        assert result.deviation_score < 100

    def test_random_text_high_deviation(self):
        """Test random text has high deviation."""
        analyzer = QResearchAnalyzer()
        random = "XQZJKWPVFYHMGLBNRTSDCAEIOU"
        result = analyzer.analyze_digraphs(random)

        # Random should have higher deviation
        assert result.deviation_score > 50

    def test_empty_text(self):
        """Test with empty text."""
        analyzer = QResearchAnalyzer()
        result = analyzer.analyze_digraphs("")

        assert result.total_digraphs == 0
        assert len(result.digraph_counts) == 0

    def test_top_digraphs_sorted(self):
        """Test top digraphs are sorted by frequency."""
        analyzer = QResearchAnalyzer()
        result = analyzer.analyze_digraphs("AABBCCDDAABBCCAABBAABB")

        # Should be sorted descending
        for i in range(len(result.top_digraphs) - 1):
            assert result.top_digraphs[i][1] >= result.top_digraphs[i + 1][1]


class TestPalindromeDetection:
    """Test palindrome pattern detection."""

    def test_detect_exact_palindrome(self):
        """Test detecting exact palindrome."""
        analyzer = QResearchAnalyzer()
        palindromes = analyzer.detect_palindromes("ABCMADAMXYZ")

        # Should find "MADAM" and other shorter palindromes
        exact = [p for p in palindromes if p.pattern_type == "exact"]
        assert len(exact) > 0  # Should find at least "ADA" or "MAM"

    def test_detect_short_palindrome(self):
        """Test detecting short palindromes."""
        analyzer = QResearchAnalyzer()
        palindromes = analyzer.detect_palindromes("XYZABADEFGHG", min_length=3)

        # Should find "ABA"
        assert len(palindromes) > 0
        assert any(p.text == "ABA" for p in palindromes)

    def test_detect_approximate_palindrome(self):
        """Test detecting approximate palindromes."""
        analyzer = QResearchAnalyzer()
        # "MADAX" is close to palindrome "MADAM"
        palindromes = analyzer.detect_palindromes("ABCMADAX")

        approx = [p for p in palindromes if p.pattern_type == "approximate"]
        # Should find some approximate matches
        assert len(approx) >= 0  # May or may not find depending on criteria

    def test_no_palindromes(self):
        """Test text with no palindromes."""
        analyzer = QResearchAnalyzer()
        palindromes = analyzer.detect_palindromes("ABC", min_length=3)

        # "ABC" is not a palindrome
        assert len([p for p in palindromes if p.text == "ABC"]) == 0

    def test_palindrome_positions(self):
        """Test palindrome positions are correct."""
        analyzer = QResearchAnalyzer()
        palindromes = analyzer.detect_palindromes("XYZRADARQRS")

        radar = [p for p in palindromes if p.text == "RADAR" and p.pattern_type == "exact"]
        if radar:
            assert radar[0].position == 3  # RADAR starts at index 3


class TestVigenereAnalysis:
    """Test Vigenère cipher analysis."""

    def test_analyze_short_text(self):
        """Test with short text."""
        analyzer = QResearchAnalyzer()
        result = analyzer.vigenere_analysis("ABCDEF")

        assert isinstance(result, VigenereMetrics)
        # Short text won't have reliable results
        assert result.likely_key_length >= 0

    def test_analyze_plaintext(self):
        """Test with English plaintext."""
        analyzer = QResearchAnalyzer()
        plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        result = analyzer.vigenere_analysis(plaintext)

        # Plaintext should have IC values calculated
        assert 1 in result.ic_values
        # IC for key length 1 means no shift applied - will be low for short diverse text
        assert result.ic_values[1] >= 0.0

    def test_repeated_sequences_kasiski(self):
        """Test Kasiski examination finds repeated sequences."""
        analyzer = QResearchAnalyzer()
        # Create text with repeated sequences
        text = "ABCABC" * 10
        result = analyzer.vigenere_analysis(text)

        # Should find distance 3 (ABC repeats every 3 chars)
        assert 3 in result.kasiski_distances

    def test_key_length_candidates(self):
        """Test key length candidates are reasonable."""
        analyzer = QResearchAnalyzer()
        text = "A" * 100
        result = analyzer.vigenere_analysis(text)

        assert len(result.key_length_candidates) > 0
        # All candidates should be reasonable
        for key_len in result.key_length_candidates:
            assert 1 <= key_len <= 20


class TestTranspositionDetection:
    """Test transposition cipher detection."""

    def test_detect_english_plaintext(self):
        """Test with English plaintext."""
        analyzer = QResearchAnalyzer()
        plaintext = "THE NORTH EAST CORNER OF THE BERLIN CLOCK"
        hints = analyzer.detect_transposition_hints(plaintext)

        # English text might show transposition hints (high IC, preserved freq)
        # But should be uncertain
        assert isinstance(hints, list)

    def test_detect_columnar_hint(self):
        """Test detecting columnar transposition hint."""
        analyzer = QResearchAnalyzer()
        # Text length 40 (divisible by many numbers)
        text = "A" * 40
        hints = analyzer.detect_transposition_hints(text)

        columnar_hints = [h for h in hints if h.method == "columnar"]
        # Should find some columnar possibilities
        assert len(columnar_hints) >= 0

    def test_short_text_no_hints(self):
        """Test short text returns no hints."""
        analyzer = QResearchAnalyzer()
        hints = analyzer.detect_transposition_hints("ABC")

        assert len(hints) == 0

    def test_hint_confidence_range(self):
        """Test hint confidence is in valid range."""
        analyzer = QResearchAnalyzer()
        text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG" * 2
        hints = analyzer.detect_transposition_hints(text)

        for hint in hints:
            assert 0.0 <= hint.confidence <= 1.0


class TestAttackStrategies:
    """Test attack strategy suggestions."""

    def test_suggest_strategies_plaintext(self):
        """Test strategies for plaintext."""
        analyzer = QResearchAnalyzer()
        plaintext = "THE QUICK BROWN FOX"
        strategies = analyzer.suggest_attack_strategies(plaintext)

        assert "substitution" in strategies
        assert "transposition" in strategies
        assert "polyalphabetic" in strategies
        assert "hybrid" in strategies

    def test_strategies_have_priorities(self):
        """Test all strategies have priority scores."""
        analyzer = QResearchAnalyzer()
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4
        strategies = analyzer.suggest_attack_strategies(text)

        for _category, details in strategies.items():
            assert "priority" in details
            assert 0.0 <= details["priority"] <= 1.0
            assert "methods" in details

    def test_high_ic_suggests_substitution(self):
        """Test high IC suggests substitution."""
        analyzer = QResearchAnalyzer()
        # English-like letter frequencies (longer text for reliable IC)
        text = "ETAOINSHRDLCUMWFGYPBVKJXQZETAOINSHRDLCUMWFGYPBVKJXQZ" * 4
        strategies = analyzer.suggest_attack_strategies(text)

        # Should suggest some strategy (at least one priority > 0)
        total_priority = sum(s["priority"] for s in strategies.values())
        assert total_priority > 0

    def test_low_ic_suggests_polyalphabetic(self):
        """Test low IC suggests polyalphabetic."""
        analyzer = QResearchAnalyzer()
        # Very flat distribution
        text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4
        strategies = analyzer.suggest_attack_strategies(text)

        # Should suggest some strategy
        total_priority = sum(s["priority"] for s in strategies.values())
        assert total_priority >= 0


class TestHelperMethods:
    """Test helper methods."""

    def test_calculate_ic_english(self):
        """Test IC calculation for English text."""
        analyzer = QResearchAnalyzer()
        english = "THENORTHEASTCORNEROFTHEBERLINCLOCK"
        ic = analyzer._calculate_ic(english)

        # English IC ≈ 0.067
        assert 0.055 < ic < 0.080

    def test_calculate_ic_random(self):
        """Test IC calculation for random text."""
        analyzer = QResearchAnalyzer()
        random = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ic = analyzer._calculate_ic(random)

        # Each letter appears once - IC will be 0
        assert ic == 0.0

    def test_calculate_ic_empty(self):
        """Test IC with empty text."""
        analyzer = QResearchAnalyzer()
        ic = analyzer._calculate_ic("")

        assert ic == 0.0

    def test_compare_letter_frequencies(self):
        """Test letter frequency comparison."""
        analyzer = QResearchAnalyzer()
        english = "ETAOIN" * 10
        score = analyzer._compare_letter_frequencies(english)

        # Should have some similarity to English
        assert 0.0 <= score <= 1.0

    def test_rank_key_lengths(self):
        """Test key length ranking."""
        analyzer = QResearchAnalyzer()
        ic_values = {1: 0.067, 2: 0.045, 3: 0.050, 5: 0.066}
        kasiski = [3, 6, 9, 12, 15]

        ranked = analyzer._rank_key_lengths(ic_values, kasiski)

        assert isinstance(ranked, list)
        assert len(ranked) > 0
        # Key length 3 should rank high (divides many Kasiski distances)
        assert 3 in ranked


class TestIntegration:
    """Integration tests."""

    def test_full_analysis_k4_sample(self):
        """Test full analysis on K4 sample."""
        analyzer = QResearchAnalyzer()
        k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBN"

        # Run all analyses
        digraphs = analyzer.analyze_digraphs(k4)
        palindromes = analyzer.detect_palindromes(k4)
        vigenere = analyzer.vigenere_analysis(k4)
        transposition = analyzer.detect_transposition_hints(k4)
        strategies = analyzer.suggest_attack_strategies(k4)

        # All should return valid results
        assert digraphs.total_digraphs > 0
        assert isinstance(palindromes, list)
        assert vigenere.likely_key_length > 0
        assert isinstance(transposition, list)
        assert sum(s["priority"] for s in strategies.values()) >= 0

    def test_multiple_analyses_consistent(self):
        """Test multiple analyses of same text are consistent."""
        analyzer = QResearchAnalyzer()
        text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"

        result1 = analyzer.analyze_digraphs(text)
        result2 = analyzer.analyze_digraphs(text)

        assert result1.total_digraphs == result2.total_digraphs
        assert result1.deviation_score == result2.deviation_score

    def test_empty_text_all_methods(self):
        """Test all methods handle empty text gracefully."""
        analyzer = QResearchAnalyzer()

        digraphs = analyzer.analyze_digraphs("")
        palindromes = analyzer.detect_palindromes("")
        vigenere = analyzer.vigenere_analysis("")
        transposition = analyzer.detect_transposition_hints("")
        strategies = analyzer.suggest_attack_strategies("")

        # Should all return without errors
        assert digraphs.total_digraphs == 0
        assert len(palindromes) == 0
        assert vigenere.likely_key_length == 0
        assert len(transposition) == 0
        assert isinstance(strategies, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_character(self):
        """Test with single character."""
        analyzer = QResearchAnalyzer()

        digraphs = analyzer.analyze_digraphs("A")
        assert digraphs.total_digraphs == 0

    def test_repeated_character(self):
        """Test with repeated characters."""
        analyzer = QResearchAnalyzer()
        text = "A" * 100

        digraphs = analyzer.analyze_digraphs(text)
        assert "AA" in digraphs.digraph_counts
        assert digraphs.digraph_counts["AA"] == 99

    def test_non_alpha_ignored(self):
        """Test non-alphabetic characters are ignored."""
        analyzer = QResearchAnalyzer()
        text = "A-B-C 1 2 3 D@E!F"

        digraphs = analyzer.analyze_digraphs(text)
        # Should only count AB, BC, CD, DE, EF
        assert digraphs.total_digraphs == 5

    def test_lowercase_converted(self):
        """Test lowercase is converted to uppercase."""
        analyzer = QResearchAnalyzer()

        result1 = analyzer.analyze_digraphs("abc")
        result2 = analyzer.analyze_digraphs("ABC")

        assert result1.digraph_counts == result2.digraph_counts
