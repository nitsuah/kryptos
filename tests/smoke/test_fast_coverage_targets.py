from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from kryptos.k4 import beaufort
from kryptos.k4.hypothesis_runner import run_hypothesis_search
from kryptos.pipeline.attack_executor import AttackExecutor
from kryptos.pipeline.k4_campaign import CampaignResult
from kryptos.pipeline.validator import PlaintextValidator, simple_dictionary_score
from kryptos.provenance.attack_log import AttackRecord
from kryptos.reporting import generate_report

# Import multiprocessing-safe test helper


def test_generate_report_with_and_without_frequency_plot(tmp_path: Path) -> None:
    with_freq = {
        "frequencies": {
            "k1": {"A": 0.2, "B": 0.8},
            "k2": {"A": 0.6, "C": 0.4},
        },
        "cribs": {"KEY1": ["BERLIN", "CLOCK"]},
    }
    png_path = generate_report(with_freq, "demo", out_dir=tmp_path)  # type: ignore[arg-type]
    assert png_path.exists()
    assert (tmp_path / "demo_summary.txt").read_text(encoding="utf-8").strip() == "Key=KEY1: BERLIN, CLOCK"

    no_freq: dict = {  # type: ignore[type-arg]
        "frequencies": {},
        "cribs": {"KEY2": []},
    }
    out = generate_report(no_freq, "demo2", out_dir=tmp_path)  # type: ignore[arg-type]
    assert out == tmp_path / "demo2_report.png"
    assert not out.exists()
    assert (tmp_path / "demo2_summary.txt").read_text(encoding="utf-8").strip() == "Key=KEY2: [none]"


def test_beaufort_roundtrip_and_recovery_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    plaintext = "KRYPTOS"
    key = "CLOCK"
    ciphertext = beaufort.beaufort_encrypt(plaintext, key)
    assert beaufort.beaufort_decrypt(ciphertext, key) == plaintext

    with_preserve = beaufort.beaufort_encrypt("AB-CD", "KEY", preserve_non_alpha=True)
    no_preserve = beaufort.beaufort_encrypt("AB-CD", "KEY", preserve_non_alpha=False)
    assert "-" in with_preserve
    assert "-" not in no_preserve

    with pytest.raises(ValueError):
        beaufort.beaufort_encrypt("ABC", "")
    with pytest.raises(ValueError):
        beaufort.beaufort_decrypt("ABC", "")
    with pytest.raises(ValueError):
        beaufort.beaufort_encrypt("ABÄ", "KEY")
    with pytest.raises(ValueError):
        beaufort.beaufort_decrypt("ABC", "KÄY")

    assert beaufort.recover_beaufort_key("ABC", 5) == []
    assert len(beaufort.recover_beaufort_key("ABCDABCDABCD", 3)) == 1

    monkeypatch.setattr(beaufort, "KEYED_ALPHABET", "KRYPTOSABCDFGHIJLMNQUVWXZ")
    recovered = beaufort.recover_beaufort_key("ABCDABCDABCD", 3)
    assert len(recovered) == 1


@dataclass
class _FakeCandidate:
    id: str
    plaintext: str
    score: float
    key_info: str | None = None


class _FakeHypothesis:
    def __init__(self, candidates: list[_FakeCandidate]) -> None:
        self.mode = "test"
        self.limit = 7
        self._candidates = candidates

    def generate_candidates(self, _ciphertext: str, limit: int = 50) -> list[_FakeCandidate]:
        return self._candidates[:limit]


def test_hypothesis_runner_writes_artifacts_and_parameters(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    baseline_dir = tmp_path / "baselines"
    baseline_dir.mkdir(parents=True)
    (baseline_dir / "random_scoring_20200101.json").write_text(
        json.dumps({"statistics": {"mean": 10.0, "stddev": 5.0}}),
        encoding="utf-8",
    )
    monkeypatch.setattr("kryptos.k4.hypothesis_runner.get_artifacts_root", lambda: tmp_path)

    candidates = [
        _FakeCandidate(id="1", plaintext="BERLINCLOCKTEXT", score=30.0, key_info="KEY=A"),
        _FakeCandidate(id="2", plaintext="SECOND", score=11.0, key_info=None),
    ]
    out = run_hypothesis_search(
        hypothesis_name="demo_h",
        hypothesis_instance=_FakeHypothesis(candidates),
        ciphertext="ABCDEF",
        limit=10,
        output_dir=str(tmp_path / "results"),
    )

    assert out["num_candidates"] == 2
    assert out["parameters"] == {"mode": "test", "limit": 7}
    written = sorted((tmp_path / "results").glob("search_*.json"))
    assert written
    loaded = json.loads(written[-1].read_text(encoding="utf-8"))
    assert loaded["candidates"][0]["id"] == "1"


def test_hypothesis_runner_without_candidates_uses_default_output_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kryptos.k4.hypothesis_runner.get_artifacts_root", lambda: tmp_path)
    out = run_hypothesis_search(
        hypothesis_name="empty_case",
        hypothesis_instance=_FakeHypothesis([]),
        ciphertext="ABC",
        limit=1,
    )
    assert out["num_candidates"] == 0
    assert (tmp_path / "empty_case_searches").exists()


class _DummyLogger:
    def __init__(self) -> None:
        self.attack_index: dict[str, AttackRecord] = {}

    def log_attack(self, ciphertext, parameters, result, tags=None, agents_involved=None):
        fp = parameters.fingerprint()
        record = AttackRecord(
            attack_id=f"id-{len(self.attack_index)+1}",
            timestamp=datetime.now(),
            ciphertext=ciphertext,
            parameters=parameters,
            result=result,
            agent_involved=agents_involved or [],
            tags=tags or [],
        )
        self.attack_index[fp] = record
        return record.attack_id, False

    def get_statistics(self):
        return {"total": len(self.attack_index)}

    def query_attacks(self, **_kwargs):
        return list(self.attack_index.values())


def test_attack_executor_vigenere_transposition_and_hill(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _DummyLogger()
    ex = AttackExecutor(logger=logger)  # type: ignore[arg-type]

    monkeypatch.setattr("kryptos.pipeline.attack_executor.vigenere_decrypt", lambda _ct, _k: "BERLINXYZ")
    plaintext, record = ex.vigenere_attack("ABC", "KEY", crib_text="BERLIN", tags=["quick"])
    assert plaintext == "BERLINXYZ"
    assert record.result.success is True
    assert record.tags == ["quick"]

    def _raise_vigenere(_ct, _k):
        raise RuntimeError("boom")

    monkeypatch.setattr("kryptos.pipeline.attack_executor.vigenere_decrypt", _raise_vigenere)
    plaintext2, record2 = ex.vigenere_attack("ABC", "KEY")
    assert plaintext2 == ""
    assert record2.result.success is False

    monkeypatch.setattr(
        "kryptos.pipeline.attack_executor.solve_columnar_permutation_exhaustive",
        lambda _ct, _p, **_kw: ([1, 0], 0.2),
    )
    monkeypatch.setattr(
        "kryptos.pipeline.attack_executor.solve_columnar_permutation_simulated_annealing_multi_start",
        lambda _ct, _p, **_kw: ([0, 1, 2], 0.05),
    )
    monkeypatch.setattr(
        "kryptos.k4.transposition_analysis.apply_columnar_permutation_reverse",
        lambda _ct, _p, _perm: "CLOCKTEXT",
    )
    (perm_ex, score_ex), rec_ex = ex.transposition_attack("CIPH", 2, method="exhaustive")
    assert perm_ex == [1, 0]
    assert score_ex == 0.2
    assert rec_ex.result.success is True

    (perm_sa, score_sa), rec_sa = ex.transposition_attack("CIPH", 3, method="simulated_annealing", crib_text="CLOCK")
    assert perm_sa == [0, 1, 2]
    assert score_sa == 0.05
    assert rec_sa.result.success is True

    (_perm_bad, score_bad), rec_bad = ex.transposition_attack("CIPH", 3, method="unknown")
    assert score_bad == 0.0
    assert rec_bad.result.success is False

    monkeypatch.setattr("kryptos.k4.hill_cipher.hill_decrypt", lambda _ct, _km: "PLAINTEXT")
    plain_hill, rec_hill = ex.hill_attack("ABC", 2, [[1, 0], [0, 1]], crib_text="PLAIN")
    assert plain_hill == "PLAINTEXT"
    assert rec_hill.result.success is True

    def _raise_hill(_ct, _km):
        raise ValueError("bad hill")

    monkeypatch.setattr("kryptos.k4.hill_cipher.hill_decrypt", _raise_hill)
    plain_hill2, rec_hill2 = ex.hill_attack("ABC", 2, [[1, 0], [0, 1]])
    assert plain_hill2 == ""
    assert rec_hill2.result.success is False
    assert ex.get_statistics()["total"] >= 1
    assert ex.query_attacks()


def test_validator_scoring_and_validation_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    assert simple_dictionary_score("") == 0.0
    assert simple_dictionary_score("123!!!") == 0.0
    assert 0.0 <= simple_dictionary_score("THEQUICKBROWNFOX") <= 1.0

    validator = PlaintextValidator(known_cribs=["BERLIN", "CLOCK"], min_dictionary_score=0.1, min_confidence=0.1)
    stage2 = validator.stage2_crib_matching("xxberlinyy")
    assert stage2["passed"] is True
    assert stage2["matches"][0]["crib"] == "BERLIN"

    stage3_empty = validator.stage3_linguistic_validation("")
    assert stage3_empty["passed"] is False
    stage3_bad = validator.stage3_linguistic_validation("ZZZZZZZZZZ")
    assert stage3_bad["passed"] is False

    stage4 = validator.stage4_confidence_scoring(
        {
            "stage1_dictionary": {"score": 0.9},
            "stage2_crib": {"passed": False},
            "stage3_linguistic": {"metrics": {"vowel_ratio": 0.3, "max_repetition": 2, "common_digraphs": 3}},
        },
    )
    assert 0.0 <= stage4["confidence"] <= 1.0

    full = validator.validate("THECLOCKISINBERLIN")
    assert isinstance(full.is_valid, bool)
    ok, conf = validator.quick_validate("THECLOCKISINBERLIN")
    assert ok == full.is_valid
    assert conf == full.confidence

    def _raise_dict(_text: str) -> float:
        raise RuntimeError("bad scoring")

    monkeypatch.setattr("kryptos.pipeline.validator.simple_dictionary_score", _raise_dict)
    stage1 = validator.stage1_dictionary_score("ANYTEXT")
    assert stage1["score"] == 0.0


def _warn_noop(*_args, **_kwargs):
    pass


def _validate_always_true(text):
    class Dummy:
        def __init__(self, t):
            self.is_valid = True
            self.confidence = 0.9
            self._t = t

        def to_dict(self):
            return {"t": self._t}

    return Dummy(text)


def _get_coverage_report():
    return {"coverage": 1}


def _recover_key_by_frequency(_ct, _kl, top_n=1):
    return ["ABCD"]


def _vigenere_decrypt(_ct, _k):
    return "DECRYPTED"


def _solve_columnar_permutation_exhaustive(_ct, _period):
    return ([0, 1], 0.4)


def _solve_columnar_permutation_simulated_annealing_multi_start(_ct, _period):
    return ([1, 0], 0.6)


# test_campaign_execute_methods_and_print_summary moved to test_multiproc_campaign.py for Windows multiprocessing compatibility.  # noqa: E501


def test_campaign_result_to_dict() -> None:
    start = datetime(2025, 1, 1, 0, 0, 0)
    end = datetime(2025, 1, 1, 0, 0, 5)
    result = CampaignResult(
        campaign_id="x",
        start_time=start,
        end_time=end,
        total_attacks=10,
        successful_attacks=2,
        best_candidates=[{"a": 1}],
        coverage_report={"b": 2},
        statistics={"c": 3},
    )
    as_dict = result.to_dict()
    assert as_dict["duration_seconds"] == 5
    assert as_dict["success_rate"] == 0.2


def test_tiny_weight_sweep_and_cli(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from kryptos.examples import tiny_weight_sweep as tws

    rows = [
        SimpleNamespace(weight=0.1, sample="SAMPLE-A", baseline=-1.0, with_cribs=-0.5, delta=0.5),
        SimpleNamespace(weight=0.5, sample="SAMPLE-B", baseline=-2.0, with_cribs=-1.0, delta=1.0),
    ]
    monkeypatch.setattr(tws, "run_crib_weight_sweep", lambda **_kwargs: rows)
    monkeypatch.setattr(tws, "get_artifacts_root", lambda: tmp_path)

    out_dir = tws.run_tiny_weight_sweep(samples=["A"], cribs=["BERLIN"], weights=[0.1, 0.5])
    assert out_dir.exists()
    assert (out_dir / "crib_weight_sweep.csv").exists()
    assert (out_dir / "weight_0_1_details.csv").exists()
    assert (out_dir / "weight_0_5_details.csv").exists()

    monkeypatch.setattr("sys.argv", ["tiny_weight_sweep", "--weights", "bad,float"])
    tws._main()

    monkeypatch.setattr("sys.argv", ["tiny_weight_sweep", "--weights", "0.2,0.4"])
    tws._main()
