"""Run the bounded World Clock six-segment diagnostic and write a JSON artifact.

Usage:
    python scripts/run_k4_world_clock_diagnostic.py
    python scripts/run_k4_world_clock_diagnostic.py --output artifacts/world_clock.json
"""
from __future__ import annotations

import argparse
import json

from kryptos.k4.world_clock_hypothesis import write_world_clock_diagnostic


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="artifacts/K4_WORLD_CLOCK_SIX_SEGMENT_DIAGNOSTIC.json",
        help="JSON artifact path (default: %(default)s)",
    )
    args = parser.parse_args()
    report = write_world_clock_diagnostic(args.output)
    print(json.dumps({
        "artifact": args.output,
        "hypothesis_id": report["hypothesis_id"],
        "status": report["status"],
        "ciphertext_length": report["ciphertext_length"],
        "delimiter_positions_zero_based": report["delimiter_positions_zero_based"],
        "segment_lengths": report["segment_lengths"],
        "historical_city_count": report["historical_baseline"]["original_city_names"],
        "segment_letters_total": report["historical_baseline"]["segment_letters_total"],
        "matches_recorded_segment_lengths": report["matches_recorded_segment_lengths"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
