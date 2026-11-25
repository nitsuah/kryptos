"""Direct tests for the spy phrase aggregator."""

import csv

from kryptos.spy.aggregate import aggregate_phrases


def test_missing_input_returns_minus_one_without_writing_output(tmp_path):
    output = tmp_path / "out" / "phrases.tsv"

    assert aggregate_phrases(tmp_path / "missing.tsv", output) == -1
    assert not output.exists()


def test_duplicate_excerpt_keeps_high_confidence_over_later_low(tmp_path):
    source = tmp_path / "input.tsv"
    output = tmp_path / "phrases.tsv"
    source.write_text(
        "token1\tfirst-source\tshared excerpt\tlow\n"
        "token2\tbest-source\tshared excerpt\thigh\n"
        "token3\tlate-source\tshared excerpt\tlow\n",
        encoding="utf-8",
    )

    assert aggregate_phrases(source, output) == 1

    with output.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    assert rows == [
        ["EXCERPT", "SOURCE", "CONFIDENCE"],
        ["shared excerpt", "best-source", "high"],
    ]


def test_malformed_lines_are_ignored(tmp_path):
    source = tmp_path / "input.tsv"
    output = tmp_path / "phrases.tsv"
    source.write_text(
        "token1\tsource\tvalid excerpt\tmed\n"
        "only\tthree\tfields\n"
        "too\tmany\tfields\tto\tkeep\n",
        encoding="utf-8",
    )

    assert aggregate_phrases(source, output) == 1


def test_output_header_count_and_parent_directory(tmp_path):
    source = tmp_path / "input.tsv"
    output = tmp_path / "new" / "nested" / "phrases.tsv"
    source.write_text(
        "t1\tsource-a\texcerpt a\tlow\n"
        "t2\tsource-b\texcerpt b\tmed\n",
        encoding="utf-8",
    )

    assert aggregate_phrases(source, output) == 2
    assert output.exists()
    with output.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream, delimiter="\t"))
    assert rows[0] == ["EXCERPT", "SOURCE", "CONFIDENCE"]
    assert len(rows) == 3


def test_verbose_reports_output_path(tmp_path, capsys):
    source = tmp_path / "input.tsv"
    output = tmp_path / "phrases.tsv"
    source.write_text("t\tsource\texcerpt\thigh\n", encoding="utf-8")

    assert aggregate_phrases(source, output, verbose=True) == 1
    assert "Wrote" in capsys.readouterr().out
