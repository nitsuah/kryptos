"""Segmentation utilities for K4 hypothesis testing.

Generates partitions of the ciphertext length into block sizes within a
specified range. Used for layered substitution block hypothesis.
"""

from functools import lru_cache


def generate_partitions(total: int, min_len: int, max_len: int, limit: int = 10000) -> list[tuple[int, ...]]:
    results: list[tuple[int, ...]] = []

    def dfs(remaining: int, current: list[int]):
        if len(results) >= limit:
            return
        if remaining == 0:
            results.append(tuple(current))
            return
        min_possible_parts = (remaining + max_len - 1) // max_len
        max_possible_parts = remaining // min_len
        if min_possible_parts > max_possible_parts:
            return
        for size in range(min_len, max_len + 1):
            if size > remaining:
                break
            current.append(size)
            dfs(remaining - size, current)
            current.pop()

    dfs(total, [])
    return results


@lru_cache(maxsize=1024)
def partitions_for_k4(min_len: int = 12, max_len: int = 24) -> list[tuple[int, ...]]:
    k4_len = 97
    return generate_partitions(k4_len, min_len, max_len, limit=5000)


def slice_by_partition(text: str, partition: tuple[int, ...]) -> list[str]:
    segments: list[str] = []
    idx = 0
    for length in partition:
        segments.append(text[idx : idx + length])
        idx += length
    return segments
