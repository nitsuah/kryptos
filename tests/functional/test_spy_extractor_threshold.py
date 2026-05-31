import csv

from kryptos.spy import extractor as spy


def test_spy_extractor_min_conf(tmp_path):
    run_dir = tmp_path / 'run_test'
    run_dir.mkdir()
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["The 'MAGNETIC' anomaly was noted", '0.0', '1.0', '1.0'])
        writer.writerow(["Saw 'MAGNETIC' again", '0.0', '1.0', '0.1'])

    crib_file = tmp_path / 'cribs.txt'
    crib_file.write_text('MAGNETIC\n', encoding='utf-8')
    cribs = spy.load_cribs(crib_file)
    assert 'MAGNETIC' in cribs

    matches = spy.scan_run(run_dir, cribs)
    assert matches and len(matches) >= 1
    max_delta = max(m.delta for m in matches)
    assert max_delta > 0
    confidences = [m.delta / max_delta for m in matches]
    assert any(c >= 0.9 for c in confidences)
