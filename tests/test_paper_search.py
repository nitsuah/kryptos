"""Tests for academic paper search functionality."""

from kryptos.research.paper_search import Paper, PaperSearch


class TestPaper:
    """Test Paper dataclass."""

    def test_create_paper(self):
        """Test creating a paper."""
        paper = Paper(
            paper_id="arxiv:1234.5678",
            title="Test Paper",
            authors=["Smith, J.", "Jones, A."],
            abstract="This is a test abstract.",
            year=2020,
        )

        assert paper.paper_id == "arxiv:1234.5678"
        assert len(paper.authors) == 2
        assert paper.year == 2020

    def test_paper_to_dict(self):
        """Test converting paper to dictionary."""
        paper = Paper(
            paper_id="test:123",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            year=2020,
            keywords=["crypto", "vigenere"],
        )

        d = paper.to_dict()
        assert d["paper_id"] == "test:123"
        assert "crypto" in d["keywords"]

    def test_paper_from_dict(self):
        """Test creating paper from dictionary."""
        data = {
            "paper_id": "test:456",
            "title": "Test Paper",
            "authors": ["Author A"],
            "abstract": "Test abstract",
            "year": 2021,
            "venue": None,
            "url": None,
            "pdf_url": None,
            "keywords": [],
            "cipher_types": [],
            "relevance_score": 0.0,
        }

        paper = Paper.from_dict(data)
        assert paper.paper_id == "test:456"
        assert paper.year == 2021


class TestPaperSearch:
    """Test paper search functionality."""

    def test_initialization(self, tmp_path):
        """Test searcher initialization."""
        searcher = PaperSearch(cache_dir=tmp_path)
        assert searcher.cache_dir == tmp_path
        assert searcher.cache_dir.exists()

    def test_arxiv_search(self, tmp_path):
        """Test arXiv search."""
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_arxiv("vigenere", max_results=5)

        assert isinstance(papers, list)
        assert all(isinstance(p, Paper) for p in papers)

    def test_iacr_search(self, tmp_path):
        """Test IACR search."""
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_iacr("transposition", max_results=5)

        assert isinstance(papers, list)
        assert all(isinstance(p, Paper) for p in papers)

    def test_combined_search(self, tmp_path):
        """Test combined search deduplication."""
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_combined("vigenere", max_results_per_source=5)

        assert isinstance(papers, list)
        # Should be sorted by relevance
        if len(papers) > 1:
            assert papers[0].relevance_score >= papers[-1].relevance_score

    def test_kryptos_search(self, tmp_path):
        """Test Kryptos-specific search."""
        searcher = PaperSearch(cache_dir=tmp_path)
        papers = searcher.search_kryptos_specific()

        assert isinstance(papers, list)
        # Should find some Kryptos papers
        if papers:
            assert any("kryptos" in p.title.lower() for p in papers)

    def test_relevance_calculation(self, tmp_path):
        """Test relevance scoring."""
        searcher = PaperSearch(cache_dir=tmp_path)

        paper = Paper(
            paper_id="test:123",
            title="Vigenere Cipher Cryptanalysis",
            authors=["Test"],
            abstract="Methods for breaking vigenere ciphers using frequency analysis.",
            year=2020,
            keywords=["vigenere", "cryptanalysis"],
        )

        score = searcher._calculate_relevance(paper, "vigenere cryptanalysis")
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high relevance

    def test_title_normalization(self, tmp_path):
        """Test title normalization for deduplication."""
        searcher = PaperSearch(cache_dir=tmp_path)

        title1 = "Breaking Vigenère Ciphers: A Modern Approach"
        title2 = "Breaking Vigenere Ciphers A Modern Approach"

        norm1 = searcher._normalize_title(title1)
        norm2 = searcher._normalize_title(title2)

        assert norm1 == norm2  # Should be same after normalization

    def test_cache_persistence(self, tmp_path):
        """Test search result caching."""
        searcher1 = PaperSearch(cache_dir=tmp_path)

        # First search (creates cache)
        papers1 = searcher1.search_arxiv("vigenere", max_results=3)

        # Second searcher (should load from cache)
        searcher2 = PaperSearch(cache_dir=tmp_path)
        papers2 = searcher2.search_arxiv("vigenere", max_results=3)

        # Should get same results from cache
        assert len(papers1) == len(papers2)
        assert papers1[0].paper_id == papers2[0].paper_id


class TestIntegration:
    """Integration tests for paper search."""

    def test_search_and_score_workflow(self, tmp_path):
        """Test complete search workflow."""
        searcher = PaperSearch(cache_dir=tmp_path)

        # Search for papers
        papers = searcher.search_combined("vigenere cryptanalysis", max_results_per_source=10)

        # Should have results
        assert len(papers) > 0

        # Should be scored
        assert all(hasattr(p, "relevance_score") for p in papers)

        # Should be sorted by relevance
        for i in range(len(papers) - 1):
            assert papers[i].relevance_score >= papers[i + 1].relevance_score
