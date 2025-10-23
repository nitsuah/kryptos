import importlib.util
from pathlib import Path


def test_e2e_autopilot_dryrun(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    orch_path = repo / 'scripts' / 'dev' / 'orchestrator.py'
    spy_path = repo / 'scripts' / 'dev' / 'spy_extractor.py'

    spec = importlib.util.spec_from_file_location('orch_e2e', str(orch_path))
    orch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orch)  # type: ignore

    # backup LEARNED.md if present
    learned = repo / 'agents' / 'LEARNED.md'
    backup = None
    if learned.exists():
        backup = tmp_path / 'LEARNED.bak'
        backup.write_bytes(learned.read_bytes())

    # run ops tuning dry-run
    run_dir = orch.ops_run_tuning(weights=[0.1, 0.5, 1.0], dry_run=True)
    assert run_dir, 'ops_run_tuning did not produce a run directory'
    runp = Path(run_dir)
    assert (runp / 'crib_weight_sweep.csv').exists()

    # run spy_extractor main
    spec2 = importlib.util.spec_from_file_location('spy_e2e', str(spy_path))
    spy = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(spy)  # type: ignore

    # run the extractor and ensure it completes
    rv = spy.main()
    assert rv == 0

    # LEARNED.md should now exist and contain SPY_MATCH lines
    assert learned.exists(), 'agents/LEARNED.md was not created'
    text = learned.read_text(encoding='utf-8')
    assert 'SPY_MATCH' in text, 'No SPY_MATCH entries written to LEARNED.md'

    # restore backup
    if backup and backup.exists():
        learned.write_bytes(backup.read_bytes())
    else:
        # if no backup, clear the file to avoid side-effects
        learned.write_text('', encoding='utf-8')
