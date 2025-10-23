import csv
import importlib.util
from pathlib import Path


def test_spy_extractor_detects_quoted_crib(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    # Prepare a fake run directory structure
    run_dir = tmp_path / 'run_test'
    run_dir.mkdir()
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        # include a quoted crib token that should be in the real crib list (MAGNETIC)
        writer.writerow(["It used the Earth's 'MAGNETIC' field", '0.0', '1.0', '1.0'])

    # load the spy_extractor module
    mod_path = repo / 'scripts' / 'dev' / 'spy_extractor.py'
    spec = importlib.util.spec_from_file_location('spy_test', str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    cribs = mod.load_cribs(mod.CRIBS)
    assert 'MAGNETIC' in cribs, 'test expects MAGNETIC in the crib list'

    res = mod.scan_run(run_dir, cribs)
    assert res, 'spy_extractor should find matches in the fake run'
    # expect the file and token to be reported
    names = [r[0] for r in res]
    assert 'weight_0_1_details.csv' in names
    tokens = ','.join(r[1] for r in res)
    assert 'MAGNETIC' in tokens
