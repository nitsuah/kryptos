"""Direct tests for kryptos.spy.aggregate.aggregate_phrases."""

import csv

from kryptos.spy.aggregate import aggregate_phrases


def _write(path, rows):
    path.write_text("".join(row + "\n" for row in rows), encoding="utf-8")


def _read(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh, delimiter="\t"))


def test_missing_input_returns_minus_one_and_writes_nothing(tmp_path):
    out = tmp_path / "out" / "agg.tsv"
    assert aggregate_phrases(tmp_path / "nope.tsv", out) == -1
    assert not out.exists()
    assert not out.parent.exists()


def test_missing_input_verbose_reports_path(tmp_path, capsys):
    missing = tmp_path / "nope.tsv"
    assert aggregate_phrases(missing, tmp_path / "out.tsv", verbose=True) == -1
    assert "No input found" in capsys.readouterr().out


def test_duplicate_excerpt_keeps_highest_confidence(tmp_path):
    src = tmp_path / "in.tsv"
    _write(
        src,
        [
            "t1\tsrcA\tsame phrase\tlow",
            "t2\tsrcB\tsame phrase\thigh",
            "t3\tsrcC\tsame phrase\tmed",
        ],
    )
    out = tmp_path / "out.tsv"
    assert aggregate_phrases(src, out) == 1
    assert _read(out)[1] == ["same phrase", "srcB", "high"]


def test_later_lower_confidence_row_does_not_replace(tmp_path):
    src = tmp_path / "in.tsv"
    _write(src, ["t1\tsrcA\tp\tmed", "t2\tsrcB\tp\tlow"])
    out = tmp_path / "out.tsv"
    aggregate_phrases(src, out)
    assert _read(out)[1] == ["p", "srcA", "med"]


def test_malformed_rows_are_ignored(tmp_path):
    src = tmp_path / "in.tsv"
    _write(
        src,
        [
            "too\tfew\tcolumns",
            "a\tb\tc\td\te",
            "",
            "t1\tsrcA\tgood phrase\thigh",
        ],
    )
    out = tmp_path / "out.tsv"
    assert aggregate_phrases(src, out) == 1
    assert _read(out) == [["EXCERPT", "SOURCE", "CONFIDENCE"], ["good phrase", "srcA", "high"]]


def test_header_row_count_and_parent_dir_creation(tmp_path):
    src = tmp_path / "in.tsv"
    _write(src, ["t1\ts1\tone\tlow", "t2\ts2\ttwo\tmed", "t3\ts3\tone\tlow"])
    out = tmp_path / "deep" / "nested" / "agg.tsv"
    assert aggregate_phrases(src, out) == 2
    rows = _read(out)
    assert rows[0] == ["EXCERPT", "SOURCE", "CONFIDENCE"]
    assert len(rows) == 3
    assert {r[0] for r in rows[1:]} == {"one", "two"}


def test_verbose_prints_wrote(tmp_path, capsys):
    src = tmp_path / "in.tsv"
    _write(src, ["t1\ts1\tp\tlow"])
    out = tmp_path / "out.tsv"
    aggregate_phrases(src, out, verbose=True)
    assert "Wrote" in capsys.readouterr().out


def test_quiet_by_default(tmp_path, capsys):
    src = tmp_path / "in.tsv"
    _write(src, ["t1\ts1\tp\tlow"])
    aggregate_phrases(src, tmp_path / "out.tsv")
    assert capsys.readouterr().out == ""
