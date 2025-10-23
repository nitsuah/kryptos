import importlib.util
from pathlib import Path


def test_ops_run_tuning_returns_metadata(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[1]
    orch_path = repo / 'scripts' / 'dev' / 'orchestrator.py'
    spec = importlib.util.spec_from_file_location('orch_meta', str(orch_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    # prepare a fake artifacts/tuning_runs/run_x directory with detail CSV
    # tr_root is unused, so it has been removed
    # tr_root = Path('artifacts') / 'tuning_runs'
    run_dir = tmp_path / 'artifacts' / 'tuning_runs' / 'run_test'
    run_dir.mkdir(parents=True)
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', encoding='utf-8') as fh:
        fh.write('sample,baseline,with_cribs,delta\n')
        fh.write("SAMPLE,0,1,0.5\n")
        fh.write("SAMPLE,0,1,2.0\n")

    # monkeypatch the repo path detection to treat tmp_path as the repo root
    monkeypatch.setenv('PYTEST_ORCH_ROOT', str(tmp_path))

    # monkeypatch subprocess.check_call to just create the run directory under repo
    def fake_check_call(cmd, cwd=None):
        # create the run dir in the expected artifacts location inside cwd
        target = Path(cwd) / 'artifacts' / 'tuning_runs' / 'run_test'
        target.mkdir(parents=True, exist_ok=True)
        # copy our detail CSV into that location
        (target / 'weight_0_1_details.csv').write_text(detail.read_text(), encoding='utf-8')
        # also write a minimal crib_weight_sweep.csv to mimic real sweep script
        try:
            (target / 'crib_weight_sweep.csv').write_text('weight,metric\n0.1,1.0\n', encoding='utf-8')
        except Exception:
            pass
        # ensure this run appears newest by setting its mtime to the future
        import os
        import time

        future = time.time() + 10000
        try:
            os.utime(str(target / 'weight_0_1_details.csv'), (future, future))
            os.utime(str(target), (future, future))
        except Exception:
            pass
        return 0

    monkeypatch.setattr(mod.subprocess, 'check_call', fake_check_call)

    # call with non-default retries/backoff to get metadata dict
    meta = mod.ops_run_tuning(weights=[0.1], dry_run=True, retries=2, backoff_factor=0.1)
    assert isinstance(meta, dict)
    assert 'run_dir' in meta and 'max_delta' in meta
    assert meta['max_delta'] == 2.0
    # cleanup the synthetic run created under the repo to avoid interfering with other tests
    try:
        import shutil

        repo_run = Path('artifacts') / 'tuning_runs' / 'run_test'
        if repo_run.exists():
            shutil.rmtree(str(repo_run))
    except Exception:
        pass
