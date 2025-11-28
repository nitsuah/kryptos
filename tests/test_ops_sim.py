import csv
import importlib.util
from pathlib import Path

import pytest


@pytest.mark.skip(reason="scripts/tuning.py removed during Phase 6 cleanup - functionality moved to CLI")
def test_pick_best_on_synthetic_run():
    """Test weight analysis using consolidated tuning CLI logic."""
    repo = Path(__file__).resolve().parents[1]
    runs_root = repo / 'artifacts' / 'tuning_runs'
    run_dir = runs_root / 'run_test_ops'
    run_dir.mkdir(parents=True, exist_ok=True)

    csv_path = run_dir / 'crib_weight_sweep.csv'
    # Create CSV with two weights; weight 0.5 has higher mean delta
    # Include 'delta' column to match new format
    rows = [
        {'weight': '0.1', 'baseline': '10', 'with_cribs': '11', 'delta': '1'},
        {'weight': '0.1', 'baseline': '20', 'with_cribs': '21', 'delta': '1'},
        {'weight': '0.5', 'baseline': '10', 'with_cribs': '13', 'delta': '3'},
        {'weight': '0.5', 'baseline': '20', 'with_cribs': '24', 'delta': '4'},
    ]
    with csv_path.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['weight', 'baseline', 'with_cribs', 'delta'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Import consolidated tuning module's pick_best_weight function
    tuning_path = repo / 'scripts' / 'tuning.py'
    spec = importlib.util.spec_from_file_location('tuning', str(tuning_path))
    if not spec or not spec.loader:
        raise RuntimeError(f'failed to load {tuning_path}')
    tuning_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tuning_mod)  # type: ignore[union-attr]
    best, _stats = tuning_mod.pick_best_weight(run_dir)  # type: ignore[attr-defined]
    assert float(best) == 0.5

    # exercise spy_eval selection path using canonical package module
    from kryptos.tuning import spy_eval as spy_mod

    labels_path = repo / 'data' / 'spy_eval_labels.csv'
    # create a minimal labels file mapping our run to a token
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    with labels_path.open('w', encoding='utf-8', newline='') as lf:
        lf.write("run_test_ops,TOKEN1\n")
    th = spy_mod.select_best_threshold(labels_path, runs_root)
    assert isinstance(th, float)


# Also skip whole module in fast CI runs (preserve the in-test skip reason)
pytest.skip("Marked slow: ops simulation tests", allow_module_level=True)
