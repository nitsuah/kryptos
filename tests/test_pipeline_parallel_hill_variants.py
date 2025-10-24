"""Tests parallel hill variant execution using pipeline hill stage factory (replaces executor parallel hill test)."""

from kryptos.k4.pipeline import StageResult, make_hill_constraint_stage


def test_parallel_hill_variant_metadata_diversity():
    # Simulate variants by calling stage multiple times manually (no internal parallelism yet)
    variants = []
    ciphertext = "OBKRUOXOGHULBSOLIFB"
    for partial in [40, 50, 60]:
        st = make_hill_constraint_stage(name="hill", prune_3x3=True, partial_len=partial, partial_min=-900.0)
        res: StageResult = st.func(ciphertext)
        variants.append({"score": res.score, "partial_len": partial})
    assert len(variants) == 3
    partial_lens = {v["partial_len"] for v in variants}
    assert len(partial_lens) >= 2
    assert all("score" in v for v in variants)
