"""Autopilot demo stub.

Writes a minimal plan.json under artifacts/demo/run_<timestamp>/plan.json for test coverage.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


def main() -> int:
    ts = time.strftime('%Y%m%dT%H%M%S')
    root = Path(__file__).resolve().parents[3] / 'artifacts' / 'demo' / f'run_{ts}'
    root.mkdir(parents=True, exist_ok=True)
    plan = {
        'persona': 'demo',
        'action': 'plan',
        'recommendation_text': 'Explore adaptive transposition weights next.',
        'timestamp': ts,
    }
    with (root / 'plan.json').open('w', encoding='utf-8') as fh:
        json.dump(plan, fh, indent=2)
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
