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

from kryptos.paths import get_artifacts_root

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
    name: str
    url: str
    source_type: str  # 'news', 'forum', 'academic', 'official'
    scrape_frequency: str
    last_scraped: datetime | None = None
    active: bool = True


@dataclass
class CribCandidate:
    text: str
    confidence: float
    source: str
    context: str
    discovered_date: datetime
    category: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SpyWebIntel:
    def __init__(self, cache_dir: Path | None = None):
        if not WEB_AVAILABLE:
            raise ImportError("requests and beautifulsoup4 required. Install: pip install requests beautifulsoup4")

        self.cache_dir = cache_dir or (get_artifacts_root() / "intel_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.processed_content_hashes: set[str] = set()

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
        ]

        self.discovered_cribs: list[CribCandidate] = []
        self._load_cache()

    def gather_intelligence(self, force_refresh: bool = False) -> dict[str, Any]:
        results = {
            "new_cribs": [],
            "updates": [],
            "timestamp": datetime.now().isoformat(),
        }

        for source in self.sources:
            if not source.active:
                continue

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

        self.discovered_cribs.extend(results["new_cribs"])
        self._save_cache()

        return results

    def search_sanborn_intel(self, query: str = "sanborn kryptos interview") -> list[dict[str, str]]:
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

            return results[:10]

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def extract_potential_cribs(self, text: str) -> list[CribCandidate]:
        if not self._is_content_new(text):
            return []

        candidates = []

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

        cap_words = re.findall(r'\b([A-Z][a-z]{2,15})\b', text)
        location_keywords = {'berlin', 'clock', 'layer', 'east', 'north', 'west', 'south'}

        for word in set(cap_words):
            word_lower = word.lower()
            if word_lower in location_keywords:
                candidates.append(
                    CribCandidate(
                        text=word.upper(),
                        confidence=0.9,
                        source="proper_noun",
                        context=f"Capitalized in source: {word}",
                        discovered_date=datetime.now(),
                        category="location",
                    ),
                )

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
        filtered = [
            c
            for c in self.discovered_cribs
            if c.confidence >= min_confidence and (category is None or c.category == category)
        ]

        seen = set()
        unique_cribs = []
        for crib in sorted(filtered, key=lambda x: x.confidence, reverse=True):
            if crib.text not in seen:
                seen.add(crib.text)
                unique_cribs.append(crib.text)

        return unique_cribs

    def _scrape_official_page(self, source: IntelSource) -> list[CribCandidate]:
        try:
            response = requests.get(
                source.url,
                headers={"User-Agent": "Mozilla/5.0 (research bot)"},
                timeout=15,
            )
            soup = BeautifulSoup(response.text, "html.parser")

            page_text = soup.get_text()

            cribs = self.extract_potential_cribs(page_text)

            return cribs

        except Exception as e:
            print(f"Failed to scrape {source.url}: {e}")
            return []

    def _scrape_forum(self, source: IntelSource) -> list[CribCandidate]:
        return []

    def _should_skip_scrape(self, source: IntelSource) -> bool:
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
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _is_content_new(self, content: str) -> bool:
        content_hash = self._content_hash(content)
        if content_hash in self.processed_content_hashes:
            return False
        self.processed_content_hashes.add(content_hash)
        return True

    def _load_cache(self):
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

        hashes_file = self.cache_dir / "processed_hashes.json"
        if hashes_file.exists():
            try:
                with open(hashes_file) as f:
                    self.processed_content_hashes = set(json.load(f))
            except Exception as e:
                print(f"Failed to load processed hashes: {e}")

    def _save_cache(self):
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

        hashes_file = self.cache_dir / "processed_hashes.json"
        try:
            with open(hashes_file, "w") as f:
                json.dump(list(self.processed_content_hashes), f, indent=2)
        except Exception as e:
            print(f"Failed to save processed hashes: {e}")


def demo_web_intel():
    if not WEB_AVAILABLE:
        print("Install dependencies: pip install requests beautifulsoup4")
        return

    print("=" * 80)
    print("SPY WEB INTELLIGENCE DEMO")
    print("=" * 80)
    print()

    intel = SpyWebIntel()

    print("🔍 Searching for Sanborn interviews...")
    results = intel.search_sanborn_intel("jim sanborn kryptos interview 2020")

    print(f"Found {len(results)} search results:\n")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['snippet'][:100]}...")
        print(f"   {result['url']}")
        print()

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
