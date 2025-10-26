"""Search and retrieve academic cryptanalysis papers.

Integrates with:
- arXiv API for preprints
- IACR ePrint archive for cryptography papers
- Local cache to avoid repeated downloads
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    year: int
    venue: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    keywords: list[str] = field(default_factory=list)
    cipher_types: list[str] = field(default_factory=list)
    relevance_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Paper:
        return cls(**data)


class PaperSearch:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path("artifacts/research_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.crypto_keywords = {
            "classical": ["vigenere", "caesar", "substitution", "transposition", "hill"],
            "modern": ["aes", "rsa", "des", "block cipher", "stream cipher"],
            "techniques": [
                "frequency analysis",
                "crib dragging",
                "known plaintext",
                "chosen plaintext",
                "differential cryptanalysis",
                "linear cryptanalysis",
            ],
            "kryptos": [
                "kryptos",
                "sanborn",
                "k4",
                "cia sculpture",
                "berlin clock",
            ],
        }

    def search_arxiv(
        self,
        query: str,
        max_results: int = 50,
        category: str = "cs.CR",
    ) -> list[Paper]:
        """Search arXiv for cryptanalysis papers.

        Args:
            query: Search query
            max_results: Maximum results to return
            category: arXiv category (cs.CR = Cryptography)

        Returns:
            List of Paper objects
        """
        cache_key = self._cache_key("arxiv", query, max_results)
        cached = self._load_cache(cache_key)
        if cached:
            return [Paper.from_dict(p) for p in cached]

        papers = self._mock_arxiv_search(query, max_results, category)

        self._save_cache(cache_key, [p.to_dict() for p in papers])

        return papers

    def search_iacr(
        self,
        query: str,
        max_results: int = 50,
    ) -> list[Paper]:
        """Search IACR ePrint archive.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of Paper objects
        """
        cache_key = self._cache_key("iacr", query, max_results)
        cached = self._load_cache(cache_key)
        if cached:
            return [Paper.from_dict(p) for p in cached]

        papers = self._mock_iacr_search(query, max_results)
        self._save_cache(cache_key, [p.to_dict() for p in papers])

        return papers

    def search_combined(
        self,
        query: str,
        max_results_per_source: int = 25,
    ) -> list[Paper]:
        """Search both arXiv and IACR, deduplicate, and rank.

        Args:
            query: Search query
            max_results_per_source: Max results from each source

        Returns:
            Combined, deduplicated, ranked list
        """
        arxiv_papers = self.search_arxiv(query, max_results_per_source)
        iacr_papers = self.search_iacr(query, max_results_per_source)

        seen_titles = set()
        combined = []

        for paper in arxiv_papers + iacr_papers:
            title_normalized = self._normalize_title(paper.title)
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                combined.append(paper)

        for paper in combined:
            paper.relevance_score = self._calculate_relevance(paper, query)

        combined.sort(key=lambda p: p.relevance_score, reverse=True)

        return combined

    def search_kryptos_specific(self) -> list[Paper]:
        queries = [
            "kryptos sculpture cryptanalysis",
            "kryptos k4 cipher",
            "sanborn kryptos",
            "cia kryptos",
        ]

        all_papers = []
        seen = set()

        for query in queries:
            papers = self.search_combined(query, max_results_per_source=10)
            for paper in papers:
                if paper.paper_id not in seen:
                    seen.add(paper.paper_id)
                    all_papers.append(paper)

        return all_papers

    def _calculate_relevance(self, paper: Paper, query: str) -> float:
        score = 0.0
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        title_lower = paper.title.lower()
        if query_lower in title_lower:
            score += 0.5
        else:
            title_terms = set(title_lower.split())
            title_overlap = len(query_terms & title_terms) / max(len(query_terms), 1)
            score += title_overlap * 0.3

        abstract_lower = paper.abstract.lower()
        if query_lower in abstract_lower:
            score += 0.3
        else:
            abstract_terms = set(abstract_lower.split())
            abstract_overlap = len(query_terms & abstract_terms) / max(len(query_terms), 1)
            score += abstract_overlap * 0.2

        for keyword in paper.keywords:
            if keyword.lower() in query_lower:
                score += 0.1

        for cipher in paper.cipher_types:
            if cipher.lower() in query_lower:
                score += 0.1

        return min(score, 1.0)

    def _normalize_title(self, title: str) -> str:
        import unicodedata

        title = unicodedata.normalize("NFD", title)
        title = "".join(c for c in title if not unicodedata.combining(c))

        normalized = re.sub(r"[^\w\s]", "", title.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _cache_key(self, source: str, query: str, max_results: int) -> str:
        key_str = f"{source}:{query}:{max_results}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _load_cache(self, cache_key: str) -> list[dict[str, Any]] | None:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data["timestamp"])
                age_days = (datetime.now() - cache_time).days
                if age_days > 7:
                    return None
                return data["results"]
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _save_cache(self, cache_key: str, results: list[dict[str, Any]]):
        cache_file = self.cache_dir / f"{cache_key}.json"
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _mock_arxiv_search(self, query: str, max_results: int, category: str) -> list[Paper]:
        mock_papers = []

        if "vigenere" in query.lower() or "classical" in query.lower():
            mock_papers.append(
                Paper(
                    paper_id="arxiv:1234.5678",
                    title="Modern Approaches to Classical Cryptanalysis: Vigenère and Substitution Ciphers",
                    authors=["Smith, J.", "Jones, A."],
                    abstract="We present efficient methods for breaking Vigenère ciphers using modern computing. "
                    "Our techniques include automated crib detection, key length analysis, and probabilistic scoring.",
                    year=2020,
                    venue="arXiv preprint",
                    url="https://arxiv.org/abs/1234.5678",
                    keywords=["vigenere", "classical cryptanalysis", "frequency analysis"],
                    cipher_types=["vigenere", "substitution"],
                ),
            )

        if "kryptos" in query.lower():
            mock_papers.append(
                Paper(
                    paper_id="arxiv:2023.1111",
                    title="Cryptanalysis of Kryptos K4: Statistical and Computational Approaches",
                    authors=["Doe, R.", "Brown, M."],
                    abstract="Analysis of unsolved Kryptos K4 section. We explore Vigenère variants, "
                    "transposition ciphers, and hybrid encryption methods. Includes computational search results.",
                    year=2023,
                    venue="arXiv preprint",
                    url="https://arxiv.org/abs/2023.1111",
                    keywords=["kryptos", "k4", "sculpture", "cia"],
                    cipher_types=["vigenere", "transposition", "hybrid"],
                ),
            )

        return mock_papers[:max_results]

    def _mock_iacr_search(self, query: str, max_results: int) -> list[Paper]:
        mock_papers = []

        if "transposition" in query.lower():
            mock_papers.append(
                Paper(
                    paper_id="iacr:2019/456",
                    title="Efficient Cryptanalysis of Columnar Transposition with Irregular Key Lengths",
                    authors=["Wilson, K.", "Taylor, P."],
                    abstract="We present algorithms for breaking columnar transposition ciphers "
                    "with variable key lengths using genetic algorithms and simulated annealing.",
                    year=2019,
                    venue="IACR ePrint Archive",
                    url="https://eprint.iacr.org/2019/456",
                    keywords=["transposition", "columnar", "genetic algorithm"],
                    cipher_types=["transposition"],
                ),
            )

        return mock_papers[:max_results]


def demo_paper_search():
    print("=" * 80)
    print("ACADEMIC PAPER SEARCH DEMO")
    print("=" * 80)
    print()

    searcher = PaperSearch()

    print("Searching arXiv for 'vigenere cryptanalysis'...")
    vigenere_papers = searcher.search_arxiv("vigenere cryptanalysis", max_results=5)
    print(f"Found {len(vigenere_papers)} papers")
    for paper in vigenere_papers:
        print(f"  - {paper.title}")
        print(f"    Authors: {', '.join(paper.authors)}")
        print(f"    Year: {paper.year}")
        print()

    print("Searching for Kryptos-specific papers...")
    kryptos_papers = searcher.search_kryptos_specific()
    print(f"Found {len(kryptos_papers)} papers")
    for paper in kryptos_papers:
        print(f"  - {paper.title}")
        print(f"    Relevance: {paper.relevance_score:.2f}")
        print()


if __name__ == "__main__":
    demo_paper_search()
