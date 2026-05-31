"""Tests for attack extraction from academic papers."""

from kryptos.research.attack_extractor import AttackExtractor, ExtractedAttack
from kryptos.research.paper_search import Paper


class TestExtractedAttack:
    """Test ExtractedAttack dataclass."""

    def test_create_extracted_attack(self):
        """Test creating an extracted attack."""
        attack = ExtractedAttack(
            cipher_type="vigenere",
            attack_method="frequency_analysis",
            key_parameters={"key_length": 8},
            crib_text="BERLIN",
            confidence=0.8,
        )

        assert attack.cipher_type == "vigenere"
        assert attack.key_parameters["key_length"] == 8
        assert attack.confidence == 0.8

    def test_to_attack_parameters(self):
        """Test converting to AttackParameters format."""
        attack = ExtractedAttack(
            cipher_type="vigenere",
            attack_method="crib_dragging",
            key_parameters={"key_length": 10},
            crib_text="KRYPTOS",
            crib_position=5,
            source_paper="arxiv:1234.5678",
        )

        params = attack.to_attack_parameters()

        assert params["cipher_type"] == "vigenere"
        assert params["key_or_params"]["key_length"] == 10
        assert params["crib_text"] == "KRYPTOS"
        assert params["crib_position"] == 5
        assert "academic:arxiv:1234.5678" in params["additional_params"]["source"]


class TestAttackExtractor:
    """Test attack extraction functionality."""

    def test_initialization(self):
        """Test extractor initialization."""
        extractor = AttackExtractor()

        assert "vigenere" in extractor.cipher_patterns
        assert "frequency_analysis" in extractor.attack_patterns

    def test_detect_cipher_types(self):
        """Test cipher type detection."""
        extractor = AttackExtractor()

        text = "We analyze Vigenère ciphers and transposition methods."
        ciphers = extractor._detect_cipher_types(text)

        assert "vigenere" in ciphers
        assert "transposition" in ciphers

    def test_detect_attack_methods(self):
        """Test attack method detection."""
        extractor = AttackExtractor()

        text = "Using frequency analysis and crib dragging techniques."
        methods = extractor._detect_attack_methods(text)

        assert "frequency_analysis" in methods
        assert "crib_dragging" in methods

    def test_extract_key_length(self):
        """Test key length extraction."""
        extractor = AttackExtractor()

        text = "We tested with key length of 8 characters."
        params = extractor._extract_key_parameters(text)

        assert "vigenere" in params
        assert params["vigenere"]["key_length"] == 8

    def test_extract_key_range(self):
        """Test key range extraction."""
        extractor = AttackExtractor()

        text = "Key lengths from 5 to 15 were tested."
        params = extractor._extract_key_parameters(text)

        assert "vigenere" in params
        assert params["vigenere"]["key_length_min"] == 5
        assert params["vigenere"]["key_length_max"] == 15

    def test_extract_cribs(self):
        """Test crib extraction."""
        extractor = AttackExtractor()

        text = 'We used the known plaintext "BERLIN" as a crib.'
        cribs = extractor._extract_cribs(text)

        assert "BERLIN" in cribs

    def test_extract_from_paper(self):
        """Test extracting attacks from paper."""
        extractor = AttackExtractor()

        paper = Paper(
            paper_id="test:123",
            title="Breaking Vigenère with Frequency Analysis",
            authors=["Smith, J."],
            abstract="We present frequency analysis methods for Vigenère ciphers "
            "with key length 8. Using known plaintext 'BERLIN' we achieve 95% success.",
            year=2020,
        )

        attacks = extractor.extract_from_paper(paper)

        assert len(attacks) > 0
        assert any(a.cipher_type == "vigenere" for a in attacks)
        assert any(a.attack_method == "frequency_analysis" for a in attacks)

    def test_extract_multiple_ciphers(self):
        """Test extracting multiple cipher types."""
        extractor = AttackExtractor()

        paper = Paper(
            paper_id="test:456",
            title="Classical Cryptanalysis",
            authors=["Jones, A."],
            abstract="Methods for Vigenère, Hill, and transposition ciphers.",
            year=2021,
        )

        attacks = extractor.extract_from_paper(paper)

        cipher_types = {a.cipher_type for a in attacks}
        assert "vigenere" in cipher_types
        assert "hill" in cipher_types
        assert "transposition" in cipher_types

    def test_extract_from_multiple_papers(self):
        """Test bulk extraction from paper list."""
        extractor = AttackExtractor()

        papers = [
            Paper(
                paper_id="test:1",
                title="Vigenère Analysis",
                authors=["A"],
                abstract="Frequency analysis of Vigenère ciphers.",
                year=2020,
            ),
            Paper(
                paper_id="test:2",
                title="Transposition Methods",
                authors=["B"],
                abstract="Columnar transposition with genetic algorithms.",
                year=2021,
            ),
        ]

        attacks = extractor.extract_from_papers(papers)

        assert len(attacks) >= 2
        cipher_types = {a.cipher_type for a in attacks}
        assert "vigenere" in cipher_types
        assert "transposition" in cipher_types


class TestIntegration:
    """Integration tests for paper extraction workflow."""

    def test_search_and_extract_workflow(self, tmp_path):
        """Test complete search and extraction workflow."""
        from kryptos.research.paper_search import PaperSearch

        # Search for papers
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_arxiv("vigenere cryptanalysis", max_results=5)

        # Extract attacks
        extractor = AttackExtractor()
        attacks = extractor.extract_from_papers(papers)

        # Should extract some attacks
        assert len(attacks) > 0

        # Attacks should have valid structure
        for attack in attacks:
            assert attack.cipher_type
            assert attack.attack_method
            assert 0.0 <= attack.confidence <= 1.0

    def test_convert_to_attack_parameters(self, tmp_path):
        """Test converting extracted attacks to provenance format."""
        from kryptos.research.paper_search import PaperSearch

        # Search and extract
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_arxiv("vigenere", max_results=2)

        extractor = AttackExtractor()
        attacks = extractor.extract_from_papers(papers)

        # Convert to AttackParameters format
        for attack in attacks:
            params = attack.to_attack_parameters()

            # Should have required fields for provenance logging
            assert "cipher_type" in params
            assert "key_or_params" in params
            assert "additional_params" in params

            # Source should be tracked
            if attack.source_paper:
                assert "academic:" in params["additional_params"]["source"]
