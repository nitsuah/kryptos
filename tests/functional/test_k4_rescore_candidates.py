"""Functional tests for rescore_candidates (no real database)."""

from __future__ import annotations

import pytest

from kryptos.k4.rescore_candidates import rescore_rows, run


class FakeCursor:
    """Fake cursor that records execute calls."""

    def __init__(self, rows: list[tuple]):
        self._rows = rows
        self.execute_calls: list[tuple[str, tuple]] = []

    def execute(self, query: str, params: tuple = ()) -> None:
        self.execute_calls.append((query, params))

    def fetchall(self) -> list[tuple]:
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class FakeConn:
    """Fake connection that yields a FakeCursor."""

    def __init__(self, rows: list[tuple]):
        self._rows = rows
        self.cursors: list[FakeCursor] = []

    def cursor(self):
        cur = FakeCursor(self._rows)
        self.cursors.append(cur)
        return cur


def test_rescore_rows_sorts_by_new_score_desc():
    rows = [
        (1, 10.0, "AAAAA"),
        (2, 20.0, "BBBBB"),
        (3, 5.0, "CCCCC"),
    ]
    results = rescore_rows(rows, scorer=lambda t: float(len(t)))
    assert [r["id"] for r in results] == [1, 2, 3]  # all same length, stable by id
    assert [r["new_score"] for r in results] == [5.0, 5.0, 5.0]


def test_rescore_rows_uses_scorer():
    rows = [(1, 0.0, "HELLO"), (2, 0.0, "WORLD")]
    results = rescore_rows(rows, scorer=lambda t: 100.0 if "HELLO" in t else 50.0)
    assert results[0]["id"] == 1
    assert results[0]["new_score"] == 100.0
    assert results[1]["new_score"] == 50.0


def test_run_dry_run_only_selects():
    rows = [(1, 1.0, "TEXT1"), (2, 2.0, "TEXT2")]
    conn = FakeConn(rows)
    results = run(conn, apply=False)

    assert len(conn.cursors) == 1
    select_call = conn.cursors[0].execute_calls[0]
    assert "SELECT id, score, text FROM candidates WHERE created_at < %s" in select_call[0]
    assert select_call[1] == ("2026-09-28",)
    assert len(results) == 2


def test_run_apply_issues_one_update_per_row_no_score_or_rank():
    rows = [(1, 1.0, "TEXT1"), (2, 2.0, "TEXT2")]
    conn = FakeConn(rows)
    run(conn, apply=True)

    assert len(conn.cursors) == 2  # one for SELECT, one for UPDATE
    # Check UPDATE calls
    update_calls = conn.cursors[1].execute_calls
    assert len(update_calls) == 2
    for query, params in update_calls:
        assert "UPDATE candidates SET metrics = metrics || jsonb_build_object" in query
        assert "WHERE id = %s" in query
        assert "score =" not in query
        assert "rank =" not in query
        # params: (new_score, id)
        assert isinstance(params[0], float)
        assert isinstance(params[1], int)


def test_run_returns_results_sorted_by_new_score_desc():
    rows = [(1, 10.0, "AAA"), (2, 5.0, "BBBB"), (3, 1.0, "CCCCC")]
    conn = FakeConn(rows)
    results = run(conn, apply=False, scorer=lambda t: float(len(t)))
    # lengths: 3, 4, 5 -> sorted desc: 5, 4, 3
    assert [r["id"] for r in results] == [3, 2, 1]
    assert [r["new_score"] for r in results] == [5.0, 4.0, 3.0]


def test_run_uses_default_scorer():
    rows = [(1, 0.0, "THE QUICK BROWN FOX")]
    conn = FakeConn(rows)
    results = run(conn, apply=False)
    assert len(results) == 1
    assert isinstance(results[0]["new_score"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
