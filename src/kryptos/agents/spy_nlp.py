"""SPY v2.0 NLP Module: Advanced linguistic analysis for pattern recognition.

This module provides NLP-powered enhancements to the SPY agent using spaCy and NLTK.
Features include:
- Named Entity Recognition (NER) for detecting proper nouns
- Part-of-Speech (POS) tagging for grammatical structure
- Dependency parsing for phrase relationships
- WordNet integration for semantic similarity
- Poetry/fragment analysis (rhyme, meter, alliteration, assonance)
- Cryptographic text patterns (word shapes, phonetics)
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

try:
    import spacy
    from nltk.corpus import cmudict
    from nltk.corpus import wordnet as wn

    SPACY_AVAILABLE = True
    WORDNET_AVAILABLE = True

    try:
        PRONUNCIATIONS = cmudict.dict()
        PHONETICS_AVAILABLE = True
    except LookupError:
        PHONETICS_AVAILABLE = False
        PRONUNCIATIONS = {}
except ImportError:
    SPACY_AVAILABLE = False
    WORDNET_AVAILABLE = False
    PHONETICS_AVAILABLE = False
    PRONUNCIATIONS = {}


@dataclass
class NLPInsight:
    category: str
    description: str
    evidence: str
    confidence: float
    position: int | None = None
    metadata: dict[str, Any] | None = None


class SpyNLP:
    def __init__(self, model_name: str = "en_core_web_sm"):
        if not SPACY_AVAILABLE:
            raise ImportError(
                "spaCy not installed. Install with: pip install spacy && python -m spacy download en_core_web_sm",
            )

        self.nlp = spacy.load(model_name)
        self.wordnet_available = WORDNET_AVAILABLE

    def analyze(self, text: str) -> list[NLPInsight]:
        insights = []

        doc = self.nlp(text)

        insights.extend(self._extract_entities(doc))

        insights.extend(self._analyze_pos_patterns(doc))

        insights.extend(self._analyze_dependencies(doc))

        if self.wordnet_available:
            insights.extend(self._semantic_analysis(doc))

        insights.extend(self._analyze_fragments(text, doc))
        insights.extend(self._analyze_phonetic_patterns(text, doc))

        return insights

    def _extract_entities(self, doc) -> list[NLPInsight]:
        insights = []

        for ent in doc.ents:
            confidence = self._calculate_ner_confidence(ent)

            insights.append(
                NLPInsight(
                    category="ner",
                    description=f"Named entity detected: {ent.label_}",
                    evidence=ent.text,
                    confidence=confidence,
                    position=ent.start_char,
                    metadata={
                        "label": ent.label_,
                        "label_meaning": spacy.explain(ent.label_),
                        "start": ent.start,
                        "end": ent.end,
                    },
                ),
            )

        return insights

    def _analyze_pos_patterns(self, doc) -> list[NLPInsight]:
        insights = []

        for chunk in doc.noun_chunks:
            if chunk.root.pos_ == "PROPN":
                insights.append(
                    NLPInsight(
                        category="pos",
                        description="Proper noun phrase detected",
                        evidence=chunk.text,
                        confidence=0.7,
                        position=chunk.start_char,
                        metadata={"chunk_type": "noun_phrase", "pos": "PROPN"},
                    ),
                )

        verb_sequences = []
        current_verbs = []
        for token in doc:
            if token.pos_ == "VERB":
                current_verbs.append(token.text)
            elif current_verbs:
                if len(current_verbs) >= 2:
                    verb_sequences.append(" ".join(current_verbs))
                current_verbs = []

        for seq in verb_sequences:
            insights.append(
                NLPInsight(
                    category="pos",
                    description="Verb sequence detected",
                    evidence=seq,
                    confidence=0.6,
                    metadata={"pattern_type": "verb_sequence"},
                ),
            )

        return insights

    def _analyze_dependencies(self, doc) -> list[NLPInsight]:
        insights = []

        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subjects = [child for child in token.children if child.dep_ in ("nsubj", "nsubjpass")]
                objects = [child for child in token.children if child.dep_ in ("dobj", "pobj")]

                if subjects and objects:
                    pattern = f"{subjects[0].text} {token.text} {objects[0].text}"
                    insights.append(
                        NLPInsight(
                            category="dependency",
                            description="Subject-Verb-Object pattern detected",
                            evidence=pattern,
                            confidence=0.8,
                            metadata={
                                "subject": subjects[0].text,
                                "verb": token.text,
                                "object": objects[0].text,
                            },
                        ),
                    )

        return insights

    def _semantic_analysis(self, doc) -> list[NLPInsight]:
        insights = []

        content_words = [token for token in doc if token.pos_ in ("NOUN", "VERB", "ADJ")]

        for i, token1 in enumerate(content_words):
            for token2 in content_words[i + 1 :]:
                if self._are_semantically_related(token1.lemma_, token2.lemma_):
                    insights.append(
                        NLPInsight(
                            category="semantic",
                            description="Semantic relationship detected",
                            evidence=f"{token1.text} <-> {token2.text}",
                            confidence=0.6,
                            metadata={
                                "word1": token1.text,
                                "word2": token2.text,
                                "lemma1": token1.lemma_,
                                "lemma2": token2.lemma_,
                            },
                        ),
                    )

        return insights

    def _calculate_ner_confidence(self, ent) -> float:
        base_confidence = 0.7

        high_confidence_types = {"PERSON", "GPE", "ORG", "DATE"}
        if ent.label_ in high_confidence_types:
            base_confidence = 0.9

        if len(ent.text) > 10:
            base_confidence = min(1.0, base_confidence + 0.1)

        return base_confidence

    def _are_semantically_related(self, word1: str, word2: str, threshold: float = 0.5) -> bool:
        try:
            synsets1 = wn.synsets(word1.lower())
            synsets2 = wn.synsets(word2.lower())

            if not synsets1 or not synsets2:
                return False

            for s1 in synsets1[:3]:
                for s2 in synsets2[:3]:
                    similarity = s1.path_similarity(s2)
                    if similarity and similarity > threshold:
                        return True

            return False
        except Exception:
            return False

    def _analyze_fragments(self, text: str, doc) -> list[NLPInsight]:
        insights = []
        words = [token.text.lower() for token in doc if token.is_alpha]

        if len(words) < 2:
            return insights

        initial_sounds = [word[0] for word in words if word]
        sound_counts = Counter(initial_sounds)
        for sound, count in sound_counts.items():
            if count >= 3:
                matching_words = [w for w in words if w[0] == sound]
                insights.append(
                    NLPInsight(
                        category="poetry",
                        description=f"Alliteration detected: '{sound}' sound",
                        evidence=", ".join(matching_words[:5]),
                        confidence=min(0.9, 0.5 + count * 0.1),
                        metadata={"pattern_type": "alliteration", "count": count},
                    ),
                )

        vowel_patterns = []
        for word in words:
            vowels = re.findall(r'[aeiou]+', word)
            if vowels:
                vowel_patterns.append((word, vowels[0]))

        if vowel_patterns:
            vowel_counts = Counter(v for _, v in vowel_patterns)
            for vowel, count in vowel_counts.items():
                if count >= 3:
                    matching = [w for w, v in vowel_patterns if v == vowel]
                    insights.append(
                        NLPInsight(
                            category="poetry",
                            description=f"Assonance detected: '{vowel}' sound",
                            evidence=", ".join(matching[:5]),
                            confidence=min(0.85, 0.45 + count * 0.1),
                            metadata={"pattern_type": "assonance", "count": count},
                        ),
                    )

        shapes = {}
        for word in words:
            if 3 <= len(word) <= 6:
                shape = ''.join('V' if c in 'aeiou' else 'C' for c in word)
                if shape not in shapes:
                    shapes[shape] = []
                shapes[shape].append(word)

        for shape, shape_words in shapes.items():
            if len(shape_words) >= 3:
                insights.append(
                    NLPInsight(
                        category="fragment",
                        description=f"Word shape pattern: {shape}",
                        evidence=", ".join(shape_words[:5]),
                        confidence=0.6,
                        metadata={"pattern_type": "word_shape", "shape": shape},
                    ),
                )

        coherent_pairs = 0
        for i in range(len(doc) - 1):
            token1, token2 = doc[i], doc[i + 1]
            if (
                (token1.pos_ == "ADJ" and token2.pos_ == "NOUN")
                or (token1.pos_ == "NOUN" and token2.pos_ == "VERB")
                or (token1.pos_ == "DET" and token2.pos_ == "NOUN")
            ):
                coherent_pairs += 1

        if coherent_pairs >= 2:
            coherence_ratio = coherent_pairs / max(1, len(words) - 1)
            if coherence_ratio >= 0.3:
                insights.append(
                    NLPInsight(
                        category="fragment",
                        description="Phrase coherence detected (grammatical word pairs)",
                        evidence=f"{coherent_pairs} coherent pairs found",
                        confidence=min(0.9, 0.5 + coherence_ratio),
                        metadata={"coherent_pairs": coherent_pairs, "ratio": coherence_ratio},
                    ),
                )

        return insights

    def _analyze_phonetic_patterns(self, text: str, doc) -> list[NLPInsight]:
        insights = []

        if not PHONETICS_AVAILABLE:
            return insights

        words = [token.text.lower() for token in doc if token.is_alpha and len(token.text) > 2]

        if len(words) < 3:
            return insights

        word_phonemes = {}
        for word in words:
            if word in PRONUNCIATIONS:
                word_phonemes[word] = PRONUNCIATIONS[word][0]

        if len(word_phonemes) < 3:
            return insights

        rhyme_groups = {}
        for word, phonemes in word_phonemes.items():
            if len(phonemes) >= 2:
                rhyme_sound = tuple(phonemes[-2:])
                if rhyme_sound not in rhyme_groups:
                    rhyme_groups[rhyme_sound] = []
                rhyme_groups[rhyme_sound].append(word)

        for rhyme_sound, rhyming_words in rhyme_groups.items():
            if len(rhyming_words) >= 2:
                insights.append(
                    NLPInsight(
                        category="poetry",
                        description=f"Rhyme detected: {len(rhyming_words)} words",
                        evidence=", ".join(rhyming_words),
                        confidence=min(0.95, 0.6 + len(rhyming_words) * 0.15),
                        metadata={"pattern_type": "rhyme", "rhyme_sound": str(rhyme_sound)},
                    ),
                )

        syllable_counts = []
        for _word, phonemes in word_phonemes.items():
            syllables = sum(1 for p in phonemes if p[-1].isdigit())
            syllable_counts.append(syllables)

        if len(syllable_counts) >= 5:
            avg_syllables = sum(syllable_counts) / len(syllable_counts)
            variance = sum((s - avg_syllables) ** 2 for s in syllable_counts) / len(syllable_counts)

            if variance < 1.0 and 2.0 <= avg_syllables <= 3.0:
                insights.append(
                    NLPInsight(
                        category="poetry",
                        description=f"Regular meter detected (avg {avg_syllables:.1f} syllables/word)",
                        evidence=f"Syllable pattern: {syllable_counts[:8]}",
                        confidence=0.8,
                        metadata={"pattern_type": "meter", "avg_syllables": avg_syllables},
                    ),
                )

        return insights

    def extract_key_phrases(self, text: str, top_n: int = 10) -> list[tuple[str, float]]:
        doc = self.nlp(text)

        phrases = []

        for ent in doc.ents:
            score = 1.0 if ent.label_ in {"PERSON", "GPE", "ORG"} else 0.8
            phrases.append((ent.text, score))

        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                phrases.append((chunk.text, 0.6))

        unique_phrases = {}
        for phrase, score in phrases:
            phrase_clean = phrase.strip().upper()
            if phrase_clean not in unique_phrases or score > unique_phrases[phrase_clean]:
                unique_phrases[phrase_clean] = score

        sorted_phrases = sorted(unique_phrases.items(), key=lambda x: x[1], reverse=True)
        return sorted_phrases[:top_n]


def test_spy_nlp():
    if not SPACY_AVAILABLE:
        print("spaCy not available - skipping test")
        return

    nlp = SpyNLP()

    test_text = "Between subtle shading and the absence of light lies the nuance of iqlusion"

    print("Analyzing:", test_text)
    print()

    insights = nlp.analyze(test_text)

    print(f"Found {len(insights)} insights:")
    for insight in insights:
        print(f"  [{insight.category}] {insight.description}: {insight.evidence}")

    print()
    phrases = nlp.extract_key_phrases(test_text)
    print("Key phrases:")
    for phrase, score in phrases:
        print(f"  {phrase} (score: {score:.2f})")


if __name__ == "__main__":
    test_spy_nlp()
