from pathlib import Path

from kryptos.tuning import spy_eval


def _fake_extractor_factory(mapping: dict[str, dict[float, set[str]]]):
    def _extract(run_dir: Path, threshold: float) -> set[str]:
        run_map = mapping.get(run_dir.name, {})
        if not run_map:
            return set()
        keys = sorted(run_map.keys())
        chosen = None
        for k in keys:
            if k <= threshold:
                chosen = k
        if chosen is None:
            return set()
        return {t.upper() for t in run_map.get(chosen, set())}

    return _extract


def test_select_best_threshold_precision_first(tmp_path):
    runs_root = tmp_path / 'tuning_runs'
    runs_root.mkdir()
    (runs_root / 'run_A').mkdir()
    (runs_root / 'run_B').mkdir()

    labels_csv = tmp_path / 'labels.csv'
    labels_csv.write_text('run_A,TOKEN1\nrun_A,TOKEN2\nrun_B,TOKEN3\n', encoding='utf-8')

    mapping = {
        'run_A': {0.0: {'TOKEN1', 'TOKEN2', 'TOKENX'}, 0.5: {'TOKEN1', 'TOKEN2'}, 0.75: {'TOKEN1'}},
        'run_B': {0.0: {'TOKEN3'}, 0.5: {'TOKEN3', 'TOKENY'}, 0.75: {'TOKEN3'}},
    }
    extractor = _fake_extractor_factory(mapping)
    thresholds = [0.0, 0.5, 0.75]
    chosen = spy_eval.select_best_threshold(labels_csv, runs_root, thresholds, extractor=extractor)
    eval_map = spy_eval.evaluate(labels_csv, runs_root, thresholds=thresholds, extractor=extractor)
    for th in thresholds:
        assert th in eval_map
        p, r, f1 = eval_map[th]
        assert 0.0 <= p <= 1.0 and 0.0 <= r <= 1.0 and 0.0 <= f1 <= 1.0
    # Highest precision occurs at 0.75 (precision=1.0); ensure it is selected.
    assert chosen == 0.75, f'expected best threshold 0.75 got {chosen}'
