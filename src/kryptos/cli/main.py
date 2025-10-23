from __future__ import annotations

import argparse
import json
from pathlib import Path

from kryptos.k4 import decrypt_best
from kryptos.k4.attempt_logging import persist_attempt_logs
from kryptos.sections import SECTIONS


def _print_sections() -> None:
    for name in SECTIONS:
        print(name)


def cmd_sections(_args: argparse.Namespace) -> int:
    _print_sections()
    return 0


def cmd_k4_decrypt(args: argparse.Namespace) -> int:
    with open(args.cipher, encoding='utf-8') as fh:
        ciphertext = fh.read().strip()
    res = decrypt_best(ciphertext, limit=args.limit, adaptive=args.adaptive, report=args.report)
    print(
        json.dumps(
            {
                'plaintext': res.plaintext,
                'score': res.score,
                'lineage': res.lineage,
                'artifacts': res.artifacts,
            },
            indent=2,
        ),
    )
    return 0


def cmd_k4_attempts(args: argparse.Namespace) -> int:
    path = persist_attempt_logs(label=args.label.upper())
    print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='kryptos', description='Kryptos research CLI')
    sub = p.add_subparsers(dest='command', required=True)

    sp_sections = sub.add_parser('sections', help='List available sections (K1-K4)')
    sp_sections.set_defaults(func=cmd_sections)

    sp_k4 = sub.add_parser('k4-decrypt', help='Run composite K4 decrypt search')
    sp_k4.add_argument('--cipher', type=Path, required=True, help='Path to ciphertext file (raw)')
    sp_k4.add_argument('--limit', type=int, default=50, help='Candidate limit')
    sp_k4.add_argument('--adaptive', action='store_true', help='Enable adaptive fusion weighting')
    sp_k4.add_argument('--report', action='store_true', help='Write artifacts (candidates + attempts)')
    sp_k4.set_defaults(func=cmd_k4_decrypt)

    sp_attempts = sub.add_parser('k4-attempts', help='Persist current in-memory attempt logs')
    sp_attempts.add_argument('--label', type=str, default='k4', help='Label for attempt log file prefix')
    sp_attempts.set_defaults(func=cmd_k4_attempts)
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin wrapper
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
