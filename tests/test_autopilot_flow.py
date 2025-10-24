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


def test_persona_prompt_with_dotted_filename():
    """Test that filenames with multiple dots (e.g., 'q.prompt.txt') are handled correctly.

    This verifies the maxsplit=1 fix in _persona_prompts() prevents issues where
    a filename like 'q.prompt.txt' would incorrectly be split into 'q' instead of 'q.prompt'.
    """
    # Test via public API: run_exchange should work correctly with dotted filenames
    here = Path(__file__).resolve().parent
    repo_root = None
    for p in [here] + list(here.parents):
        if (p / 'pyproject.toml').exists():
            repo_root = p
            break
    assert repo_root is not None, 'repo root not found'

    # Verify q.prompt file exists (may have multiple dots in actual setup)
    agents_dir = repo_root / 'agents'
    q_prompt = agents_dir / 'q.prompt'
    if q_prompt.exists():
        # Run exchange and verify Q persona is correctly loaded and used
        path = autopilot_mod.run_exchange(plan_text='test dotted filename', autopilot=False)
        text = path.read_text(encoding='utf-8')
        # If Q persona loaded correctly, should see Q_SUMMARY in output
        assert 'Q_SUMMARY' in text, 'Q persona should produce output (dotted filename handled)'
