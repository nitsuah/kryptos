"""Tests using Pipeline (migrated from legacy executor tests) for pattern bonus and simple pruning mimic.

Focus: Remove reliance on PipelineExecutor for pattern bonus verification.
"""

from kryptos.k4.pipeline import Pipeline, Stage
from kryptos.k4.scoring import baseline_stats


def _dummy_stage_factory(candidates):
    def _run(_ct: str):
        # mimic StageResult structure via simple dict
        # Stage expects a callable returning StageResult in the real pipeline
        from kryptos.k4.pipeline import StageResult  # local import to avoid circular issues at module load

        # choose best by score
        best = sorted(candidates, key=lambda c: c.get('score', 0.0), reverse=True)[0]
        return StageResult(name='dummy', output=best['text'], metadata={'candidates': candidates}, score=best['score'])

    return _run


def test_pattern_bonus_in_baseline_stats():
    stats_good = baseline_stats('BERLIN CLOCK')
    assert stats_good.get('berlin_clock_pattern_bonus') == 1.0
    stats_bad = baseline_stats('CLOCK BERLIN')
    assert stats_bad.get('berlin_clock_pattern_bonus') == 0.0


def test_pipeline_runs_and_attaches_duration():
    cands = [
        {'text': 'BERLIN CLOCK', 'score': 100.0},
        {'text': 'CLOCK BERLIN', 'score': 10.0},
    ]
    stage = Stage(name='dummy', func=_dummy_stage_factory(cands))
    pipe = Pipeline([stage])
    results = pipe.run('X')
    assert len(results) == 1
    res = results[0]
    assert res.metadata.get('duration') is not None
    # ensure best candidate surfaced
    assert res.output == 'BERLIN CLOCK'
