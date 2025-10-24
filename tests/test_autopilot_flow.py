from pathlib import Path

from kryptos import autopilot as autopilot_mod


def test_run_exchange_writes_log():
    """Run a safe single exchange and verify a log file appears in artifacts/logs."""
    # ensure artifacts/logs exists under repo root
    here = Path(__file__).resolve().parent
    repo_root = None
    for p in [here] + list(here.parents):
        if (p / 'pyproject.toml').exists():
            repo_root = p
            break
    assert repo_root is not None, 'repo root not found'
    logs_dir = repo_root / 'artifacts' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    path = autopilot_mod.run_exchange(plan_text='please review the current plan', autopilot=False)
    assert path.exists(), 'Expected run log path to exist'
    text = path.read_text(encoding='utf-8')
    assert 'Q_SUMMARY' in text or 'SPY_SUMMARY' in text
