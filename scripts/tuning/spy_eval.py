"""Legacy spy_eval script shim.

Exports select_best_threshold and evaluate for backward compatibility tests.
"""

from __future__ import annotations

from pathlib import Path

from kryptos.tuning import spy_eval as _impl

select_best_threshold = _impl.select_best_threshold
evaluate = _impl.evaluate


def _main() -> int:  # pragma: no cover
    import argparse
    import json

    p = argparse.ArgumentParser(description='Legacy spy_eval shim')
    p.add_argument('--labels', type=Path, required=True)
    p.add_argument('--runs', type=Path, required=True)
    p.add_argument('--thresholds', type=str, default='0.0,0.25,0.5,0.75')
    args = p.parse_args()
    thresholds = [float(t) for t in args.thresholds.split(',') if t.strip()]
    res = evaluate(args.labels, args.runs, thresholds=thresholds)
    best = select_best_threshold(args.labels, args.runs, thresholds)
    out = {
        'thresholds': {f'{th:.2f}': {'precision': p, 'recall': r, 'f1': f1} for th, (p, r, f1) in res.items()},
        'best_threshold': best,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(_main())
