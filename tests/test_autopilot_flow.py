import importlib.util
from pathlib import Path


def load_ask_module():
    here = Path(__file__).resolve().parent
    # Walk parents to find the repo root that contains scripts/dev/ask_triumverate.py
    repo_root = None
    for p in [here] + list(here.parents):
        candidate = p / 'scripts' / 'dev' / 'ask_triumverate.py'
        if candidate.exists():
            repo_root = p
            mod_path = candidate
            break
    if repo_root is None:
        raise RuntimeError('could not find scripts/dev/ask_triumverate.py in parents')
    spec = importlib.util.spec_from_file_location('ask_triumverate', str(mod_path))
    mod = importlib.util.module_from_spec(spec) if spec else None
    if spec and mod:
        spec.loader.exec_module(mod)  # type: ignore
        return mod
    raise RuntimeError('failed to load ask_triumverate')


def test_run_plan_check_writes_log(tmp_path):
    """Run a safe plan_text (no OPS run) and verify a log file appears in artifacts/logs."""
    ask = load_ask_module()
    # locate same repo root as above for artifacts path
    here = Path(__file__).resolve().parent
    repo_root = None
    for p in [here] + list(here.parents):
        if (p / 'scripts' / 'dev' / 'ask_triumverate.py').exists():
            repo_root = p
            break
    if repo_root is None:
        raise RuntimeError('could not find repo root')
    logs_dir = repo_root / 'artifacts' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Use a plan_text that does not contain 'crib' or the substring 'run' to avoid invoking OPS.
    ask.run_plan_check(plan_text='please review the current plan', autopilot=False, dry_run=True)

    # locate any run_*.jsonl under repo artifacts/logs (match possible relative paths)
    candidates = list(repo_root.glob('**/artifacts/logs/run_*.jsonl'))
    assert candidates, 'Expected at least one run_*.jsonl under artifacts/logs'
    # find a non-empty candidate
    non_empty = [p for p in candidates if p.stat().st_size > 0]
    assert non_empty, 'Expected at least one non-empty run_*.jsonl log'
    newest = sorted(non_empty, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    text = newest.read_text(encoding='utf-8')
    assert 'Q_SUMMARY' in text or 'SPY_SUMMARY' in text
