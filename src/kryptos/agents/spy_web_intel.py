"""SPY Web Intelligence Module: Dynamic Crib Discovery & External Intel.

This module enables SPY to autonomously gather intelligence from external sources:
- Kryptos community updates (elonka.com, forums, social media)
- Jim Sanborn interviews and public statements
- Academic papers and new cryptanalysis techniques
- Historical context for contextual cribs

Philosophy: The best cribs aren't static - they're discovered through continuous
monitoring of the Kryptos ecosystem.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
    from bs4 import BeautifulSoup

    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    requests = None
    BeautifulSoup = None


@dataclass
class IntelSource:
    """An external intelligence source."""

    name: str
    url: str
    source_type: str  # 'news', 'forum', 'academic', 'official'
    scrape_frequency: str  # 'daily', 'weekly', 'monthly'
    last_scraped: datetime | None = None
    active: bool = True


@dataclass
class CribCandidate:
    """A potential plaintext word/phrase discovered from external sources."""

    text: str
    confidence: float  # 0.0-1.0
    source: str
    context: str
    discovered_date: datetime
    category: str  # 'location', 'person', 'theme', 'technical', 'confirmed'
    metadata: dict[str, Any] = field(default_factory=dict)


class SpyWebIntel:
    """Autonomous intelligence gathering for SPY agent.

    This is like having a research assistant who:
    - Reads every Kryptos forum post
    - Watches for Sanborn interviews
    - Tracks academic breakthroughs
    - Monitors the CIA Kryptos page
    """

    def __init__(self, cache_dir: Path | None = None):
        """Initialize web intelligence system.

        Args:
            cache_dir: Directory to cache scraped data (default: ./data/intel_cache)
        """
        if not WEB_AVAILABLE:
            raise ImportError("requests and beautifulsoup4 required. Install: pip install requests beautifulsoup4")

        self.cache_dir = cache_dir or Path("./data/intel_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track content we've already processed to avoid redundant work
        self.processed_content_hashes: set[str] = set()

        # Define intelligence sources
        self.sources = [
            IntelSource(
                name="Elonka Kryptos Page",
                url="https://elonka.com/kryptos/",
                source_type="official",
                scrape_frequency="daily",
            ),
            IntelSource(
                name="CIA Kryptos",
                url="https://www.cia.gov/stories/story/kryptos/",
                source_type="official",
                scrape_frequency="weekly",
            ),
            IntelSource(
                name="Reddit r/codes",
                url="https://www.reddit.com/r/codes/search/?q=kryptos",
                source_type="forum",
                scrape_frequency="daily",
            ),
            # Add more as we discover them
        ]

        self.discovered_cribs: list[CribCandidate] = []
        self._load_cache()

    def gather_intelligence(self, force_refresh: bool = False) -> dict[str, Any]:
        """Gather intelligence from all active sources.

        Args:
            force_refresh: Ignore cache and scrape everything fresh

        Returns:
            Dict with discovered cribs, updates, and insights
        """
        results = {
            "new_cribs": [],
            "updates": [],
            "timestamp": datetime.now().isoformat(),
        }

        for source in self.sources:
            if not source.active:
                continue

            # Check if we need to scrape based on frequency
            if not force_refresh and self._should_skip_scrape(source):
                continue

            try:
                if source.source_type == "official":
                    cribs = self._scrape_official_page(source)
                elif source.source_type == "forum":
                    cribs = self._scrape_forum(source)
                else:
                    continue

                results["new_cribs"].extend(cribs)
                source.last_scraped = datetime.now()

            except Exception as e:
                results["updates"].append(f"Failed to scrape {source.name}: {e}")

        # Update our crib database
        self.discovered_cribs.extend(results["new_cribs"])
        self._save_cache()

        return results

    def search_sanborn_intel(self, query: str = "sanborn kryptos interview") -> list[dict[str, str]]:
        """Search for Sanborn interviews and statements.

        This is GOLD - Sanborn has dropped hints over the years that became
        crucial cribs (like NORTHEAST in 2020).

        Args:
            query: Search query

        Returns:
            List of search results with URLs and snippets
        """
        # Use DuckDuckGo HTML search (no API key needed)
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        try:
            response = requests.get(
                search_url,
                headers={"User-Agent": "Mozilla/5.0 (research bot for academic cryptanalysis)"},
                timeout=10,
            )

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for result in soup.find_all("div", class_="result"):
                title_elem = result.find("a", class_="result__a")
                snippet_elem = result.find("a", class_="result__snippet")

                if title_elem and snippet_elem:
                    results.append(
                        {
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get("href", ""),
                            "snippet": snippet_elem.get_text(strip=True),
                        },
                    )

            return results[:10]  # Top 10 results

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def extract_potential_cribs(self, text: str) -> list[CribCandidate]:
        """Extract potential cribs from text using heuristics.

        Looks for:
        - Capitalized words (proper nouns)
        - Location names
        - Dates/times
        - Technical terms
        - Words Sanborn emphasizes (quotes, italics)

        Args:
            text: Text to analyze

        Returns:
            List of potential crib candidates
        """
        # Skip if we've already processed this content
        if not self._is_content_new(text):
            return []

        candidates = []

        # Pattern 1: Quoted text (Sanborn quotes are often hints)
        quotes = re.findall(r'"([^"]{3,30})"', text)
        for quote in quotes:
            if quote.isupper() or quote[0].isupper():
                candidates.append(
                    CribCandidate(
                        text=quote.upper(),
                        confidence=0.7,
                        source="quoted_text",
                        context=f"Found in quotes: '{quote}'",
                        discovered_date=datetime.now(),
                        category="emphasized",
                    ),
                )

        # Pattern 2: Capitalized words (proper nouns)
        cap_words = re.findall(r'\b([A-Z][a-z]{2,15})\b', text)
        location_keywords = {'berlin', 'clock', 'layer', 'east', 'north', 'west', 'south'}

        for word in set(cap_words):
            word_lower = word.lower()
            if word_lower in location_keywords:
                candidates.append(
                    CribCandidate(
                        text=word.upper(),
                        confidence=0.9,  # High confidence for known location words
                        source="proper_noun",
                        context=f"Capitalized in source: {word}",
                        discovered_date=datetime.now(),
                        category="location",
                    ),
                )

        # Pattern 3: Direction/coordinates mentions (Sanborn loves coordinates)
        coord_patterns = [
            r'(\d+)\s*degrees',
            r'(north|south|east|west|northeast|northwest|southeast|southwest)',
            r'latitude|longitude',
        ]

        for pattern in coord_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and len(match) > 2:
                    candidates.append(
                        CribCandidate(
                            text=match.upper(),
                            confidence=0.8,
                            source="coordinate_reference",
                            context="Found in coordinate/direction context",
                            discovered_date=datetime.now(),
                            category="location",
                        ),
                    )

        return candidates

    def get_top_cribs(self, min_confidence: float = 0.6, category: str | None = None) -> list[str]:
        """Get highest confidence cribs for use in attacks.

        Args:
            min_confidence: Minimum confidence threshold
            category: Filter by category (location, person, theme, etc.)

        Returns:
            List of crib strings sorted by confidence
        """
        filtered = [
            c
            for c in self.discovered_cribs
            if c.confidence >= min_confidence and (category is None or c.category == category)
        ]

        # Sort by confidence, deduplicate
        seen = set()
        unique_cribs = []
        for crib in sorted(filtered, key=lambda x: x.confidence, reverse=True):
            if crib.text not in seen:
                seen.add(crib.text)
                unique_cribs.append(crib.text)

        return unique_cribs

    def _scrape_official_page(self, source: IntelSource) -> list[CribCandidate]:
        """Scrape official Kryptos pages for updates."""
        try:
            response = requests.get(
                source.url,
                headers={"User-Agent": "Mozilla/5.0 (research bot)"},
                timeout=15,
            )
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract all text
            page_text = soup.get_text()

            # Look for updates about K4
            cribs = self.extract_potential_cribs(page_text)

            return cribs

        except Exception as e:
            print(f"Failed to scrape {source.url}: {e}")
            return []

    def _scrape_forum(self, source: IntelSource) -> list[CribCandidate]:
        """Scrape forum discussions for community insights."""
        # Forums are trickier - would need specific parsers for each
        # For now, return empty - we can add specific forum parsers later
        return []

    def _should_skip_scrape(self, source: IntelSource) -> bool:
        """Check if we should skip scraping based on frequency."""
        if source.last_scraped is None:
            return False

        hours_since = (datetime.now() - source.last_scraped).total_seconds() / 3600

        frequency_hours = {
            "daily": 24,
            "weekly": 168,
            "monthly": 720,
        }

        threshold = frequency_hours.get(source.scrape_frequency, 24)
        return hours_since < threshold

    def _content_hash(self, content: str) -> str:
        """Generate hash for content to detect duplicates."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _is_content_new(self, content: str) -> bool:
        """Check if we've already processed this content."""
        content_hash = self._content_hash(content)
        if content_hash in self.processed_content_hashes:
            return False
        self.processed_content_hashes.add(content_hash)
        return True

    def _load_cache(self):
        """Load cached intelligence and processed content hashes."""
        # Load cribs
        cache_file = self.cache_dir / "cribs.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    self.discovered_cribs = [
                        CribCandidate(
                            text=c["text"],
                            confidence=c["confidence"],
                            source=c["source"],
                            context=c["context"],
                            discovered_date=datetime.fromisoformat(c["discovered_date"]),
                            category=c["category"],
                            metadata=c.get("metadata", {}),
                        )
                        for c in data
                    ]
            except Exception as e:
                print(f"Failed to load cache: {e}")

        # Load processed content hashes
        hashes_file = self.cache_dir / "processed_hashes.json"
        if hashes_file.exists():
            try:
                with open(hashes_file) as f:
                    self.processed_content_hashes = set(json.load(f))
            except Exception as e:
                print(f"Failed to load processed hashes: {e}")

    def _save_cache(self):
        """Save intelligence and processed hashes to cache."""
        # Save cribs
        cache_file = self.cache_dir / "cribs.json"
        try:
            data = [
                {
                    "text": c.text,
                    "confidence": c.confidence,
                    "source": c.source,
                    "context": c.context,
                    "discovered_date": c.discovered_date.isoformat(),
                    "category": c.category,
                    "metadata": c.metadata,
                }
                for c in self.discovered_cribs
            ]

            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Failed to save cache: {e}")

        # Save processed content hashes
        hashes_file = self.cache_dir / "processed_hashes.json"
        try:
            with open(hashes_file, "w") as f:
                json.dump(list(self.processed_content_hashes), f, indent=2)
        except Exception as e:
            print(f"Failed to save processed hashes: {e}")


def demo_web_intel():
    """Demonstrate web intelligence gathering."""
    if not WEB_AVAILABLE:
        print("Install dependencies: pip install requests beautifulsoup4")
        return

    print("=" * 80)
    print("SPY WEB INTELLIGENCE DEMO")
    print("=" * 80)
    print()

    intel = SpyWebIntel()

    # Search for Sanborn intel
    print("🔍 Searching for Sanborn interviews...")
    results = intel.search_sanborn_intel("jim sanborn kryptos interview 2020")

    print(f"Found {len(results)} search results:\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['snippet'][:100]}...")
        print(f"   {result['url']}")
        print()

    # Extract cribs from sample text
    print("\n" + "=" * 80)
    print("📝 Testing crib extraction...")
    sample_text = """
    Jim Sanborn revealed in 2020 that characters 26-34 of K4 are "NORTHEAST".
    The sculpture is located at coordinates near the CIA headquarters in Langley.
    Sanborn said "BERLIN" appears in K3 and relates to the "CLOCK" theme.
    """

    cribs = intel.extract_potential_cribs(sample_text)
    print(f"Extracted {len(cribs)} potential cribs:\n")
    for crib in cribs:
        print(f"  '{crib.text}' (conf: {crib.confidence:.2f}, category: {crib.category})")
        print(f"    Context: {crib.context}")
        print()


if __name__ == "__main__":
    demo_web_intel()
