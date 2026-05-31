from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

import kryptos.agents.spy_web_intel as web


@pytest.mark.skipif(not web.WEB_AVAILABLE, reason="web intel dependencies unavailable")
def test_gather_intelligence_paths(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    intel = web.SpyWebIntel(cache_dir=tmp_path)

    now = datetime.now()
    intel.sources = [
        web.IntelSource("official", "u1", "official", "daily", last_scraped=None, active=True),
        web.IntelSource("forum", "u2", "forum", "daily", last_scraped=None, active=True),
        web.IntelSource("inactive", "u3", "official", "daily", last_scraped=None, active=False),
        web.IntelSource("other", "u4", "academic", "daily", last_scraped=now - timedelta(days=3), active=True),
        web.IntelSource("boom", "u5", "official", "daily", last_scraped=None, active=True),
    ]

    crib = web.CribCandidate(
        text="BERLIN",
        confidence=0.9,
        source="s",
        context="c",
        discovered_date=now,
        category="location",
    )

    monkeypatch.setattr(intel, "_should_skip_scrape", lambda src: src.name == "forum")
    monkeypatch.setattr(intel, "_scrape_forum", lambda _src: [crib])

    def _official(src):
        if src.name == "boom":
            raise RuntimeError("x")
        return [crib]

    monkeypatch.setattr(intel, "_scrape_official_page", _official)

    out = intel.gather_intelligence(force_refresh=False)
    assert out["new_cribs"]
    assert any("Failed to scrape" in u for u in out["updates"])

    out2 = intel.gather_intelligence(force_refresh=True)
    assert "timestamp" in out2


@pytest.mark.skipif(not web.WEB_AVAILABLE, reason="web intel dependencies unavailable")
def test_search_extract_top_and_scrape_helpers(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    intel = web.SpyWebIntel(cache_dir=tmp_path)

    class _Resp:
        text = (
            '<div class="result"><a class="result__a" href="u">Title</a>'
            '<a class="result__snippet">Snippet text</a></div>'
        )

    monkeypatch.setattr(web.requests, "get", lambda *args, **kwargs: _Resp())
    results = intel.search_sanborn_intel("kryptos interview")
    assert results and results[0]["title"] == "Title"

    monkeypatch.setattr(web.requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("net")))
    assert intel.search_sanborn_intel("kryptos") == []

    text = (
        'Sanborn said "NORTHEAST" near BERLIN CLOCK and 52 degrees north. '
        'A second quote is "CLOCK".'
    )
    cribs = intel.extract_potential_cribs(text)
    assert any(c.text == "NORTHEAST" for c in cribs)
    assert any(c.category == "location" for c in cribs)
    assert any(c.source == "coordinate_reference" for c in cribs)

    intel.discovered_cribs.extend(cribs)
    tops = intel.get_top_cribs(min_confidence=0.6)
    assert tops
    loc_tops = intel.get_top_cribs(min_confidence=0.6, category="location")
    assert all(t in tops for t in loc_tops)

    # _scrape_official_page success + failure branches
    class _Resp2:
        text = '<html><body>Text with "BERLIN" and CLOCK</body></html>'

    monkeypatch.setattr(web.requests, "get", lambda *args, **kwargs: _Resp2())
    src = web.IntelSource("off", "http://example", "official", "daily")
    got = intel._scrape_official_page(src)
    assert isinstance(got, list)

    monkeypatch.setattr(web.requests, "get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("bad")))
    got2 = intel._scrape_official_page(src)
    assert got2 == []

    assert intel._scrape_forum(src) == []


@pytest.mark.skipif(not web.WEB_AVAILABLE, reason="web intel dependencies unavailable")
def test_skip_logic_cache_error_and_demo(tmp_path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    intel = web.SpyWebIntel(cache_dir=tmp_path)

    src = web.IntelSource("x", "u", "official", "daily", last_scraped=datetime.now() - timedelta(hours=1))
    assert intel._should_skip_scrape(src) is True
    src2 = web.IntelSource("y", "u", "official", "weekly", last_scraped=datetime.now() - timedelta(hours=200))
    assert intel._should_skip_scrape(src2) is False
    src3 = web.IntelSource("z", "u", "official", "unknown", last_scraped=datetime.now() - timedelta(hours=2))
    assert intel._should_skip_scrape(src3) is True

    # Force cache load error branches with bad json.
    (tmp_path / "cribs.json").write_text("{bad", encoding="utf-8")
    (tmp_path / "processed_hashes.json").write_text("{bad", encoding="utf-8")
    intel2 = web.SpyWebIntel(cache_dir=tmp_path)
    assert isinstance(intel2.discovered_cribs, list)

    # Save path
    intel2.discovered_cribs = [
        web.CribCandidate("BERLIN", 0.9, "s", "c", datetime.now(), "location", {}),
    ]
    intel2._save_cache()
    assert json.loads((tmp_path / "cribs.json").read_text(encoding="utf-8"))

    # demo branches for WEB_AVAILABLE false/true.
    monkeypatch.setattr(web, "WEB_AVAILABLE", False)
    web.demo_web_intel()
    assert "Install dependencies" in capsys.readouterr().out

    monkeypatch.setattr(web, "WEB_AVAILABLE", True)

    class _Intel:
        def search_sanborn_intel(self, _query):
            return [{"title": "t", "snippet": "s", "url": "u"}]

        def extract_potential_cribs(self, _text):
            return [web.CribCandidate("BERLIN", 0.9, "s", "c", datetime.now(), "location", {})]

    monkeypatch.setattr(web, "SpyWebIntel", lambda *args, **kwargs: _Intel())
    web.demo_web_intel()
    out = capsys.readouterr().out
    assert "SPY WEB INTELLIGENCE DEMO" in out
