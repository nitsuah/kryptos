from pathlib import Path


def test_ops_run_tuning_dry_run():
    # import the orchestrator from scripts/dev by executing the file
    here = Path(__file__).resolve().parent
    repo_root = here.parent
    orch_path = repo_root / 'scripts' / 'dev' / 'orchestrator.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('orch_test', str(orch_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    # run with dry_run True and a tiny weight list
    run_dir = mod.ops_run_tuning(weights=[0.1, 0.5, 1.0], dry_run=True)
    assert run_dir, 'ops_run_tuning returned empty run path'
    p = Path(run_dir)
    assert p.exists() and p.is_dir(), f'Run dir does not exist: {run_dir}'
    # expect the sweep csv file to be present
    assert (p / 'crib_weight_sweep.csv').exists(), 'crib_weight_sweep.csv missing in run dir'
