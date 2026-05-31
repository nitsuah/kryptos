from __future__ import annotations

import json
import runpy
import sys

from kryptos.provenance import attack_log as al
from kryptos.provenance import search_space as ss


def test_search_space_load_tried_keys_and_demo(tmp_path, monkeypatch, capsys) -> None:
    cache_dir = tmp_path / "search"
    cache_dir.mkdir(parents=True, exist_ok=True)

    tried_file = cache_dir / "tried_keys.jsonl"
    tried_file.write_text('{"cipher_type": "vigenere", "key": "ABC"}\n{bad-json\n', encoding="utf-8")

    tracker = ss.SearchSpaceTracker(cache_dir=cache_dir)
    assert tracker.already_tried("vigenere", "ABC") is True

    tracker._record_tried_keys("vigenere", ["ABC", "XYZ", "XYZ"])
    tracker.mark_tried("vigenere", "NEW")
    tracker.mark_tried("vigenere", "NEW")

    monkeypatch.setattr(ss, "get_artifacts_root", lambda: tmp_path)
    ss.demo_search_space_tracker()
    out = capsys.readouterr().out
    assert "SEARCH SPACE TRACKER DEMO" in out
    assert "Recommendations:" in out


def test_attack_log_load_existing_and_demo(tmp_path, monkeypatch, capsys) -> None:
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    params = al.AttackParameters(cipher_type="vigenere", key_or_params={"key": "ABC"})
    result = al.AttackResult(success=True, confidence_scores={"SPY": 0.9})
    record = al.AttackRecord(
        attack_id="a1",
        timestamp=al.datetime.now(),
        ciphertext="XYZ",
        parameters=params,
        result=result,
    )

    log_file = log_dir / "attack_log.jsonl"
    log_file.write_text(json.dumps(record.to_dict()) + "\n" + "{bad-json\n", encoding="utf-8")

    logger = al.AttackLogger(log_dir=log_dir)
    assert logger.stats["total_attacks"] == 1
    assert logger.stats["successful_attacks"] == 1

    monkeypatch.setattr(al, "get_artifacts_root", lambda: tmp_path)
    al.demo_attack_logger()
    out = capsys.readouterr().out
    assert "ATTACK LOGGER DEMO" in out
    assert "Statistics:" in out


def test_provenance_modules_main_entrypoints() -> None:
    sys.modules.pop("kryptos.provenance.search_space", None)
    sys.modules.pop("kryptos.provenance.attack_log", None)
    runpy.run_module("kryptos.provenance.search_space", run_name="__main__")
    runpy.run_module("kryptos.provenance.attack_log", run_name="__main__")
