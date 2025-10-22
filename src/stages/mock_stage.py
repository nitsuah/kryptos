from __future__ import annotations

from src.scoring.fitness import compute_meta_and_score

from .interface import DEFAULT_WEIGHTS, CandidateResult, Stage, StageContext


class MockStage(Stage):
    """Produces trivial candidates for testing."""

    def run(self, ctx: StageContext) -> list[CandidateResult]:
        if not ctx.ciphertext:
            return []
        base = ctx.ciphertext[:3]
        variants = {base, base.lower(), base[::-1]}
        results: list[CandidateResult] = []
        for v in variants:
            meta = compute_meta_and_score(v, DEFAULT_WEIGHTS)
            results.append(CandidateResult(text=v, score=meta["score"], meta=meta))
        return results


# TODO: Extend with parameter-driven generation logic.
