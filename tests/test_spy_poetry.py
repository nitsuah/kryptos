"""Test SPY v2.0 enhanced NLP with poetry and fragment analysis."""

from __future__ import annotations

from kryptos.agents.spy import SpyAgent


def test_enhanced_nlp():
    """Test poetry/fragment analysis on K1-K3."""

    test_cases = [
        ("K1 (short)", "Between subtle shading and the absence of light lies the nuance of iqlusion"),
        ("K2 (medium)", "It was totally invisible hows that possible they used the earths magnetic field"),
        ("K3 (fragment)", "Slowly desparately slowly the remains of passage debris that encumbered"),
        ("Poetry test", "The light lies low and the shadow grows tall in the hall"),
        ("Alliteration", "Peter Piper picked a peck of pickled peppers perfectly"),
    ]

    spy = SpyAgent()

    print("=" * 100)
    print("SPY v2.0 ENHANCED NLP TEST - Poetry & Fragment Analysis")
    print("=" * 100)
    print(f"NLP Status: {'ENABLED ✓' if spy.nlp_available else 'DISABLED ✗'}")
    print()

    for name, text in test_cases:
        print(f"\n{'='*100}")
        print(f"TEST: {name}")
        print(f"{'='*100}")
        print(f"Text: {text}")
        print()

        results = spy.analyze_candidate(text, candidate_id=name)

        # Filter insights by category
        nlp_insights = results['nlp_insights']
        poetry_insights = [i for i in nlp_insights if 'poetry' in i.category]
        fragment_insights = [i for i in nlp_insights if 'fragment' in i.category]

        print("📊 Results:")
        print(f"  Total NLP Insights: {len(nlp_insights)}")
        print(f"  Poetry Patterns:    {len(poetry_insights)}")
        print(f"  Fragment Patterns:  {len(fragment_insights)}")
        print()

        if poetry_insights:
            print("🎵 Poetry Patterns:")
            for insight in poetry_insights:
                print(f"  [{insight.category:20s}] conf={insight.confidence:.2f}")
                print(f"    {insight.description}")
                print(f"    → {insight.evidence}")
                print()

        if fragment_insights:
            print("🔤 Fragment Patterns:")
            for insight in fragment_insights:
                print(f"  [{insight.category:20s}] conf={insight.confidence:.2f}")
                print(f"    {insight.description}")
                print(f"    → {insight.evidence}")
                print()


if __name__ == '__main__':
    test_enhanced_nlp()
