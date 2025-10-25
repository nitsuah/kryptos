"""Pipeline components for automated cryptanalysis.

This package provides pipeline components for systematic K4 attack generation,
including:
- Attack parameter generation from research hints
- Coverage-gap targeting
- Literature-informed attack strategies
- Deduplication and prioritization
"""

from kryptos.pipeline.attack_generator import AttackGenerator

__all__ = ["AttackGenerator"]
