from __future__ import annotations

import runpy
import sys

import pytest

from kryptos.provenance.attack_log import AttackLogger, AttackParameters, AttackResult
from kryptos.provenance.search_space import KeySpaceRegion, SearchSpaceTracker
from kryptos.tuning import spy_eval


def test_sections_placeholder_callable_raises() -> None:
    import kryptos.sections as sections_mod

    with pytest.raises(NotImplementedError):
        sections_mod._k4_decrypt_placeholder("ABC")


def test_attack_logger_get_attack_none(tmp_path) -> None:
    logger = AttackLogger(log_dir=tmp_path)
    params = AttackParameters(cipher_type="vigenere", key_or_params={"k": "A"})
    logger.log_attack("XYZ", params, AttackResult(success=False))
    assert logger.get_attack("does-not-exist") is None


def test_search_space_small_missing_lines(tmp_path) -> None:
    region = KeySpaceRegion(cipher_type="vigenere", parameters={}, total_size=0)
    assert region.coverage_percent == 0.0

    cache = tmp_path / "ss"
    cache.mkdir(parents=True, exist_ok=True)

    # Corrupt cache file to hit JSON decode fallback.
    (cache / "search_space.json").write_text("{bad-json", encoding="utf-8")
    # Tried keys with blank line to hit continue path.
    (cache / "tried_keys.jsonl").write_text("\n" + '{"cipher_type":"vigenere","key":"ABC"}\n', encoding="utf-8")

    tracker = SearchSpaceTracker(cache_dir=cache)
    tracker.record_exploration("vigenere", "len_5", count=1, keys=["A"])
    assert tracker.get_coverage("missing_cipher") == 0.0

    tracker.register_region("vigenere", "len_0", {}, 0)
    assert tracker.get_coverage("vigenere") == 0.0

    recs = tracker.get_recommendations(top_n=3)
    assert isinstance(recs, list)


def test_spy_eval_extra_branches(tmp_path, monkeypatch) -> None:
    labels_missing = spy_eval.load_labels(tmp_path / "missing.csv")
    assert labels_missing == {}

    labels_file = tmp_path / "labels.csv"
    labels_file.write_text("run_1,tokena\n", encoding="utf-8")
    labels = spy_eval.load_labels(labels_file)
    assert labels["run_1"] == {"TOKENA"}

    class _Match:
        def __init__(self, tokens):
            self.tokens = tokens

    # Successful extractor import path + token normalization.
    monkeypatch.setattr("kryptos.spy.extract", lambda min_conf, run_dir: [_Match(["tok1", "TOK2"])])
    run_dir = tmp_path / "run_1"
    run_dir.mkdir()
    toks = spy_eval.run_extractor_on_run(run_dir, min_conf=0.1)
    assert toks == {"TOK1", "TOK2"}

    # RuntimeError path.
    monkeypatch.setattr("kryptos.spy.extract", lambda min_conf, run_dir: (_ for _ in ()).throw(RuntimeError("x")))
    assert spy_eval.run_extractor_on_run(run_dir, min_conf=0.1) == set()

    runs_root = tmp_path / "runs"
    runs_root.mkdir()
    (runs_root / "not_a_run").mkdir()
    (runs_root / "run_1").mkdir()

    def _extractor(_run, _th):
        return set()

    out = spy_eval.evaluate(labels_file, runs_root, thresholds=[0.0], extractor=_extractor)
    assert out[0.0] == (0.0, 0.0, 0.0)


def test_spy_eval_main_entry(monkeypatch, tmp_path) -> None:
    labels = tmp_path / "labels.csv"
    labels.write_text("run_1,TOK\n", encoding="utf-8")
    runs = tmp_path / "runs"
    (runs / "run_1").mkdir(parents=True, exist_ok=True)

    class _Logger:
        def info(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr("kryptos.log_setup.setup_logging", lambda logger_name="kryptos.spy": _Logger())
    monkeypatch.setattr(sys, "argv", ["spy_eval", "--labels", str(labels), "--runs", str(runs)])
    sys.modules.pop("kryptos.tuning.spy_eval", None)
    runpy.run_module("kryptos.tuning.spy_eval", run_name="__main__")
