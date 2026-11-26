"""Rescore K4 candidates created before the real n-gram tables were loaded (2026-09-28)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from kryptos.k4.scoring import combined_plaintext_score

CUTOFF = "2026-09-28"


def rescore_rows(
    rows: list[tuple[int, float, str]],
    scorer: Callable[[str], float] = combined_plaintext_score,
) -> list[dict]:
    """Rescore a list of (id, old_score, text) rows.

    Returns a list of dicts with keys: id, old_score, new_score,
    sorted by new_score descending.
    """
    results = []
    for cid, old_score, text in rows:
        new_score = scorer(text)
        results.append({"id": cid, "old_score": old_score, "new_score": new_score})
    results.sort(key=lambda r: r["new_score"], reverse=True)
    return results


def run(
    conn,
    apply: bool = False,
    scorer: Callable[[str], float] = combined_plaintext_score,
) -> list[dict]:
    """Select pre-cutoff candidates, rescore them, optionally write back.

    Args:
        conn: psycopg2 connection (autocommit).
        apply: If True, UPDATE candidates with rescored_score in metrics JSONB.
        scorer: Scoring function (default: combined_plaintext_score).

    Returns:
        List of dicts with id, old_score, new_score sorted by new_score desc.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, score, text FROM candidates WHERE created_at < %s ORDER BY id",
            (CUTOFF,),
        )
        rows = cur.fetchall()

    results = rescore_rows(rows, scorer)

    if apply:
        with conn.cursor() as cur:
            for r in results:
                cur.execute(
                    "UPDATE candidates SET metrics = metrics || "
                    "jsonb_build_object('rescored_score', %s::double precision) WHERE id = %s",
                    (r["new_score"], r["id"]),
                )

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rescore pre-2026-09-28 K4 candidates")
    parser.add_argument("--apply", action="store_true", help="Write rescored_score to DB")
    parser.add_argument("--top", type=int, default=20, help="Number of top rows to print")
    args = parser.parse_args(argv)

    from kryptos.db import get_conn

    with get_conn() as conn:
        results = run(conn, apply=args.apply)

    print(f"Read {len(results)} candidate(s) created before {CUTOFF}")
    if results:
        for r in results[: args.top]:
            print(f"  id={r['id']} old={r['old_score']:.3f} new={r['new_score']:.3f}")
    if not args.apply:
        print("dry run, nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
