import csv

from kryptos.spy import extractor as spy


def test_spy_extractor_detects_quoted_crib(tmp_path):
    # Prepare a fake run directory structure with a weight details csv
    run_dir = tmp_path / 'run_test'
    run_dir.mkdir()
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["It used the Earth's 'MAGNETIC' field", '0.0', '1.0', '1.0'])

    # Provide a minimal crib list containing MAGNETIC
    crib_file = tmp_path / 'cribs.txt'
    crib_file.write_text('MAGNETIC\n', encoding='utf-8')
    cribs = spy.load_cribs(crib_file)
    assert 'MAGNETIC' in cribs

    matches = spy.scan_run(run_dir, cribs)
    assert matches, 'Expected matches from scan_run'
    names = [m.filename for m in matches]
    assert 'weight_0_1_details.csv' in names
    all_tokens = ','.join(t for m in matches for t in m.tokens)
    assert 'MAGNETIC' in all_tokens
