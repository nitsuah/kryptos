from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from kryptos import paths
from kryptos.pipeline.attack_generator import AttackGenerator
from kryptos.pipeline.k4_campaign import CampaignResult, demo_k4_campaign
from kryptos.pipeline.validator import demo_validator
from kryptos.provenance.attack_log import AttackLogger
from kryptos.research.attack_extractor import demo_attack_extractor
from kryptos.research.literature_bridge import LiteratureGapAnalyzer, demo_literature_gap_analysis
from kryptos.research.paper_search import PaperSearch, demo_paper_search
from kryptos.research.q_patterns import demo_q_research


def test_attack_generator_parse_and_seed_edge_cases(tmp_path: Path) -> None:
    logger = AttackLogger(log_dir=tmp_path / "logs")
    gen = AttackGenerator(attack_logger=logger)

    assert gen._parse_strategy_method("polyalphabetic", "vigenere_kx", "ABC") is None
    assert gen._parse_strategy_method("hybrid", "badformat", "ABC") is None
    assert gen._parse_strategy_method("unknown", "anything", "ABC") is None

    assert gen._parse_region_key("bad") == {}
    assert gen._parse_region_key("key_length_no-range") == {}
    assert gen._parse_region_key("period_bad-x") == {}

    assert gen._generate_seed_attacks("hill", "ABC", max_attacks=5) == []
    assert gen._generate_gap_filling_attacks("vigenere", "bad", 20.0, "ABC", max_attacks=5) == []


def test_attack_generator_no_regions_and_parse_failures(tmp_path: Path) -> None:
    logger = AttackLogger(log_dir=tmp_path / "logsx")
    gen = AttackGenerator(attack_logger=logger)

    class _TrackerNoRegions:
        def get_coverage_report(self, _cipher_type: str):
            return {"cipher_types": {"vigenere": {"regions": []}}}

    gen.coverage_analyzer.tracker = _TrackerNoRegions()  # type: ignore[assignment]
    attacks = gen.generate_from_coverage_gaps("vigenere", "OBKRUOX", max_attacks=3)
    assert len(attacks) == 3

    assert gen._parse_strategy_method("polyalphabetic", "vigenere_k", "ABC") is None
    assert gen._parse_strategy_method("polyalphabetic", "vigenere_kbad", "ABC") is None


def test_attack_generator_literature_and_export(tmp_path: Path) -> None:
    logger = AttackLogger(log_dir=tmp_path / "logs")
    gen = AttackGenerator(attack_logger=logger)

    no_attack = gen._literature_to_attacks({"cipher_type": "unknown"}, "ABC")
    assert no_attack == []

    recs = [
        {
            "cipher_type": "vigenere",
            "parameters": {"key_length": 8},
            "confidence": 0.7,
            "paper_title": "Paper A",
        },
        {
            "cipher_type": "transposition",
            "parameters": {"period": 7, "method": "columnar"},
            "confidence": 0.5,
            "paper_title": "Paper B",
        },
    ]
    attacks = gen.generate_from_literature(recs, "OBKRUOX", max_attacks=10)
    assert len(attacks) == 2
    assert attacks[0].priority >= attacks[1].priority

    out_file = tmp_path / "queue" / "attacks.json"
    gen.export_queue(attacks, out_file)
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["total_attacks"] == 2
    assert "statistics" in data
    assert "attacks" in data


def test_paper_search_cache_and_demo_paths(tmp_path: Path, capsys) -> None:
    searcher = PaperSearch(cache_dir=tmp_path / "cache")

    key = searcher._cache_key("arxiv", "vigenere", 3)
    cache_file = searcher.cache_dir / f"{key}.json"

    cache_file.write_text("{ not-json }", encoding="utf-8")
    assert searcher._load_cache(key) is None

    stale = {
        "timestamp": (datetime.now() - timedelta(days=10)).isoformat(),
        "results": [],
    }
    cache_file.write_text(json.dumps(stale), encoding="utf-8")
    assert searcher._load_cache(key) is None

    live = {
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "paper_id": "x",
                "title": "t",
                "authors": ["a"],
                "abstract": "b",
                "year": 2024,
                "venue": None,
                "url": None,
                "pdf_url": None,
                "keywords": [],
                "cipher_types": [],
                "relevance_score": 0.0,
            }
        ],
    }
    cache_file.write_text(json.dumps(live), encoding="utf-8")
    loaded = searcher._load_cache(key)
    assert loaded and loaded[0]["paper_id"] == "x"

    demo_paper_search()
    out = capsys.readouterr().out
    assert "ACADEMIC PAPER SEARCH DEMO" in out


def test_research_demo_functions_and_literature_report(tmp_path: Path, capsys) -> None:
    demo_q_research()
    out1 = capsys.readouterr().out
    assert "Q-RESEARCH ANALYZER DEMO" in out1

    demo_attack_extractor()
    out2 = capsys.readouterr().out
    assert "ATTACK EXTRACTION DEMO" in out2

    analyzer = LiteratureGapAnalyzer(attack_logger=AttackLogger(log_dir=tmp_path / "log2"))
    report = analyzer.generate_coverage_report(["vigenere", "kryptos"], "OBKRUOXOGHULBSO")
    assert "top_gaps" in report
    assert report["total_papers"] >= 0

    demo_literature_gap_analysis()
    out3 = capsys.readouterr().out
    assert "LITERATURE GAP ANALYSIS DEMO" in out3


def test_comprehensive_queue_custom_gap_report(tmp_path: Path) -> None:
    logger = AttackLogger(log_dir=tmp_path / "log3")
    gen = AttackGenerator(attack_logger=logger)

    class _Tracker:
        def get_coverage_report(self, _cipher_type: str):
            return {
                "cipher_types": {
                    "vigenere": {
                        "regions": [
                            {"region": "key_length_5-7", "coverage_percent": 10.0},
                            {"region": "key_length_8-10", "coverage_percent": 95.0},
                        ],
                    },
                    "transposition": {
                        "regions": [
                            {"region": "period_6-8", "coverage_percent": 20.0},
                        ],
                    },
                }
            }

    gen.coverage_analyzer.tracker = _Tracker()  # type: ignore[assignment]

    queue = gen.generate_comprehensive_queue(
        "OBKRUOXOGHULBSO", cipher_types=["vigenere", "transposition"], max_total=50
    )  # noqa: E501
    assert queue
    assert len(queue) <= 50

    seen = set()
    for item in queue:
        fp = item.fingerprint()
        assert fp not in seen
        seen.add(fp)

    stats = gen.get_statistics()
    assert "deduplication_rate" in stats


def test_paths_provenance_info_branches(monkeypatch, tmp_path: Path) -> None:
    paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setenv(paths.ENV_ROOT, str(tmp_path))

    class _Res:
        def __init__(self, code: int, out: str = ""):
            self.returncode = code
            self.stdout = out

    calls = [
        _Res(1, ""),
        _Res(0, "main\n"),
        _Res(0, "M x\n"),
    ]

    def _run(*args, **kwargs):
        _ = args
        _ = kwargs
        return calls.pop(0)

    monkeypatch.setattr(paths.subprocess, "run", _run)
    info = paths.get_provenance_info(include_params={"x": 1})
    assert info["git_commit"] is None
    assert info["git_branch"] == "main"
    assert info["git_dirty"] is True
    assert info["params"] == {"x": 1}

    def _raise(*args, **kwargs):
        _ = args
        _ = kwargs
        raise paths.subprocess.TimeoutExpired(cmd="git", timeout=1)

    monkeypatch.setattr(paths.subprocess, "run", _raise)
    info2 = paths.get_provenance_info()
    assert info2["git_commit"] is None
    assert info2["git_branch"] is None
    assert info2["git_dirty"] is None


def test_paths_repo_root_fallback(monkeypatch, tmp_path: Path) -> None:
    paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.delenv(paths.ENV_ROOT, raising=False)

    fake_file = tmp_path / "pkg" / "paths.py"
    fake_file.parent.mkdir(parents=True, exist_ok=True)
    fake_file.write_text("# placeholder", encoding="utf-8")
    monkeypatch.setattr(paths, "__file__", str(fake_file))
    monkeypatch.setattr(paths, "_find_repo_root", lambda *args, **kwargs: None)

    try:
        root = paths.get_repo_root()
        assert root == fake_file.resolve().parents[1]
    finally:
        paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]


def test_validator_and_campaign_demos(monkeypatch, capsys) -> None:
    demo_validator()
    out = capsys.readouterr().out
    assert "PLAINTEXT VALIDATOR DEMO" in out

    class _FakeOrchestrator:
        def __init__(self, workspace_dir=None):
            self.workspace_dir = workspace_dir

        def run_campaign(self, ciphertext, max_attacks=20, max_time_seconds=60):
            _ = ciphertext
            _ = max_attacks
            _ = max_time_seconds
            now = datetime.now()
            return CampaignResult(
                campaign_id="demo",
                start_time=now,
                end_time=now,
                total_attacks=1,
                successful_attacks=1,
                best_candidates=[{"confidence": 1.0, "cipher_type": "vigenere", "parameters": {}, "plaintext": "TEXT"}],
                coverage_report={},
                statistics={"duration_seconds": 0.0, "attacks_per_second": 1.0},
            )

        def print_summary(self, result):
            _ = result

    monkeypatch.setattr("kryptos.pipeline.k4_campaign.K4CampaignOrchestrator", _FakeOrchestrator)
    demo_k4_campaign()
