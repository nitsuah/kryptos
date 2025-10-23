import csv
from pathlib import Path

from kryptos.spy.extractor import SpyMatch, extract, load_cribs, scan_run


def test_scan_run_finds_magnetic(tmp_path):
    # Prepare synthetic run directory CSV similar to previous legacy tests
    run_dir = tmp_path / 'run_test'
    run_dir.mkdir()
    detail = run_dir / 'weight_0_1_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["It used the Earth's 'MAGNETIC' field", '0.0', '1.0', '1.0'])
    cribs_raw = load_cribs(Path('config/config.json'))  # may be list
    cribs = list(cribs_raw)
    if 'MAGNETIC' not in cribs:
        cribs.append('MAGNETIC')
    results = scan_run(run_dir, cribs)
    assert results, 'Expected at least one result from scan_run'
    tokens = {t for r in results for t in r.tokens}
    assert 'MAGNETIC' in tokens


def test_extract_with_run_dir(tmp_path):
    run_dir = tmp_path / 'run_test2'
    run_dir.mkdir()
    detail = run_dir / 'weight_x_details.csv'
    with detail.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["Saw 'MAGNETIC' anomaly again", '0.0', '1.0', '0.5'])
    cribs = ['MAGNETIC']
    matches = scan_run(run_dir, set(cribs))
    assert all(isinstance(m, SpyMatch) for m in matches)
    # confidence assignment done inside scan_run
    assert matches, 'scan_run should yield matches'
    # Filter with extract using min_conf threshold
    kept = extract(min_conf=0.5, run_dir=run_dir)
    assert kept, 'extract should keep matches above confidence threshold'
    assert matches, 'extract should return matches when run_dir provided'
    tokens2 = {t for m in kept for t in m.tokens}
    assert 'MAGNETIC' in tokens2
    max_delta = max(m.delta for m in kept)
    top_conf = max(m.confidence for m in kept)
    assert max_delta > 0 and top_conf >= 0.5
