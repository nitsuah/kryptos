from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from kryptos import autopilot as autopilot_mod
from kryptos.examples import purge_demo_artifacts, run_composite_demo, run_sections_demo, run_tiny_weight_sweep
from kryptos.k4 import decrypt_best
from kryptos.k4 import scoring as k4_scoring
from kryptos.k4.attempt_logging import persist_attempt_logs
from kryptos.k4.report import write_condensed_report, write_top_candidates_markdown
from kryptos.k4.tuning import pick_best_weight_from_rows, run_crib_weight_sweep, tiny_param_sweep
from kryptos.k4.tuning.artifacts import end_to_end_process
from kryptos.k4.tuning.crib_sweep import WeightSweepRow
from kryptos.log_setup import setup_logging
from kryptos.sections import SECTIONS
from kryptos.spy import extract as spy_module_extract
from kryptos.tuning import spy_eval


def _print_sections(logger: logging.Logger, emit_log: bool = True, emit_print: bool = True) -> None:
    for name in SECTIONS:
        if emit_log:
            logger.info("%s", name)
        if emit_print:
            print(name)


def cmd_sections(args: argparse.Namespace) -> int:
    logger = logging.getLogger("kryptos.cli")
    if not any(getattr(h, "_kryptos_handler", False) for h in logger.handlers):
        logger = setup_logging(logger_name="kryptos.cli")
    quiet = getattr(args, "quiet", False)
    _print_sections(logger, emit_log=not quiet, emit_print=not quiet)
    return 0


def _load_ciphertext(cipher_path: Path | None, section: str = "K4") -> str:
    if cipher_path is not None:
        with open(cipher_path, encoding="utf-8") as fh:
            return fh.read().strip()
    from kryptos.paths import get_repo_root

    config_path = get_repo_root() / "config" / "config.json"
    with open(config_path, encoding="utf-8") as fh:
        return json.load(fh)["ciphertexts"][section]


def cmd_k4_decrypt(args: argparse.Namespace) -> int:
    logger = setup_logging(logger_name="kryptos.cli")
    ciphertext = _load_ciphertext(args.cipher)
    # Enable alphabet auto-selection by default unless explicitly disabled
    try_all_alphabets = getattr(args, "try_all_alphabets", True)
    res = decrypt_best(
        ciphertext,
        limit=args.limit,
        adaptive=args.adaptive,
        report=args.report,
        try_all_alphabets=try_all_alphabets,
    )
    logger.info("k4-decrypt score=%.3f lineage=%s", res.score, res.lineage)
    print(
        json.dumps(
            {"plaintext": res.plaintext, "score": res.score, "lineage": res.lineage, "artifacts": res.artifacts},
            indent=2,
        ),
    )
    return 0


def cmd_k4_attempts(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    path = persist_attempt_logs(label=args.label.upper())
    print(path)
    return 0


def cmd_sections_decrypt(args: argparse.Namespace) -> int:
    from kryptos.sections import SECTIONS

    logger = setup_logging(logger_name="kryptos.cli")
    section = args.section.upper()
    if section not in SECTIONS:
        print(json.dumps({"error": "invalid_section", "section": section}))
        return 2
    ciphertext = _load_ciphertext(args.cipher, section)
    decrypt_fn = SECTIONS[section]
    try:
        explain = getattr(args, "explain", False)
        out = {"section": section}
        if section in ("K1", "K2"):
            if not args.key:
                print(json.dumps({"error": "missing_key", "section": section}))
                return 2
            plaintext = decrypt_fn(ciphertext, args.key)
            out["plaintext"] = plaintext
            if explain:
                from kryptos.ciphers import KEYED_ALPHABET

                out["explain"] = {
                    "keyed_alphabet": KEYED_ALPHABET,
                    "key": args.key,
                    "note": "K1/K2 use keyed Vigenère with this alphabet and provided key.",
                }
        elif section == "K3":
            plaintext = decrypt_fn(ciphertext)
            out["plaintext"] = plaintext
            if explain:
                out["explain"] = {
                    "matrix_1": {"cols": 24, "rows": 14},
                    "matrix_2": {"cols": 8, "rows": 42},
                    "note": "K3 uses double rotational transposition with these matrix dimensions.",
                }
        elif section == "K4":
            res = decrypt_fn(ciphertext)
            if hasattr(res, "plaintext"):
                out["plaintext"] = res.plaintext
                if explain:
                    meta = getattr(res, "metadata", None)
                    out["explain"] = meta if meta else {"note": "No explainability metadata available for K4."}
            else:
                out["plaintext"] = res
                if explain:
                    out["explain"] = {"note": "No explainability metadata available for K4."}
        else:
            print(json.dumps({"error": "unsupported_section", "section": section}))
            return 2
        if getattr(args, "json", False):
            print(json.dumps(out))
        else:
            print(json.dumps(out, indent=2))
        return 0
    except Exception as exc:
        logger.error("sections-decrypt failed: %s", exc)
        out = {"error": "decrypt_failed", "section": section, "detail": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(out))
        else:
            print(json.dumps(out, indent=2))
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kryptos CLI")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-essential output (for CI/scripts)")
    parser.add_argument("--log-level", type=str, default="INFO", help="Set log level (DEBUG, INFO, WARNING, ERROR)")
    sub = parser.add_subparsers(dest="command", required=True)

    # Other subcommands...
    sp_sections = sub.add_parser("sections", help="List available sections")
    sp_sections.set_defaults(func=cmd_sections)

    sp_k4_decrypt = sub.add_parser("k4-decrypt", help="Decrypt K4 ciphertext")
    sp_k4_decrypt.add_argument(
        "--cipher", type=Path, default=None, help="Path to ciphertext file; omit to use K4 from config/config.json"
    )
    sp_k4_decrypt.add_argument("--limit", type=int, default=100, help="Candidate limit")
    sp_k4_decrypt.add_argument("--adaptive", action="store_true", help="Enable adaptive mode")
    sp_k4_decrypt.add_argument("--report", action="store_true", help="Emit report")
    sp_k4_decrypt.add_argument(
        "--no-auto-alphabet",
        dest="try_all_alphabets",
        action="store_false",
        help="Disable alphabet auto-selection (default: enabled)",
    )
    sp_k4_decrypt.set_defaults(func=cmd_k4_decrypt)

    sp_sections_decrypt = sub.add_parser("sections-decrypt", help="Decrypt a section (K1, K2, K3, K4)")
    sp_sections_decrypt.add_argument(
        "--section", type=str, required=True, choices=["K1", "K2", "K3", "K4"], help="Section to decrypt"
    )
    sp_sections_decrypt.add_argument(
        "--cipher",
        type=Path,
        default=None,
        help="Path to ciphertext file; omit to use the section ciphertext from config/config.json",
    )
    sp_sections_decrypt.add_argument("--key", type=str, default=None, help="Key for K1/K2 (ignored for K3/K4)")
    sp_sections_decrypt.add_argument(
        "--json", action="store_true", help="Emit output as JSON (single line, no extra text)"
    )
    sp_sections_decrypt.add_argument(
        "--explain", action="store_true", help="Show explainability metadata for the decryption (if available)"
    )
    sp_sections_decrypt.set_defaults(func=cmd_sections_decrypt)

    sp_k4_attempts = sub.add_parser("k4-attempts", help="Persist current in-memory attempt logs")
    sp_k4_attempts.add_argument("--label", type=str, default="k4", help="Label for attempt log file prefix")
    sp_k4_attempts.set_defaults(func=cmd_k4_attempts)

    sp_tuning_sweep = sub.add_parser("tuning-crib-weight-sweep", help="Run crib weight sweep over provided weights")
    sp_tuning_sweep.add_argument("--weights", type=str, default="0.5,1.0,1.5", help="Comma-separated weights")
    sp_tuning_sweep.add_argument("--cribs", type=str, default="", help="Comma-separated crib tokens")
    sp_tuning_sweep.add_argument(
        "--samples", type=str, default="", help="Optional path to newline-delimited samples file"
    )
    sp_tuning_sweep.add_argument("--json", action="store_true", help="Emit JSON rows to stdout")
    sp_tuning_sweep.set_defaults(func=cmd_tuning_crib_weight_sweep)

    sp_tuning_pick = sub.add_parser("tuning-pick-best", help="Pick best weight from a sweep CSV file")
    sp_tuning_pick.add_argument("--csv", type=Path, required=True, help="Path to crib_weight_sweep.csv")
    sp_tuning_pick.set_defaults(func=cmd_tuning_pick_best)

    sp_tuning_summary = sub.add_parser(
        "tuning-summarize-run", help="Clean, summarize, and count crib hits for a run dir"
    )
    sp_tuning_summary.add_argument("--run-dir", type=Path, required=True, help="Path to tuning run directory")
    sp_tuning_summary.add_argument(
        "--no-write", action="store_true", help="Do not write summary artifacts, just print JSON"
    )
    sp_tuning_summary.set_defaults(func=cmd_tuning_summarize_run)

    sp_tuning_tiny = sub.add_parser("tuning-tiny-param-sweep", help="Run tiny deterministic param sweep")
    sp_tuning_tiny.set_defaults(func=cmd_tuning_tiny_param_sweep)

    sp_tuning_holdout = sub.add_parser("tuning-holdout-score", help="Compute holdout scoring deltas for a crib weight")
    sp_tuning_holdout.add_argument("--weight", type=float, required=True, help="Crib weight to score")
    sp_tuning_holdout.add_argument(
        "--out", type=Path, default=Path("artifacts/reports/holdout.csv"), help="Output CSV path"
    )
    sp_tuning_holdout.add_argument("--no-write", action="store_true", help="Do not write CSV, just print JSON summary")
    sp_tuning_holdout.set_defaults(func=cmd_tuning_holdout_score)

    sp_spy_eval = sub.add_parser("spy-eval", help="Evaluate SPY thresholds and print metrics")
    sp_spy_eval.add_argument("--labels", type=Path, default=Path("data/spy_eval_labels.csv"), help="Labels CSV path")
    sp_spy_eval.add_argument("--runs", type=Path, default=Path("artifacts/tuning_runs"), help="Root runs directory")
    sp_spy_eval.add_argument("--thresholds", type=str, default="0.0,0.25,0.5,0.75", help="Comma-separated thresholds")
    sp_spy_eval.set_defaults(func=cmd_spy_eval)

    sp_spy_extract = sub.add_parser("spy-extract", help="Extract SPY tokens from runs at min confidence")
    sp_spy_extract.add_argument("--runs", type=Path, default=Path("artifacts/tuning_runs"), help="Root runs directory")
    sp_spy_extract.add_argument("--min-conf", type=float, default=0.25, help="Minimum confidence threshold")
    sp_spy_extract.set_defaults(func=cmd_spy_extract)

    sp_tuning_report = sub.add_parser(
        "tuning-report", help="Generate condensed CSV and top candidates markdown for a run"
    )
    sp_tuning_report.add_argument("--run-dir", type=Path, required=True, help="Path to tuning run directory")
    sp_tuning_report.add_argument("--top-n", dest="top_n", type=int, default=10, help="Top candidates markdown limit")
    sp_tuning_report.add_argument("--no-markdown", action="store_true", help="Skip markdown generation")
    sp_tuning_report.set_defaults(func=cmd_tuning_report)

    sp_autopilot = sub.add_parser("autopilot", help="Run a single exchange or loop until safe decision")
    sp_autopilot.add_argument("--plan", type=str, default=None, help="Optional plan text appended to Q prompt")
    sp_autopilot.add_argument("--dry-run", action="store_true", help="Dry-run (no destructive actions)")
    sp_autopilot.add_argument("--loop", action="store_true", help="Loop until safe decision or iterations cap")
    sp_autopilot.add_argument("--iterations", type=int, default=0, help="Loop iteration cap (0=infinite)")
    sp_autopilot.add_argument("--interval", type=int, default=300, help="Seconds between loop iterations")
    sp_autopilot.add_argument("--force", action="store_true", help="Override dry-run inside loop")
    sp_autopilot.set_defaults(func=cmd_autopilot)

    sp_autonomous = sub.add_parser("autonomous", help="Run autonomous coordination loop (24/7 cryptanalysis)")
    sp_autonomous.add_argument("--max-hours", type=float, default=None, help="Maximum runtime in hours (None=infinite)")
    sp_autonomous.add_argument(
        "--max-cycles", type=int, default=None, help="Maximum coordination cycles (None=infinite)"
    )
    sp_autonomous.add_argument(
        "--cycle-interval", type=float, default=0.25, help="Minutes between cycles (default: 15 sec)"
    )
    sp_autonomous.add_argument(
        "--ops-cycle", type=float, default=0.5, help="Minutes between OPS strategic analyses (default: 30 sec)"
    )
    sp_autonomous.add_argument(
        "--web-intel-hours", type=float, default=0.5, help="Hours between web intelligence checks (default: 30 min)"
    )
    sp_autonomous.set_defaults(func=cmd_autonomous)

    sp_examples_smoke = sub.add_parser(
        "examples-smoke", help="Run fast example demos (sections, tiny sweep, composite) for CI smoke validation"
    )
    sp_examples_smoke.add_argument("--limit", type=int, default=5, help="Composite demo candidate limit")
    sp_examples_smoke.add_argument(
        "--keep", type=int, default=4, help="Max number of recent demo dirs to keep after run (purge older)"
    )
    sp_examples_smoke.set_defaults(func=cmd_examples_smoke)

    sp_keyspace_stats = sub.add_parser(
        "keyspace-stats",
        help="Show keyspace coverage heatmap and attack prioritisation recommendations",
    )
    sp_keyspace_stats.add_argument(
        "--cipher",
        type=str,
        default=None,
        help='Cipher type to report on (e.g. "vigenere"). Omit for all types.',
    )
    sp_keyspace_stats.add_argument(
        "--top-n",
        dest="top_n",
        type=int,
        default=5,
        help="Number of priority recommendations to display (default: 5)",
    )
    sp_keyspace_stats.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human-readable table",
    )
    sp_keyspace_stats.set_defaults(func=cmd_keyspace_stats)

    sp_serve = sub.add_parser("serve", help="Run the Kryptos FastAPI server (turbovec RAG search over artifacts/)")
    sp_serve.add_argument("--host", type=str, default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    sp_serve.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    sp_serve.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")
    sp_serve.set_defaults(func=cmd_serve)

    return parser

    p = argparse.ArgumentParser(prog="kryptos", description="Kryptos research CLI")
    p.add_argument("--log-level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    p.add_argument("--quiet", action="store_true", help="Suppress non-error logging (JSON output only)")
    sub = p.add_subparsers(dest="command", required=True)

    sp_sections = sub.add_parser("sections", help="List available sections (K1-K4)")
    sp_sections.set_defaults(func=cmd_sections)

    sp_k4 = sub.add_parser("k4-decrypt", help="Run composite K4 decrypt search")
    sp_k4.add_argument("--cipher", type=Path, required=True, help="Path to ciphertext file (raw)")
    sp_k4.add_argument("--limit", type=int, default=50, help="Candidate limit")
    sp_k4.add_argument("--adaptive", action="store_true", help="Enable adaptive fusion weighting")
    sp_k4.add_argument("--report", action="store_true", help="Write artifacts (candidates + attempts)")
    sp_k4.set_defaults(func=cmd_k4_decrypt)

    sp_attempts = sub.add_parser("k4-attempts", help="Persist current in-memory attempt logs")
    sp_attempts.add_argument("--label", type=str, default="k4", help="Label for attempt log file prefix")
    sp_attempts.set_defaults(func=cmd_k4_attempts)

    sp_tuning_sweep = sub.add_parser("tuning-crib-weight-sweep", help="Run crib weight sweep over provided weights")
    sp_tuning_sweep.add_argument("--weights", type=str, default="0.5,1.0,1.5", help="Comma-separated weights")
    sp_tuning_sweep.add_argument("--cribs", type=str, default="", help="Comma-separated crib tokens")
    sp_tuning_sweep.add_argument(
        "--samples",
        type=str,
        default="",
        help="Optional path to newline-delimited samples file",
    )
    sp_tuning_sweep.add_argument("--json", action="store_true", help="Emit JSON rows to stdout")
    sp_tuning_sweep.set_defaults(func=cmd_tuning_crib_weight_sweep)

    sp_tuning_pick = sub.add_parser("tuning-pick-best", help="Pick best weight from a sweep CSV file")
    sp_tuning_pick.add_argument("--csv", type=Path, required=True, help="Path to crib_weight_sweep.csv")
    sp_tuning_pick.set_defaults(func=cmd_tuning_pick_best)

    sp_tuning_summary = sub.add_parser(
        "tuning-summarize-run",
        help="Clean, summarize, and count crib hits for a run dir",
    )
    sp_tuning_summary.add_argument("--run-dir", type=Path, required=True, help="Path to tuning run directory")
    sp_tuning_summary.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write summary artifacts, just print JSON",
    )
    sp_tuning_summary.set_defaults(func=cmd_tuning_summarize_run)

    sp_tuning_tiny = sub.add_parser("tuning-tiny-param-sweep", help="Run tiny deterministic param sweep")
    sp_tuning_tiny.set_defaults(func=cmd_tuning_tiny_param_sweep)

    sp_tuning_holdout = sub.add_parser("tuning-holdout-score", help="Compute holdout scoring deltas for a crib weight")
    sp_tuning_holdout.add_argument("--weight", type=float, required=True, help="Crib weight to score")
    sp_tuning_holdout.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/reports/holdout.csv"),
        help="Output CSV path",
    )
    sp_tuning_holdout.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write CSV, just print JSON summary",
    )
    sp_tuning_holdout.set_defaults(func=cmd_tuning_holdout_score)

    sp_spy_eval = sub.add_parser("spy-eval", help="Evaluate SPY thresholds and print metrics")
    sp_spy_eval.add_argument("--labels", type=Path, default=Path("data/spy_eval_labels.csv"), help="Labels CSV path")
    sp_spy_eval.add_argument("--runs", type=Path, default=Path("artifacts/tuning_runs"), help="Root runs directory")
    sp_spy_eval.add_argument("--thresholds", type=str, default="0.0,0.25,0.5,0.75", help="Comma-separated thresholds")
    sp_spy_eval.set_defaults(func=cmd_spy_eval)

    sp_spy_extract = sub.add_parser("spy-extract", help="Extract SPY tokens from runs at min confidence")
    sp_spy_extract.add_argument("--runs", type=Path, default=Path("artifacts/tuning_runs"), help="Root runs directory")
    sp_spy_extract.add_argument("--min-conf", type=float, default=0.25, help="Minimum confidence threshold")
    sp_spy_extract.set_defaults(func=cmd_spy_extract)

    sp_tuning_report = sub.add_parser(
        "tuning-report",
        help="Generate condensed CSV and top candidates markdown for a run",
    )
    sp_tuning_report.add_argument("--run-dir", type=Path, required=True, help="Path to tuning run directory")
    sp_tuning_report.add_argument("--top-n", dest="top_n", type=int, default=10, help="Top candidates markdown limit")
    sp_tuning_report.add_argument("--no-markdown", action="store_true", help="Skip markdown generation")
    sp_tuning_report.set_defaults(func=cmd_tuning_report)

    sp_autopilot = sub.add_parser("autopilot", help="Run a single exchange or loop until safe decision")
    sp_autopilot.add_argument("--plan", type=str, default=None, help="Optional plan text appended to Q prompt")
    sp_autopilot.add_argument("--dry-run", action="store_true", help="Dry-run (no destructive actions)")
    sp_autopilot.add_argument("--loop", action="store_true", help="Loop until safe decision or iterations cap")
    sp_autopilot.add_argument("--iterations", type=int, default=0, help="Loop iteration cap (0=infinite)")
    sp_autopilot.add_argument("--interval", type=int, default=300, help="Seconds between loop iterations")
    sp_autopilot.add_argument("--force", action="store_true", help="Override dry-run inside loop")
    sp_autopilot.set_defaults(func=cmd_autopilot)

    sp_autonomous = sub.add_parser("autonomous", help="Run autonomous coordination loop (24/7 cryptanalysis)")
    sp_autonomous.add_argument("--max-hours", type=float, default=None, help="Maximum runtime in hours (None=infinite)")
    sp_autonomous.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Maximum coordination cycles (None=infinite)",
    )
    sp_autonomous.add_argument(
        "--cycle-interval",
        type=float,
        default=0.25,
        help="Minutes between cycles (default: 15 sec)",
    )
    sp_autonomous.add_argument(
        "--ops-cycle",
        type=float,
        default=0.5,
        help="Minutes between OPS strategic analyses (default: 30 sec)",
    )
    sp_autonomous.add_argument(
        "--web-intel-hours",
        type=float,
        default=0.5,
        help="Hours between web intelligence checks (default: 30 min)",
    )
    sp_autonomous.set_defaults(func=cmd_autonomous)

    sp_examples_smoke = sub.add_parser(
        "examples-smoke",
        help="Run fast example demos (sections, tiny sweep, composite) for CI smoke validation",
    )
    sp_examples_smoke.add_argument("--limit", type=int, default=5, help="Composite demo candidate limit")
    sp_examples_smoke.add_argument(
        "--keep",
        type=int,
        default=4,
        help="Max number of recent demo dirs to keep after run (purge older)",
    )
    sp_examples_smoke.set_defaults(func=cmd_examples_smoke)
    return p


def cmd_serve(args: argparse.Namespace) -> int:
    """Run the Kryptos FastAPI server (turbovec RAG search over artifacts/)."""
    import uvicorn

    uvicorn.run("kryptos.api.app:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def cmd_keyspace_stats(args: argparse.Namespace) -> int:
    """Print a keyspace coverage heatmap and attack prioritisation table."""
    import json as _json

    from kryptos.provenance.search_space import SearchSpaceTracker

    tracker = SearchSpaceTracker()
    report = tracker.get_coverage_report(args.cipher)
    recs = tracker.get_priority_recommendations(top_n=args.top_n)

    if args.json:
        print(_json.dumps({"coverage": report, "recommendations": recs}, indent=2, default=str))
        return 0

    # Human-readable output
    print("\n=== Keyspace Coverage ===")
    for ct, data in report.get("cipher_types", {}).items():
        print(
            f"\n{ct}  (overall {data['overall_coverage']:.1f}%  |  "
            f"{data['total_explored']:,}/{data['total_size']:,} explored)"
        )
        for r in data.get("regions", []):
            bar_fill = int(r["coverage_percent"] / 5)
            bar = "#" * bar_fill + "." * (20 - bar_fill)
            print(
                f"  {r['region']:20s} [{bar}] {r['coverage_percent']:5.1f}%  "
                f"({r['explored_count']:,}/{r['total_size']:,})"
            )

    if not report.get("cipher_types"):
        print("  (no regions registered yet — run a campaign to populate)")

    print("\n=== Priority Recommendations ===")
    if not recs:
        print("  (no data yet)")
    for i, rec in enumerate(recs, 1):
        print(
            f"  {i}. [{rec['cipher_type']} / {rec['region']}]  score={rec['adjusted_score']:.1f}  "
            f"coverage={rec['coverage']:.1f}%"
        )
        print(f"     {rec['reason']}  |  tried_keys={rec['tried_key_count']}")
    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Only set log level if present
    level = getattr(logging, getattr(args, "log_level", "INFO").upper(), logging.INFO)
    logger = setup_logging(logger_name="kryptos.cli")
    logger.setLevel(level)
    if hasattr(args, "quiet") and args.quiet:
        logger.setLevel(logging.ERROR)
    return args.func(args)


def _load_samples(path: Path) -> list[str]:
    if not path or not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cmd_tuning_crib_weight_sweep(args: argparse.Namespace) -> int:
    logger = setup_logging(logger_name="kryptos.cli")
    weights = [float(w) for w in args.weights.split(",") if w.strip()]
    cribs = [c.strip().upper() for c in args.cribs.split(",") if c.strip()]
    samples = _load_samples(Path(args.samples)) if args.samples else None
    rows = run_crib_weight_sweep(samples=samples, cribs=cribs, weights=weights)
    if args.json:
        print(json.dumps([r.__dict__ for r in rows], indent=2))
    else:
        for r in rows:
            logger.info("weight=%s delta=%+.3f sample='%s'", r.weight, r.delta, r.sample[:60])
    return 0


def cmd_tuning_pick_best(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    if not args.csv.exists():
        print(json.dumps({"error": "csv_not_found", "path": str(args.csv)}))
        return 2
    import csv

    rows: list[WeightSweepRow] = []
    with args.csv.open("r", encoding="utf-8") as fh:
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
    print(json.dumps({"best_weight": best}))
    return 0


def cmd_tuning_summarize_run(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    if not args.run_dir.exists() or not args.run_dir.is_dir():
        print(json.dumps({"error": "run_dir_not_found", "path": str(args.run_dir)}))
        return 2
    res = end_to_end_process(args.run_dir, write=not args.no_write)
    print(json.dumps(res, indent=2))
    return 0


def cmd_tuning_tiny_param_sweep(_args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    rows = tiny_param_sweep()
    print(json.dumps(rows, indent=2))
    return 0


def cmd_tuning_holdout_score(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    holdout_samples = [
        "IN THE QUIET AFTERNOON THE SHADOWS GREW LONG ON THE FLOOR",
        "THE SECRET MESSAGE WAS HIDDEN IN PLAIN SIGHT AMONG THE TEXT",
    ]
    chosen_w = float(args.weight)
    rows = []
    for s in holdout_samples:
        base = k4_scoring.combined_plaintext_score(s)
        withc = k4_scoring.combined_plaintext_score_with_external_cribs(s, external_cribs=[], crib_weight=chosen_w)
        rows.append({"sample": s, "base": base, "with": withc, "delta": withc - base})

    mean_delta = sum(r["delta"] for r in rows) / len(rows) if rows else None
    out = {"weight": chosen_w, "mean_delta": mean_delta, "rows": rows}
    if args.no_write:
        print(json.dumps(out, indent=2))
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    import csv

    with args.out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["sample", "base", "with", "delta"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(json.dumps(out, indent=2))
    if not getattr(args, "quiet", False):
        print(str(args.out))
    return 0


def cmd_spy_eval(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    thresholds = [float(t) for t in args.thresholds.split(",") if t.strip()]
    eval_res = spy_eval.evaluate(args.labels, args.runs, thresholds=thresholds)
    best = spy_eval.select_best_threshold(args.labels, args.runs, thresholds)
    out = {
        "thresholds": {f"{th:.2f}": {"precision": p, "recall": r, "f1": f1} for th, (p, r, f1) in eval_res.items()},
        "best_threshold": best,
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_spy_extract(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    tokens_by_run = {}
    for run_dir in args.runs.iterdir():
        if run_dir.is_dir() and run_dir.name.startswith("run_"):
            matches = spy_module_extract(min_conf=args.min_conf, run_dir=run_dir)
            if matches:
                tokens_by_run[run_dir.name] = sorted({t for m in matches for t in m.tokens})
    print(json.dumps({"min_conf": args.min_conf, "extracted": tokens_by_run}, indent=2))
    return 0


def cmd_tuning_report(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    if not args.run_dir.exists() or not args.run_dir.is_dir():
        print(json.dumps({"error": "run_dir_not_found", "path": str(args.run_dir)}))
        return 2
    condensed_path = write_condensed_report(args.run_dir)
    md_path = None
    if not args.no_markdown:
        md_path = write_top_candidates_markdown(args.run_dir, top_n=args.top_n)
    out = {"condensed_csv": str(condensed_path), "markdown": str(md_path) if md_path else None}
    print(json.dumps(out, indent=2))
    return 0


def cmd_autopilot(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    if args.loop:
        code = autopilot_mod.run_autopilot_loop(
            iterations=args.iterations,
            interval=args.interval,
            plan=args.plan,
        )
        print(json.dumps({"mode": "loop", "exit_code": code}))
        return code
    path = autopilot_mod.run_exchange(plan_text=args.plan, autopilot=True)
    print(json.dumps({"mode": "single", "log_path": str(path)}))
    return 0


def cmd_autonomous(args: argparse.Namespace) -> int:
    from kryptos.autonomous_coordinator import AutonomousCoordinator

    logger = setup_logging(logger_name="kryptos.cli")
    logger.info("🚀 Starting autonomous coordination system")

    coordinator = AutonomousCoordinator(
        ops_cycle_minutes=args.ops_cycle,
        web_intel_check_hours=args.web_intel_hours,
    )

    try:
        coordinator.run_autonomous_loop(
            max_hours=args.max_hours,
            max_cycles=args.max_cycles,
            cycle_interval_minutes=args.cycle_interval,
        )
        return 0
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
        return 130
    except Exception as exc:
        logger.exception("❌ Autonomous coordination failed: %s", exc)
        return 1


def cmd_examples_smoke(args: argparse.Namespace) -> int:
    setup_logging(logger_name="kryptos.cli")
    try:
        sections = run_sections_demo()
        sweep_dir = run_tiny_weight_sweep()
        composite_dir = run_composite_demo(limit=args.limit)
        purge_res = purge_demo_artifacts(max_keep=args.keep)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": repr(exc)}))
        return 2
    out = {
        "status": "ok",
        "sections": [s["name"] for s in sections],
        "tiny_weight_sweep_dir": str(sweep_dir),
        "composite_dir": composite_dir,
        "purged": [p.name for p in purge_res.removed],
        "kept": [p.name for p in purge_res.kept],
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
