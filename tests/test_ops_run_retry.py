import importlib.util
from pathlib import Path


def test_ops_run_tuning_retries(tmp_path, monkeypatch):
    # load orchestrator module from scripts/dev
    here = Path(__file__).resolve().parent
    repo_root = here.parent
    orch_path = repo_root / 'scripts' / 'dev' / 'orchestrator.py'
    spec = importlib.util.spec_from_file_location('orch_retry', str(orch_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    calls = {'count': 0}

    def fake_check_call(cmd, cwd=None):
        calls['count'] += 1
        # fail the first two calls, succeed on the third
        if calls['count'] < 3:
            raise RuntimeError('simulated transient failure')
        return 0

    monkeypatch.setattr(mod.subprocess, 'check_call', fake_check_call)

    # call ops_run_tuning which should retry and eventually return (or empty if it gives up)
    # call ops_run_tuning which should retry and eventually return (or empty if it gives up)
    _ = mod.ops_run_tuning(weights=[0.1], dry_run=True)
    # since the fake_check_call doesn't actually create artifacts, function may return ''
    # but it should have attempted 3 times
    assert calls['count'] == 3, f"expected 3 attempts, got {calls['count']}"
