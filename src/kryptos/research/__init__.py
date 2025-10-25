"""Research module for academic paper integration."""

# Academic paper integration (Sprint 4.2)
from .attack_extractor import AttackExtractor, ExtractedAttack
from .paper_search import Paper, PaperSearch

__all__ = ["PaperSearch", "Paper", "AttackExtractor", "ExtractedAttack"]
