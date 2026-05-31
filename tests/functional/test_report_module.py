from __future__ import annotations

from pathlib import Path

from kryptos.k4.report import (
    build_condensed_rows,
    write_condensed_report,
    write_top_candidates_markdown,
)


def _make_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / 'run_fake'
    run_dir.mkdir()
    # create two weight detail files with different deltas
    (run_dir / 'weight_1_0_details.csv').write_text(
        'sample,baseline,with_cribs,delta\nAAA,0,0,0\nBBB,0,1,1\n',
        encoding='utf-8',
    )
    (run_dir / 'weight_0_5_details.csv').write_text(
        'sample,baseline,with_cribs,delta\nCCC,0,0.6,0.6\n',
        encoding='utf-8',
    )
    return run_dir


def test_build_condensed_rows(tmp_path: Path):
    run_dir = _make_run(tmp_path)
    rows = build_condensed_rows(run_dir)
    assert rows and rows[0].top_delta >= rows[-1].top_delta
    weights = {r.weight for r in rows}
    assert 1.0 in weights and 0.5 in weights


def test_write_condensed_report(tmp_path: Path):
    run_dir = _make_run(tmp_path)
    out = write_condensed_report(run_dir)
    assert out.exists()
    content = out.read_text(encoding='utf-8')
    assert 'weight,top_delta,sample_snippet' in content


def test_write_top_candidates_markdown(tmp_path: Path):
    run_dir = _make_run(tmp_path)
    md = write_top_candidates_markdown(run_dir, out_dir=tmp_path)
    assert md.exists()
    text = md.read_text(encoding='utf-8')
    assert '# Top K4 Candidates Report' in text
    assert 'Candidate 1' in text
