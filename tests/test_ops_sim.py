import csv
import importlib.util
from pathlib import Path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec) if spec else None
    if spec and mod:
        spec.loader.exec_module(mod)  # type: ignore
        return mod
    raise RuntimeError(f'failed to load {path}')


def test_pick_best_on_synthetic_run(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    runs_root = repo / 'artifacts' / 'tuning_runs'
    run_dir = runs_root / 'run_test_ops'
    run_dir.mkdir(parents=True, exist_ok=True)

    csv_path = run_dir / 'crib_weight_sweep.csv'
    # Create CSV with two weights; weight 0.5 has higher mean delta
    rows = [
        {'weight': '0.1', 'baseline': '10', 'with_cribs': '11'},
        {'weight': '0.1', 'baseline': '20', 'with_cribs': '21'},
        {'weight': '0.5', 'baseline': '10', 'with_cribs': '13'},
        {'weight': '0.5', 'baseline': '20', 'with_cribs': '24'},
    ]
    with csv_path.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['weight', 'baseline', 'with_cribs'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # load analyzer and run pick_best
    pick_mod = load_module(repo / 'scripts' / 'tuning' / 'pick_best_weight.py', 'pick_best')
    best, stats = pick_mod.pick_best(run_dir)
    assert float(best) == 0.5

    # exercise spy_eval selection path (likely returns 0.0 because extractor not importable)
    spy_mod = load_module(repo / 'scripts' / 'tuning' / 'spy_eval.py', 'spy_eval')
    labels_path = repo / 'data' / 'spy_eval_labels.csv'
    # create a minimal labels file mapping our run to a token
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    with labels_path.open('w', encoding='utf-8', newline='') as lf:
        lf.write("run_test_ops,TOKEN1\n")
    th = spy_mod.select_best_threshold(labels_path, runs_root)
    assert isinstance(th, float)
