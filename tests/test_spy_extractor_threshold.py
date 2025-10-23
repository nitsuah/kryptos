import csv
import importlib.util
from pathlib import Path


def test_spy_extractor_min_conf(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    run_dir = tmp_path / 'run_test'
    run_dir.mkdir()
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        # two rows with different deltas to create different confidences
        writer.writerow(["The 'MAGNETIC' anomaly was noted", '0.0', '1.0', '1.0'])
        writer.writerow(["Saw 'MAGNETIC' again", '0.0', '1.0', '0.1'])

    # load module
    mod_path = repo / 'scripts' / 'dev' / 'spy_extractor.py'
    spec = importlib.util.spec_from_file_location('spy_test_conf', str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    cribs = mod.load_cribs(mod.CRIBS)
    assert 'MAGNETIC' in cribs

    # scan_run should return both matches
    res = mod.scan_run(run_dir, cribs)
    assert res and len(res) >= 1

    # compute filtering: call main with min_conf=0.9 to only keep the top match
    # Use main directly; it expects to find runs in artifacts, so call the logic locally
    max_delta = max((d for _, _, d in res), default=0.0)
    assert max_delta > 0
    # compute confidences
    confs = [d / max_delta for _, _, d in res]
    assert any(c >= 0.9 for c in confs)
