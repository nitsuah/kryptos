#!/usr/bin/env python3
"""Unified hypothesis runner - replaces all individual hypothesis scripts.

Usage:
    python run_hypothesis.py hill_2x2
    python run_hypothesis.py vigenere --max-length 30
    python run_hypothesis.py playfair
    python run_hypothesis.py --list
"""

import argparse
import sys

from kryptos.k4.hypotheses import (
    BerlinClockTranspositionHypothesis,
    HillCipher2x2Hypothesis,
    PlayfairHypothesis,
    SimpleSubstitutionHypothesis,
    VigenereHypothesis,
)
from kryptos.k4.hypothesis_runner import run_hypothesis_search

# Hypothesis registry - add new hypotheses here
HYPOTHESES = {
    'hill_2x2': {
        'class': HillCipher2x2Hypothesis,
        'params': {},
        'description': 'Exhaustive 2x2 Hill cipher search (~158k keys)',
    },
    'vigenere': {
        'class': VigenereHypothesis,
        'params': {
            'min_key_length': 1,
            'max_key_length': 30,
            'keys_per_length': 50,
            'explicit_keywords': ['BERLIN', 'CLOCK', 'KRYPTOS', 'ABSCISSA', 'PALIMPSEST'],
        },
        'description': 'Vigenère cipher with frequency analysis + explicit keywords',
    },
    'playfair': {
        'class': PlayfairHypothesis,
        'params': {},
        'description': 'Playfair cipher with Sanborn keywords',
    },
    'transposition': {
        'class': BerlinClockTranspositionHypothesis,
        'params': {},
        'description': 'Columnar transposition with Berlin Clock periods',
    },
    'substitution': {
        'class': SimpleSubstitutionHypothesis,
        'params': {},
        'description': 'Simple substitution (Caesar, Atbash, Reverse)',
    },
}


def main():
    parser = argparse.ArgumentParser(
        description='Run K4 hypothesis search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'hypothesis',
        nargs='?',
        help='Hypothesis to run (e.g., hill_2x2, vigenere, playfair)',
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available hypotheses',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Max candidates to generate (default: 50)',
    )

    # Vigenère-specific args
    parser.add_argument(
        '--min-length',
        type=int,
        help='Min key length for Vigenère (default: 1)',
    )
    parser.add_argument(
        '--max-length',
        type=int,
        help='Max key length for Vigenère (default: 20)',
    )
    parser.add_argument(
        '--keys-per-length',
        type=int,
        help='Keys to test per length for Vigenère (default: 10)',
    )

    args = parser.parse_args()

    # List hypotheses
    if args.list:
        print("Available hypotheses:")
        print()
        for name, info in sorted(HYPOTHESES.items()):
            print(f"  {name:20s} - {info['description']}")
        print()
        return 0

    # Validate hypothesis
    if not args.hypothesis:
        parser.print_help()
        return 1

    if args.hypothesis not in HYPOTHESES:
        print(f"Error: Unknown hypothesis '{args.hypothesis}'")
        print(f"Available: {', '.join(sorted(HYPOTHESES.keys()))}")
        print("Use --list for descriptions")
        return 1

    # Get hypothesis config
    hyp_config = HYPOTHESES[args.hypothesis]
    hyp_class = hyp_config['class']
    hyp_params = hyp_config['params'].copy()

    # Override params from command line
    if args.hypothesis == 'vigenere':
        if args.min_length is not None:
            hyp_params['min_key_length'] = args.min_length
        if args.max_length is not None:
            hyp_params['max_key_length'] = args.max_length
        if args.keys_per_length is not None:
            hyp_params['keys_per_length'] = args.keys_per_length

    # Create hypothesis instance
    hypothesis = hyp_class(**hyp_params)

    # Run search
    try:
        run_hypothesis_search(
            hypothesis_name=args.hypothesis,
            hypothesis_instance=hypothesis,
            limit=args.limit,
        )
        return 0
    except Exception as e:
        print(f"Error running hypothesis: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
