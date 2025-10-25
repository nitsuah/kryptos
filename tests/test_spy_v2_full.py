"""Test SPY v2.0 with full K1-K3 plaintexts."""

from __future__ import annotations

from kryptos.agents.spy import SpyAgent


def test_spy_v2_full_plaintexts():
    """Test SPY v2.0 on complete K1-K3 sentences."""

    # Full plaintext sections (with proper spacing for NLP)
    plaintexts = {
        'K1': "Between subtle shading and the absence of light lies the nuance of iqlusion",
        'K2': (
            "It was totally invisible. How's that possible? They used the earth's magnetic field. "
            "The information was gathered and transmitted undergruund to an unknown location. "
            "Does Langley know about this? They should. It's buried out there somewhere. "
            "Who knows the exact location? Only WW. This was his last message. "
            "Thirty eight degrees fifty seven minutes six point five seconds north, "
            "seventy seven degrees eight minutes forty four seconds west. Layer two."
        ),
        'K3': (
            "Slowly, desparately slowly, the remains of passage debris that encumbered the lower part "
            "of the doorway was removed. With trembling hands I made a tiny breach in the upper left "
            "hand corner. And then, widening the hole a little, I inserted the candle and peered in. "
            "The hot air escaping from the chamber caused the flame to flicker, but presently details "
            "of the room within emerged from the mist. Can you see anything? Q"
        ),
    }

    spy = SpyAgent()

    print("=" * 100)
    print("SPY v2.0 FULL PLAINTEXT ANALYSIS")
    print("=" * 100)
    print(f"NLP Status: {'ENABLED ✓' if spy.nlp_available else 'DISABLED ✗'}")
    print()

    for section, text in plaintexts.items():
        print(f"\n{'='*100}")
        print(f"{section} ANALYSIS")
        print(f"{'='*100}")
        print(f"Text length: {len(text)} characters")
        print(f"Preview: {text[:80]}...")
        print()

        results = spy.analyze_candidate(text, candidate_id=section)

        # Summary stats
        total = results['insight_count']
        nlp_count = len(results['nlp_insights'])
        classic_count = total - nlp_count
        high_conf = len(results['high_confidence_insights'])

        print("📊 RESULTS:")
        print(f"  Total Insights:       {total}")
        print(f"  Classic Patterns:     {classic_count}")
        print(f"  NLP Insights:         {nlp_count} {'(NLP ACTIVE ✓)' if nlp_count > 0 else ''}")
        print(f"  High Confidence:      {high_conf}")
        print(f"  Pattern Score:        {results['pattern_score']:.2f}")
        print()

        # Show NLP insights
        if results['nlp_insights']:
            print("🧠 NLP DISCOVERIES:")
            for insight in sorted(results['nlp_insights'], key=lambda x: x.confidence, reverse=True)[:5]:
                print(f"  [{insight.category:20s}] conf={insight.confidence:.2f} | {insight.description}")
                print(f"                          → {insight.evidence}")
            print()

        # Show top classic patterns
        classic_insights = [i for i in results['insights'] if not i.category.startswith('nlp_')]
        if classic_insights:
            print("🔍 TOP CLASSIC PATTERNS:")
            for insight in sorted(classic_insights, key=lambda x: x.confidence, reverse=True)[:3]:
                print(f"  [{insight.category:20s}] conf={insight.confidence:.2f} | {insight.description}")
            print()


if __name__ == '__main__':
    test_spy_v2_full_plaintexts()
