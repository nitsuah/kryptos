"""Test SPY v2.0 NLP integration."""

from __future__ import annotations

from kryptos.agents.spy import SpyAgent


def test_spy_v2_on_k1_fragment():
    """Test SPY v2.0 with NLP on K1 plaintext fragment."""
    # K1 plaintext fragment with natural English
    k1_fragment = "Between subtle shading and the absence of light lies the nuance of iqlusion"

    spy = SpyAgent()

    print("=" * 80)
    print("SPY v2.0 ANALYSIS TEST")
    print("=" * 80)
    print(f"Input: {k1_fragment}")
    print(f"NLP Enabled: {spy.nlp_available}")
    print()

    results = spy.analyze_candidate(k1_fragment, candidate_id="K1_fragment")

    print(f"Total Insights: {results['insight_count']}")
    print(f"High Confidence: {len(results['high_confidence_insights'])}")
    print(f"NLP Insights: {len(results['nlp_insights'])}")
    print(f"Pattern Score: {results['pattern_score']:.4f}")
    print()

    # Show NLP insights specifically
    if results['nlp_insights']:
        print("NLP INSIGHTS:")
        print("-" * 80)
        for insight in results['nlp_insights']:
            print(f"  Category: {insight.category}")
            print(f"  Description: {insight.description}")
            print(f"  Evidence: {insight.evidence}")
            print(f"  Confidence: {insight.confidence:.2f}")
            print()

    # Show all high confidence insights
    print("HIGH CONFIDENCE INSIGHTS (all sources):")
    print("-" * 80)
    for insight in results['high_confidence_insights']:
        print(f"  [{insight.category}] {insight.description}")
        print(f"    Confidence: {insight.confidence:.2f}")
        print()

    return results


def test_spy_v1_vs_v2_comparison():
    """Compare SPY v1.0 (pattern-only) vs v2.0 (with NLP)."""
    test_texts = [
        "Between subtle shading and the absence of light lies the nuance",
        "It was totally invisible how is that possible they used the",
        "RANDOMLETTERSWITHNOMEANING XQZJKWPVBMFGH ZYXWVUTSRQP",
    ]

    spy = SpyAgent()

    print("=" * 80)
    print("SPY v1.0 vs v2.0 COMPARISON")
    print("=" * 80)
    print(f"NLP Status: {'ENABLED' if spy.nlp_available else 'DISABLED'}")
    print()

    for i, text in enumerate(test_texts, 1):
        print(f"Text {i}: {text[:60]}...")
        results = spy.analyze_candidate(text, candidate_id=f"test_{i}")

        total = results['insight_count']
        nlp_count = len(results['nlp_insights'])
        classic_count = total - nlp_count

        print(f"  Classic Patterns: {classic_count}")
        print(f"  NLP Insights: {nlp_count}")
        print(f"  Total: {total}")
        print(f"  Pattern Score: {results['pattern_score']:.4f}")
        print()


def test_k1_k2_k3_plaintexts():
    """Test SPY v2.0 on known K1-K3 plaintexts."""
    plaintexts = {
        'K1': "Between subtle shading and the absence of light lies the nuance of iqlusion",
        'K2': "It was totally invisible hows that possible they used the earths magnetic field",
        'K3': "Slowly desparatly slowly the remains of passage debris that encumbered",
    }

    spy = SpyAgent()

    print("=" * 80)
    print("SPY v2.0 ON KNOWN PLAINTEXTS (K1-K3)")
    print("=" * 80)
    print(f"NLP Enabled: {spy.nlp_available}")
    print()

    for section, text in plaintexts.items():
        print(f"{section}: {text}")
        results = spy.analyze_candidate(text, candidate_id=section)

        print(f"  Total Insights: {results['insight_count']}")
        print(f"  High Confidence: {len(results['high_confidence_insights'])}")
        print(f"  NLP Insights: {len(results['nlp_insights'])}")
        print(f"  Pattern Score: {results['pattern_score']:.4f}")

        # Show top NLP insights
        nlp_insights = sorted(results['nlp_insights'], key=lambda x: x.confidence, reverse=True)[:3]
        if nlp_insights:
            print("  Top NLP Patterns:")
            for insight in nlp_insights:
                print(f"    - {insight.description} (conf: {insight.confidence:.2f})")
        print()


if __name__ == '__main__':
    print("\n")

    # Test 1: K1 fragment detailed analysis
    test_spy_v2_on_k1_fragment()

    print("\n" * 2)

    # Test 2: Compare different text types
    test_spy_v1_vs_v2_comparison()

    print("\n" * 2)

    # Test 3: K1-K3 analysis
    test_k1_k2_k3_plaintexts()
