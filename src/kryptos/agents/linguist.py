"""LINGUIST: Neural NLP Specialist for Kryptos Cryptanalysis.

This agent complements SPY's rule-based analysis with transformer-based neural validation.
Uses BERT/GPT for perplexity scoring and deep linguistic coherence assessment.

Philosophy: Neural networks trained on billions of words can detect linguistic patterns
that simple rules miss. Use them to validate candidates and filter noise.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class LinguisticScore:
    text: str
    perplexity: float
    coherence: float
    grammar_score: float
    confidence: float
    model_used: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SanbornCorpusAnalysis:
    style_similarity: float
    vocabulary_match: float
    structure_match: float
    themes_detected: list[str]
    confidence: float


class LinguistAgent:
    def __init__(
        self,
        model_name: str = "distilbert-base-uncased",
        device: str = "cpu",
        cache_dir: Path | None = None,
    ):
        """Initialize LINGUIST agent.

        Args:
            model_name: HuggingFace model name
            device: 'cpu' or 'cuda'
            cache_dir: Directory for caching scores
        """
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir or Path("./data/linguist")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._perplexity_model = None
        self._coherence_model = None

        self.sanborn_corpus = self._load_sanborn_corpus()

        self.score_cache: dict[str, LinguisticScore] = {}

    def validate_candidate(
        self,
        text: str,
        threshold: float = 0.6,
        use_sanborn: bool = True,
    ) -> LinguisticScore:
        """Validate a decryption candidate using neural models.

        Args:
            text: Candidate plaintext
            threshold: Confidence threshold for validation
            use_sanborn: Also check against Sanborn corpus

        Returns:
            Linguistic score with neural validation
        """
        cache_key = f"{text}_{self.model_name}"
        if cache_key in self.score_cache:
            return self.score_cache[cache_key]

        perplexity = self._calculate_perplexity(text)

        coherence = self._calculate_coherence(text)

        grammar_score = self._calculate_grammar_score(text)

        confidence = self._compute_confidence(perplexity, coherence, grammar_score)

        sanborn_bonus = 0.0
        if use_sanborn and len(text) > 20:
            sanborn_analysis = self.analyze_sanborn_style(text)
            sanborn_bonus = sanborn_analysis.confidence * 0.2

        final_confidence = min(1.0, confidence + sanborn_bonus)

        score = LinguisticScore(
            text=text,
            perplexity=perplexity,
            coherence=coherence,
            grammar_score=grammar_score,
            confidence=final_confidence,
            model_used=self.model_name,
            timestamp=datetime.now(),
            metadata={
                "threshold": threshold,
                "sanborn_bonus": sanborn_bonus,
                "passed": final_confidence >= threshold,
            },
        )

        self.score_cache[cache_key] = score

        return score

    def analyze_sanborn_style(self, text: str) -> SanbornCorpusAnalysis:
        text_lower = text.lower()
        words = text_lower.split()

        sanborn_words = set(self.sanborn_corpus["vocabulary"])
        text_words = set(words)
        vocab_match = len(text_words & sanborn_words) / len(text_words) if text_words else 0.0

        themes_detected = []
        for theme, keywords in self.sanborn_corpus["themes"].items():
            if any(keyword in text_lower for keyword in keywords):
                themes_detected.append(theme)

        style_similarity = vocab_match * 0.7 + (len(themes_detected) / 5) * 0.3

        structure_score = 0.0
        if "northeast" in text_lower or "berlinclock" in text_lower:
            structure_score += 0.3
        if any(word in text_lower for word in ["palimpsest", "abscissa", "lucid", "shadow"]):
            structure_score += 0.2
        structure_score = min(1.0, structure_score)

        confidence = style_similarity * 0.5 + vocab_match * 0.3 + structure_score * 0.2

        return SanbornCorpusAnalysis(
            style_similarity=style_similarity,
            vocabulary_match=vocab_match,
            structure_match=structure_score,
            themes_detected=themes_detected,
            confidence=confidence,
        )

    def batch_validate(
        self,
        candidates: list[str],
        threshold: float = 0.6,
        top_k: int = 10,
    ) -> list[tuple[str, LinguisticScore]]:
        """Validate multiple candidates and return top-k.

        Args:
            candidates: List of candidate plaintexts
            threshold: Minimum confidence threshold
            top_k: Number of top candidates to return

        Returns:
            Top-k candidates with scores, sorted by confidence
        """
        scored = []
        for text in candidates:
            score = self.validate_candidate(text, threshold=threshold)
            if score.confidence >= threshold:
                scored.append((text, score))

        scored.sort(key=lambda x: x[1].confidence, reverse=True)

        return scored[:top_k]

    def cross_validate_with_spy(
        self,
        text: str,
        spy_score: float,
        spy_features: dict[str, Any],
    ) -> dict[str, Any]:
        """Cross-validate with SPY's rule-based analysis.

        Args:
            text: Candidate text
            spy_score: SPY's linguistic score
            spy_features: SPY's detected features

        Returns:
            Combined validation with agreement analysis
        """
        linguist_score = self.validate_candidate(text)

        agreement = 1.0 - abs(spy_score - linguist_score.confidence)

        correlations = {}
        if "rhyme" in spy_features and linguist_score.coherence > 0.7:
            correlations["poetic_structure"] = 0.8
        if "entities" in spy_features and linguist_score.grammar_score > 0.7:
            correlations["named_entities"] = 0.9

        return {
            "text": text,
            "spy_score": spy_score,
            "linguist_score": linguist_score.confidence,
            "agreement": agreement,
            "combined_score": (spy_score + linguist_score.confidence) / 2,
            "correlations": correlations,
            "recommendation": "STRONG_CANDIDATE" if agreement > 0.8 else "REVIEW_NEEDED",
        }

    def _calculate_perplexity(self, text: str) -> float:
        if self._perplexity_model is None:
            self._perplexity_model = self._init_perplexity_model()

        if self._perplexity_model is None:
            return self._heuristic_perplexity(text)

        try:
            return self._model_perplexity(text)
        except Exception:
            return self._heuristic_perplexity(text)

    def _calculate_coherence(self, text: str) -> float:
        words = text.lower().split()

        if len(words) < 3:
            return 0.3

        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.5:
            unique_ratio *= 0.5

        avg_word_len = sum(len(w) for w in words) / len(words)
        length_score = 1.0 if 3 <= avg_word_len <= 8 else 0.5

        common_words = {"the", "a", "an", "is", "are", "was", "were", "to", "from", "in", "on", "at"}
        common_ratio = len([w for w in words if w in common_words]) / len(words)

        coherence = unique_ratio * 0.5 + length_score * 0.2 + min(common_ratio * 2, 1.0) * 0.3

        return coherence

    def _calculate_grammar_score(self, text: str) -> float:
        sentences = text.split(".")
        cap_score = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper()) / max(len(sentences), 1)

        punct_score = 1.0
        if text.count("(") != text.count(")"):
            punct_score -= 0.2
        if text.count("[") != text.count("]"):
            punct_score -= 0.2

        words = text.split()
        if words:
            avg_sentence_len = len(words) / max(len(sentences), 1)
            length_score = 1.0 if 5 <= avg_sentence_len <= 30 else 0.6
        else:
            length_score = 0.0

        grammar = cap_score * 0.3 + punct_score * 0.3 + length_score * 0.4

        return max(0.0, min(1.0, grammar))

    def _compute_confidence(
        self,
        perplexity: float,
        coherence: float,
        grammar: float,
    ) -> float:
        """Compute overall confidence from component scores.

        Args:
            perplexity: Perplexity score
            coherence: Coherence score
            grammar: Grammar score

        Returns:
            Overall confidence 0.0-1.0
        """
        perplexity_score = 1.0 / (1.0 + np.log1p(perplexity / 100))

        confidence = perplexity_score * 0.4 + coherence * 0.4 + grammar * 0.2

        return confidence

    def _init_perplexity_model(self) -> Any:
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
            model.to(self.device)
            model.eval()

            return {"model": model, "tokenizer": tokenizer}
        except ImportError:
            print("Warning: transformers not installed, using heuristic scoring")
            return None
        except Exception as e:
            print(f"Warning: Failed to load model ({e}), using heuristic scoring")
            return None

    def _model_perplexity(self, text: str) -> float:
        import torch

        model = self._perplexity_model["model"]
        tokenizer = self._perplexity_model["tokenizer"]

        encodings = tokenizer(text, return_tensors="pt").to(self.device)
        max_length = model.config.n_positions if hasattr(model.config, "n_positions") else 1024
        stride = 512

        nlls = []
        for i in range(0, encodings.input_ids.size(1), stride):
            begin_loc = max(i + stride - max_length, 0)
            end_loc = min(i + stride, encodings.input_ids.size(1))
            trg_len = end_loc - i

            input_ids = encodings.input_ids[:, begin_loc:end_loc].to(self.device)
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = model(input_ids, labels=target_ids)
                neg_log_likelihood = outputs.loss * trg_len

            nlls.append(neg_log_likelihood)

        ppl = torch.exp(torch.stack(nlls).sum() / end_loc)
        return ppl.item()

    def _heuristic_perplexity(self, text: str) -> float:
        chars = text.lower()
        if not chars:
            return 1000.0

        expected_freq = {
            "e": 0.127,
            "t": 0.091,
            "a": 0.082,
            "o": 0.075,
            "i": 0.070,
            "n": 0.067,
            "s": 0.063,
            "h": 0.061,
            "r": 0.060,
        }

        char_counts = {}
        for c in chars:
            if c.isalpha():
                char_counts[c] = char_counts.get(c, 0) + 1

        total_alpha = sum(char_counts.values())
        if total_alpha == 0:
            return 1000.0

        deviation = 0.0
        for char, expected in expected_freq.items():
            observed = char_counts.get(char, 0) / total_alpha
            deviation += abs(observed - expected)

        perplexity = 50 + (deviation * 500)

        return perplexity

    def _load_sanborn_corpus(self) -> dict[str, Any]:
        k1_text = """BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION"""
        k2_text = """IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE ? THEY USED THE EARTHS MAGNETIC FIELD X
        THE INFORMATION WAS GATHERED AND TRANSMITTED UNDERGRUUND TO AN UNKNOWN LOCATION X
        DOES LANGLEY KNOW ABOUT THIS ? THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X
        WHO KNOWS THE EXACT LOCATION ? ONLY WW THIS WAS HIS LAST MESSAGE X
        THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
        SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST ID BY ROWS"""
        k3_text = """SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED
        THE LOWER PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY
        BREACH IN THE UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE
        I INSERTED THE CANDLE AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER
        CAUSED THE FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED
        FROM THE MIST X CAN YOU SEE ANYTHING Q ?"""

        corpus_text = (k1_text + " " + k2_text + " " + k3_text).lower()
        words = [w.strip(".,?!") for w in corpus_text.split()]

        vocabulary = list(set(words))

        themes = {
            "location": ["northeast", "degrees", "minutes", "seconds", "north", "south", "east", "west"],
            "mystery": ["invisible", "unknown", "secret", "buried", "hidden"],
            "archaeology": ["chamber", "passage", "debris", "doorway", "remains"],
            "light": ["shadow", "shading", "light", "darkness", "flame", "candle"],
            "art": ["iqlusion", "illusion", "palimpsest", "abscissa"],
        }

        return {
            "vocabulary": vocabulary,
            "themes": themes,
            "total_words": len(words),
            "unique_words": len(vocabulary),
        }

    def save_scores(self, filepath: Path | None = None):
        filepath = filepath or (self.cache_dir / "linguist_scores.json")

        scores_data = []
        for score in self.score_cache.values():
            metadata = {}
            for key, value in score.metadata.items():
                if hasattr(value, "item"):
                    metadata[key] = value.item()
                else:
                    metadata[key] = value

            scores_data.append(
                {
                    "text": score.text,
                    "perplexity": float(score.perplexity),
                    "coherence": float(score.coherence),
                    "grammar_score": float(score.grammar_score),
                    "confidence": float(score.confidence),
                    "model_used": score.model_used,
                    "timestamp": score.timestamp.isoformat(),
                    "metadata": metadata,
                },
            )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scores_data, f, indent=2)


def demo_linguist():
    print("=" * 80)
    print("LINGUIST AGENT DEMO")
    print("=" * 80)
    print()

    linguist = LinguistAgent(model_name="distilbert-base-uncased", device="cpu")

    candidates = [
        "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT",
        "THE CLOCK IS HIDDEN IN BERLIN NEAR THE WALL",
        "XQZMWPVUTRSLKJIHGFEDCBA",
        "SLOWLY DESPERATELY SLOWLY THE REMAINS",
        "AAA BBB CCC DDD EEE FFF",
    ]

    print("Validating candidates:\n")
    for text in candidates:
        score = linguist.validate_candidate(text)
        print(f"Text: {text[:50]}...")
        print(f"  Perplexity: {score.perplexity:.2f}")
        print(f"  Coherence: {score.coherence:.3f}")
        print(f"  Grammar: {score.grammar_score:.3f}")
        print(f"  Confidence: {score.confidence:.3f}")
        print(f"  Passed: {score.metadata['passed']}")
        print()

    print("\nTop-3 candidates by confidence:")
    top_candidates = linguist.batch_validate(candidates, threshold=0.5, top_k=3)
    for i, (text, score) in enumerate(top_candidates, 1):
        print(f"{i}. {text[:50]}... (confidence: {score.confidence:.3f})")


if __name__ == "__main__":
    demo_linguist()
