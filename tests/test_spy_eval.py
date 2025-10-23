import csv


def test_spy_eval_smoke(tmp_path):
    # create a fake run dir with a details csv
    runs_root = tmp_path / 'artifacts' / 'tuning_runs'
    run_dir = runs_root / 'run_test'
    run_dir.mkdir(parents=True)
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["Found 'MAGNETIC' in sample", '0', '1', '1.0'])

    # create labels file
    labels = tmp_path / 'data' / 'spy_eval_labels.csv'
    labels.parent.mkdir()
    with labels.open('w', encoding='utf-8') as fh:
        fh.write('run_test,MAGNETIC\n')

    # import harness from package and run evaluate
    import importlib

    mod = importlib.import_module('kryptos.scripts.tuning.spy_eval')

    res = mod.evaluate(labels, runs_root, thresholds=[0.0, 0.5])
    assert 0.0 in res and 0.5 in res
    # expect precision/recall values to be numeric
    for _k, (p, r, f) in res.items():
        assert isinstance(p, float)
        assert isinstance(r, float)
        assert isinstance(f, float)
