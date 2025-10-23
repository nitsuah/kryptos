from __future__ import annotations

import csv
from pathlib import Path

from kryptos.k4.tuning.artifacts import (
    clean_all_match_files,
    crib_hit_counts,
    end_to_end_process,
    summarize_run,
)


def _make_run_dir(tmp_path: Path) -> Path:
    rd = tmp_path / 'run_20250101T000000'
    rd.mkdir()
    # create a sweep csv
    sweep = rd / 'crib_weight_sweep.csv'
    with sweep.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['weight', 'sample', 'baseline', 'with_cribs', 'delta'])
        w.writerow(['0.1', 'SAMPLEAA', '1.0', '1.1', '0.1'])
        w.writerow(['0.1', 'SAMPLEBB', '2.0', '2.4', '0.4'])
        w.writerow(['0.5', 'SAMPLECC', '1.5', '2.0', '0.5'])
    # create matches files
    m1 = rd / 'matches_weight_0_1.csv'
    with m1.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['sample', 'matched_cribs'])
        w.writerow(['SAMPLEAA', 'A|B|A|C'])
        w.writerow(['SAMPLEBB', ''])
    m2 = rd / 'matches_weight_0_5.csv'
    with m2.open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['sample', 'matched_cribs'])
        w.writerow(['SAMPLECC', 'B|C'])
    return rd


def test_clean_and_summarize_and_counts(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    cleaned = clean_all_match_files(run_dir)
    assert '0_1' in cleaned and '0_5' in cleaned
    # dedup worked
    aa_entry = [e for e in cleaned['0_1'] if e.sample == 'SAMPLEAA'][0]
    assert aa_entry.matched == 'A|B|C'
    summary = summarize_run(run_dir)
    assert summary['run_dir'] == run_dir.name
    assert summary['top_deltas']
    counts = crib_hit_counts(run_dir)
    # counts reflect cleaned matches
    assert counts['B'] >= 1 and counts['C'] >= 1
    combo = end_to_end_process(run_dir, write=True)
    assert 'summary' in combo and 'counts' in combo
    assert (run_dir / 'artifact_summary.txt').exists()
    assert (run_dir / 'crib_hit_counts.json').exists()
