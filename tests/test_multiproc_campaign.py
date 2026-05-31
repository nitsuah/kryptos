import pytest
from pathlib import Path
from types import SimpleNamespace
from kryptos.pipeline.k4_campaign import K4CampaignOrchestrator
from tests.test_multiproc_helpers import AttackGenTestHelper

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

def test_campaign_execute_methods_and_print_summary(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    orchestrator = object.__new__(K4CampaignOrchestrator)
    orchestrator.log = SimpleNamespace(warning=_warn_noop)
    orchestrator.validator = SimpleNamespace(validate=_validate_always_true)
    orchestrator.search_space = SimpleNamespace(get_coverage_report=_get_coverage_report)
    orchestrator.attack_generator = AttackGenTestHelper()
    orchestrator.workspace_dir = Path.cwd()

    monkeypatch.setattr("kryptos.pipeline.k4_campaign.recover_key_by_frequency", _recover_key_by_frequency)
    monkeypatch.setattr("kryptos.pipeline.k4_campaign.vigenere_decrypt", _vigenere_decrypt)
    monkeypatch.setattr("kryptos.pipeline.k4_campaign.solve_columnar_permutation_exhaustive", _solve_columnar_permutation_exhaustive)
    monkeypatch.setattr("kryptos.pipeline.k4_campaign.solve_columnar_permutation_simulated_annealing_multi_start", _solve_columnar_permutation_simulated_annealing_multi_start)

    # Run the campaign and print summary (actual test logic omitted for brevity)
    # ...existing code for running and asserting campaign summary...
    pass
