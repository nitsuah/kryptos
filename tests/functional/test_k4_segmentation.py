"""Edge-case tests for K4 segmentation helpers."""

from kryptos.k4.segmentation import generate_partitions, partitions_for_k4, slice_by_partition


def test_generate_partitions_handles_zero_negative_and_impossible_totals():
    assert generate_partitions(0, 2, 4) == [()]
    assert generate_partitions(-1, 2, 4) == []
    assert generate_partitions(5, 3, 4) == []
    assert generate_partitions(5, 4, 3) == []
    assert generate_partitions(24, 12, 12) == [(12, 12)]


def test_generate_partitions_returns_ordered_exact_partitions():
    assert generate_partitions(5, 2, 3) == [(2, 3), (3, 2)]


def test_generate_partitions_respects_result_limit():
    assert generate_partitions(5, 2, 3, limit=1) == [(2, 3)]
    assert generate_partitions(5, 2, 3, limit=0) == []


def test_partitions_for_k4_default_bounds_cover_all_97_characters():
    partitions_for_k4.cache_clear()

    partitions = partitions_for_k4()

    assert partitions
    assert len(partitions) <= 5000
    assert all(sum(partition) == 97 for partition in partitions)
    assert all(12 <= size <= 24 for partition in partitions for size in partition)


def test_partitions_for_k4_honors_custom_bounds_and_caches_results():
    partitions_for_k4.cache_clear()

    first = partitions_for_k4(97, 97)
    second = partitions_for_k4(97, 97)

    assert first == [(97,)]
    assert first is second


def test_slice_by_partition_returns_segments_in_order():
    assert slice_by_partition("ABCDEFGHIJ", (3, 2, 5)) == ["ABC", "DE", "FGHIJ"]
    assert slice_by_partition("ABCDE", (2, 2)) == ["AB", "CD"]
    assert slice_by_partition("ABC", (2, 2, 2)) == ["AB", "C", ""]


def test_slice_by_partition_handles_empty_input_and_partition():
    assert slice_by_partition("", ()) == []
    assert slice_by_partition("ABCDE", ()) == []
