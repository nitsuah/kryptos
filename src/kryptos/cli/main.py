from __future__ import annotations

import argparse
import json
from pathlib import Path

from kryptos.k4 import decrypt_best
from kryptos.k4 import scoring as k4_scoring
from kryptos.k4.attempt_logging import persist_attempt_logs
from kryptos.k4.report import write_condensed_report, write_top_candidates_markdown
from kryptos.k4.tuning import (
    pick_best_weight_from_rows,
    run_crib_weight_sweep,
    tiny_param_sweep,
)
from kryptos.k4.tuning.artifacts import end_to_end_process
from kryptos.k4.tuning.crib_sweep import WeightSweepRow
from kryptos.sections import SECTIONS
from kryptos.spy import extract as spy_module_extract
from kryptos.tuning import spy_eval


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

    # Tuning: crib weight sweep
    sp_tuning_sweep = sub.add_parser('tuning-crib-weight-sweep', help='Run crib weight sweep over provided weights')
    sp_tuning_sweep.add_argument('--weights', type=str, default='0.5,1.0,1.5', help='Comma-separated weights')
    sp_tuning_sweep.add_argument('--cribs', type=str, default='', help='Comma-separated crib tokens')
    sp_tuning_sweep.add_argument(
        '--samples',
        type=str,
        default='',
        help='Optional path to newline-delimited samples file',
    )
    sp_tuning_sweep.add_argument('--json', action='store_true', help='Emit JSON rows to stdout')
    sp_tuning_sweep.set_defaults(func=cmd_tuning_crib_weight_sweep)

    # Tuning: pick best weight from a sweep CSV (stdin unsupported; pass path)
    sp_tuning_pick = sub.add_parser('tuning-pick-best', help='Pick best weight from a sweep CSV file')
    sp_tuning_pick.add_argument('--csv', type=Path, required=True, help='Path to crib_weight_sweep.csv')
    sp_tuning_pick.set_defaults(func=cmd_tuning_pick_best)

    # Tuning: summarize run (end-to-end process)
    sp_tuning_summary = sub.add_parser(
        'tuning-summarize-run',
        help='Clean, summarize, and count crib hits for a run dir',
    )
    sp_tuning_summary.add_argument('--run-dir', type=Path, required=True, help='Path to tuning run directory')
    sp_tuning_summary.add_argument(
        '--no-write',
        action='store_true',
        help='Do not write summary artifacts, just print JSON',
    )
    sp_tuning_summary.set_defaults(func=cmd_tuning_summarize_run)

    # Tuning: tiny param sweep demo
    sp_tuning_tiny = sub.add_parser('tuning-tiny-param-sweep', help='Run tiny deterministic param sweep')
    sp_tuning_tiny.set_defaults(func=cmd_tuning_tiny_param_sweep)

    # Tuning: holdout score (replacement for scripts/tools/holdout_score.py)
    sp_tuning_holdout = sub.add_parser('tuning-holdout-score', help='Compute holdout scoring deltas for a crib weight')
    sp_tuning_holdout.add_argument('--weight', type=float, required=True, help='Crib weight to score')
    sp_tuning_holdout.add_argument(
        '--out',
        type=Path,
        default=Path('artifacts/reports/holdout.csv'),
        help='Output CSV path',
    )
    sp_tuning_holdout.add_argument(
        '--no-write',
        action='store_true',
        help='Do not write CSV, just print JSON summary',
    )
    sp_tuning_holdout.set_defaults(func=cmd_tuning_holdout_score)

    # SPY evaluation
    sp_spy_eval = sub.add_parser('spy-eval', help='Evaluate SPY thresholds and print metrics')
    sp_spy_eval.add_argument('--labels', type=Path, default=Path('data/spy_eval_labels.csv'), help='Labels CSV path')
    sp_spy_eval.add_argument('--runs', type=Path, default=Path('artifacts/tuning_runs'), help='Root runs directory')
    sp_spy_eval.add_argument('--thresholds', type=str, default='0.0,0.25,0.5,0.75', help='Comma-separated thresholds')
    sp_spy_eval.set_defaults(func=cmd_spy_eval)

    sp_spy_extract = sub.add_parser('spy-extract', help='Extract SPY tokens from runs at min confidence')
    sp_spy_extract.add_argument('--runs', type=Path, default=Path('artifacts/tuning_runs'), help='Root runs directory')
    sp_spy_extract.add_argument('--min-conf', type=float, default=0.25, help='Minimum confidence threshold')
    sp_spy_extract.set_defaults(func=cmd_spy_extract)

    sp_tuning_report = sub.add_parser(
        'tuning-report',
        help='Generate condensed CSV and top candidates markdown for a run',
    )
    sp_tuning_report.add_argument('--run-dir', type=Path, required=True, help='Path to tuning run directory')
    sp_tuning_report.add_argument('--top-n', dest='top_n', type=int, default=10, help='Top candidates markdown limit')
    sp_tuning_report.add_argument('--no-markdown', action='store_true', help='Skip markdown generation')
    sp_tuning_report.set_defaults(func=cmd_tuning_report)
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin wrapper
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


# -------------------- Command Implementations --------------------


def _load_samples(path: Path) -> list[str]:
    if not path or not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def cmd_tuning_crib_weight_sweep(args: argparse.Namespace) -> int:
    weights = [float(w) for w in args.weights.split(',') if w.strip()]
    cribs = [c.strip().upper() for c in args.cribs.split(',') if c.strip()]
    samples = _load_samples(Path(args.samples)) if args.samples else None
    rows = run_crib_weight_sweep(samples=samples, cribs=cribs, weights=weights)
    if args.json:
        print(json.dumps([r.__dict__ for r in rows], indent=2))
    else:
        for r in rows:
            print(f"weight={r.weight} delta={r.delta:+.3f} sample='{r.sample[:60]}'")
    return 0


def cmd_tuning_pick_best(args: argparse.Namespace) -> int:
    if not args.csv.exists():
        print(json.dumps({'error': 'csv_not_found', 'path': str(args.csv)}))
        return 2
    # parse CSV into WeightSweepRow list
    import csv

    rows: list[WeightSweepRow] = []
    with args.csv.open('r', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for row in reader:
            if len(row) < 5:
                continue
            try:
                w = float(row[0])
                baseline = float(row[2])
                with_cribs = float(row[3])
                delta = float(row[4])
            except ValueError:
                continue
            rows.append(
                WeightSweepRow(
                    weight=w,
                    sample=row[1],
                    baseline=baseline,
                    with_cribs=with_cribs,
                    delta=delta,
                ),
            )
    best = pick_best_weight_from_rows(rows)
    print(json.dumps({'best_weight': best}))
    return 0


def cmd_tuning_summarize_run(args: argparse.Namespace) -> int:
    if not args.run_dir.exists() or not args.run_dir.is_dir():
        print(json.dumps({'error': 'run_dir_not_found', 'path': str(args.run_dir)}))
        return 2
    res = end_to_end_process(args.run_dir, write=not args.no_write)
    print(json.dumps(res, indent=2))
    return 0


def cmd_tuning_tiny_param_sweep(_args: argparse.Namespace) -> int:
    rows = tiny_param_sweep()
    print(json.dumps(rows, indent=2))
    return 0


def cmd_tuning_holdout_score(args: argparse.Namespace) -> int:
    # Minimal representative holdout samples (formerly in holdout_score.py)
    holdout_samples = [
        'IN THE QUIET AFTERNOON THE SHADOWS GREW LONG ON THE FLOOR',
        'THE SECRET MESSAGE WAS HIDDEN IN PLAIN SIGHT AMONG THE TEXT',
    ]
    chosen_w = float(args.weight)
    rows = []
    for s in holdout_samples:
        base = k4_scoring.combined_plaintext_score(s)
        withc = k4_scoring.combined_plaintext_score_with_external_cribs(s, external_cribs=[], crib_weight=chosen_w)
        rows.append({'sample': s, 'base': base, 'with': withc, 'delta': withc - base})

    mean_delta = sum(r['delta'] for r in rows) / len(rows) if rows else None
    out = {'weight': chosen_w, 'mean_delta': mean_delta, 'rows': rows}
    if args.no_write:
        print(json.dumps(out, indent=2))
        return 0
    # write CSV
    args.out.parent.mkdir(parents=True, exist_ok=True)
    import csv

    with args.out.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['sample', 'base', 'with', 'delta'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(json.dumps(out, indent=2))
    print(str(args.out))
    return 0


def cmd_spy_eval(args: argparse.Namespace) -> int:
    thresholds = [float(t) for t in args.thresholds.split(',') if t.strip()]
    eval_res = spy_eval.evaluate(args.labels, args.runs, thresholds=thresholds)
    best = spy_eval.select_best_threshold(args.labels, args.runs, thresholds)
    out = {
        'thresholds': {f"{th:.2f}": {'precision': p, 'recall': r, 'f1': f1} for th, (p, r, f1) in eval_res.items()},
        'best_threshold': best,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_spy_extract(args: argparse.Namespace) -> int:
    # Use new spy module extraction (latest run only) or iterate runs
    tokens_by_run = {}
    for run_dir in args.runs.iterdir():
        if run_dir.is_dir() and run_dir.name.startswith('run_'):
            matches = spy_module_extract(min_conf=args.min_conf, run_dir=run_dir)
            if matches:
                tokens_by_run[run_dir.name] = sorted({t for m in matches for t in m.tokens})
    print(json.dumps({'min_conf': args.min_conf, 'extracted': tokens_by_run}, indent=2))
    return 0


def cmd_tuning_report(args: argparse.Namespace) -> int:
    if not args.run_dir.exists() or not args.run_dir.is_dir():
        print(json.dumps({'error': 'run_dir_not_found', 'path': str(args.run_dir)}))
        return 2
    condensed_path = write_condensed_report(args.run_dir)
    md_path = None
    if not args.no_markdown:
        md_path = write_top_candidates_markdown(args.run_dir, top_n=args.top_n)
    out = {'condensed_csv': str(condensed_path), 'markdown': str(md_path) if md_path else None}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
