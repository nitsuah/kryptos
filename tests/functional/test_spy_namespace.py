from pathlib import Path

from kryptos.spy import SpyMatch, aggregate_phrases, extract, load_cribs, scan_run


def test_load_cribs_empty(tmp_path: Path):
    cribs_file = tmp_path / 'cribs.txt'
    assert load_cribs(cribs_file) == set()


def test_aggregate_missing(tmp_path: Path):
    in_path = tmp_path / 'spy_cribs.tsv'
    out_path = tmp_path / 'spy_crib_phrases.tsv'
    count = aggregate_phrases(in_path, out_path)
    assert count == -1
    assert not out_path.exists()


def test_aggregate_phrases(tmp_path: Path):
    in_path = tmp_path / 'spy_cribs.tsv'
    lines = [
        'TOK1\tSRC1\tEXCERPT ONE\thigh',
        'TOK2\tSRC2\tEXCERPT ONE\tmed',  # lower rank ignored
        'TOK3\tSRC3\tEXCERPT TWO\tlow',
    ]
    in_path.write_text('\n'.join(lines), encoding='utf-8')
    out_path = tmp_path / 'spy_crib_phrases.tsv'
    count = aggregate_phrases(in_path, out_path)
    assert count == 2
    data = out_path.read_text(encoding='utf-8').splitlines()
    assert data[0] == 'EXCERPT\tSOURCE\tCONFIDENCE'
    assert any('EXCERPT ONE\tSRC1\thigh' in line for line in data[1:])


def test_scan_run_and_extract(tmp_path: Path, monkeypatch):
    # create fake run dir structure
    run_dir = tmp_path / 'run_ABC'
    run_dir.mkdir()
    details = run_dir / 'weight_1_details.csv'
    # Provide explicit sample & delta columns; extractor only cares about these two
    # Simpler CSV: each row with a single token for deterministic matching
    details.write_text('sample,delta,extra\n"ALPHA" "OMEGA",0.5,x\n"OMEGA",0.4,x\n', encoding='utf-8')
    cribs = {'ALPHA', 'OMEGA'}
    matches = scan_run(run_dir, cribs)
    # First row contains TOK1 TOK2 (both captured); second row TOK2 is deduped -> one SpyMatch
    assert len(matches) == 1
    # monkeypatch find_latest_run & load_cribs
    monkeypatch.setattr('kryptos.spy.extractor.find_latest_run', lambda: run_dir)
    monkeypatch.setattr('kryptos.spy.extractor.load_cribs', lambda path=Path('x'): cribs)
    kept = extract(min_conf=0.0, cribs_path=Path('dummy'))
    assert len(kept) == 1
    assert all(isinstance(m, SpyMatch) for m in kept)
