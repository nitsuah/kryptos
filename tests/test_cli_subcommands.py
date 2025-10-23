from __future__ import annotations

import json
from pathlib import Path

from kryptos.cli.main import main as cli_main


def _invoke(argv: list[str]):
    return cli_main(argv)


def test_sections(capsys):
    _invoke(['sections'])
    out = capsys.readouterr().out.strip().splitlines()
    assert 'K1' in out and 'K4' in out


def test_k4_decrypt_minimal(tmp_path: Path, capsys):
    cipher_file = tmp_path / 'cipher.txt'
    cipher_file.write_text('OBKRUOXOGHULBSOLIFB', encoding='utf-8')
    _invoke(['k4-decrypt', '--cipher', str(cipher_file), '--limit', '5'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 'plaintext' in data and 'score' in data


def test_tuning_holdout_score_no_write(capsys):
    _invoke(['tuning-holdout-score', '--weight', '1.0', '--no-write'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data['weight'] == 1.0
    assert 'rows' in data and len(data['rows']) >= 1


def test_tuning_tiny_param_sweep(capsys):
    _invoke(['tuning-tiny-param-sweep'])
    out = capsys.readouterr().out
    rows = json.loads(out)
    assert isinstance(rows, list)


def test_tuning_crib_weight_sweep_json(capsys):
    _invoke(['tuning-crib-weight-sweep', '--weights', '0.5,1.0', '--json'])
    out = capsys.readouterr().out
    rows = json.loads(out)
    assert len(rows) >= 2
    assert {'weight', 'delta'} <= set(rows[0].keys())


def test_tuning_pick_best(tmp_path: Path, capsys):
    # Create a minimal CSV and run pick-best
    csv_path = tmp_path / 'crib_weight_sweep.csv'
    csv_path.write_text(
        'weight,sample,baseline,with_cribs,delta\n1.0,SAMP,0.0,1.0,1.0\n0.5,SAMP,0.0,0.8,0.8\n',
        encoding='utf-8',
    )
    _invoke(['tuning-pick-best', '--csv', str(csv_path)])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data['best_weight'] == 1.0


def _make_fake_run(root: Path) -> Path:
    run_dir = root / 'run_20250101T000000'
    run_dir.mkdir(parents=True, exist_ok=True)
    # minimal files for summarize_run: attempts.json & weight sweep mock
    (run_dir / 'attempts.json').write_text('[]', encoding='utf-8')
    (run_dir / 'crib_weight_sweep.csv').write_text(
        'weight,sample,baseline,with_cribs,delta\n1.0,SAMP,0.0,1.0,1.0\n',
        encoding='utf-8',
    )
    return run_dir


def test_tuning_summarize_run(tmp_path: Path, capsys):
    run_dir = _make_fake_run(tmp_path)
    _invoke(['tuning-summarize-run', '--run-dir', str(run_dir), '--no-write'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 'crib_hit_counts' in data or 'summary' in data


def test_spy_eval(tmp_path: Path, capsys):
    # fabricate runs + labels
    runs_root = tmp_path / 'tuning_runs'
    runs_root.mkdir()
    rdir = runs_root / 'run_20250101T000001'
    rdir.mkdir()
    # fabricate extractor-compatible file for spy-eval path (simulate tokens) if needed
    labels_csv = tmp_path / 'labels.csv'
    labels_csv.write_text('run_20250101T000001,TESTTOKEN\n', encoding='utf-8')
    _invoke(['spy-eval', '--labels', str(labels_csv), '--runs', str(runs_root), '--thresholds', '0.0'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 'thresholds' in data and '0.00' in data['thresholds']


def test_spy_extract(tmp_path: Path, capsys):
    runs_root = tmp_path / 'tuning_runs'
    runs_root.mkdir()
    (runs_root / 'run_20250101T000002').mkdir()
    _invoke(['spy-extract', '--runs', str(runs_root), '--min-conf', '0.25'])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 'min_conf' in data and 'extracted' in data
