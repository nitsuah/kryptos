#!/usr/bin/env python3
"""Run a single exchange with the SPY/Q/OPS personas and print a concise summary.

This script uses the canonical orchestrator harness in `scripts/dev/orchestrator.py`.
It accepts an optional short plan text (via PLAN environment variable) which will be
appended to the Q persona prompt so Q can comment on the current plan.
"""

import importlib.util
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


def load_orchestrator():
    # load the canonical orchestrator module by file path
    here = Path(__file__).resolve().parent
    orch_path = here / "orchestrator.py"
    spec = importlib.util.spec_from_file_location("orch_dev", str(orch_path))
    mod = importlib.util.module_from_spec(spec) if spec else None
    if spec and mod:
        spec.loader.exec_module(mod)  # type: ignore
        return mod
    raise RuntimeError(f"Failed to load orchestrator at {orch_path}")


def run_plan_check(
    plan_text: str | None = None,
    autopilot: bool = True,
    weights: list[float] | None = None,
    dry_run: bool = True,
):
    orch = load_orchestrator()
    personas = orch.load_personas()

    # If autopilot enabled and no explicit plan_text provided, ask triumverate for next action.
    if autopilot and not plan_text:
        rec, just, plan = orch.recommend_next_action()
        plan_text = f"Recommendation: {rec}. Reason: {just}"
        print(f"[AUTOPILOT] Triumverate recommends: {rec} -- {just}")

        # Execute a small set of safe, idempotent actions automatically when recommended.
        # Use the structured plan.action for deterministic dispatch.
        action = plan.get('action') if isinstance(plan, dict) else None

        # If triumverate asks to run OPS or analyze artifacts, run it.
        if action in ('run_ops', 'analyze_artifacts'):
            # Prefer the existing manager daemon's run_sweep if it's available to avoid
            # duplicating sweep logic and respect the canonical manager implementation.
            run_path = None
            try:
                from scripts.dev import manager_daemon as mgr  # type: ignore

                try:
                    print(f"[AUTOPILOT] Executing manager_daemon.run_sweep (dry_run={dry_run})...")
                    # manager.run_sweep expects a param mapping; use a small default grid
                    params = {'pruning_top_n': 15, 'candidate_cap': 40}
                    csv_path = mgr.run_sweep(params, dry_run=dry_run)
                    run_path = csv_path.parent
                    if run_path:
                        print(f"[AUTOPILOT] Manager wrote tuning artifacts to: {run_path}")
                except Exception:
                    run_path = None
            except Exception:
                # manager not available; fall back to orchestrator's OPS hook if present
                run_path = None

            if run_path is None and hasattr(orch, 'ops_run_tuning'):
                try:
                    print(f"[AUTOPILOT] Executing recommended OPS run (dry_run={dry_run})...")
                    run_path = orch.ops_run_tuning(weights=weights, dry_run=dry_run)
                    if run_path:
                        print(f"[AUTOPILOT] OPS wrote tuning artifacts to: {run_path}")
                        # After OPS completes, try to pick the best weight using the sweep analyzer
                        try:
                            import importlib.util

                            repo_root = Path(__file__).resolve().parents[2]
                            pick_path = repo_root / 'scripts' / 'tuning' / 'pick_best_weight.py'
                            best_w = None
                            if pick_path.exists():
                                spec = importlib.util.spec_from_file_location('pick_best', str(pick_path))
                                mod = importlib.util.module_from_spec(spec) if spec else None
                                if spec and mod:
                                    spec.loader.exec_module(mod)  # type: ignore
                                    try:
                                        best_w, _stats = mod.pick_best(Path(run_path))
                                        print(f"[AUTOPILOT] pick_best_weight selected weight={best_w}")
                                    except Exception:
                                        best_w = None
                            # compute SPY min_conf using spy_eval if available, else fallback
                            spy_min_conf = os.environ.get('SPY_MIN_CONF')
                            spy_eval_path = repo_root / 'scripts' / 'tuning' / 'spy_eval.py'
                            if not spy_min_conf and spy_eval_path.exists():
                                try:
                                    spec2 = importlib.util.spec_from_file_location('spy_eval', str(spy_eval_path))
                                    mod2 = importlib.util.module_from_spec(spec2) if spec2 else None
                                    if spec2 and mod2:
                                        spec2.loader.exec_module(mod2)  # type: ignore
                                        labels = Path(repo_root) / 'data' / 'spy_eval_labels.csv'
                                        runs = Path(repo_root) / 'artifacts' / 'tuning_runs'
                                        spy_min_conf = str(mod2.select_best_threshold(labels, runs))
                                        print(f"[AUTOPILOT] spy_eval suggested min_conf={spy_min_conf}")
                                except Exception:
                                    spy_min_conf = None
                            if not spy_min_conf:
                                spy_min_conf = '0.25'

                            # run SPY extractor if present and concrete
                            spy_path = repo_root / 'scripts' / 'dev' / 'spy_extractor.py'
                            if spy_path.exists():
                                import subprocess
                                import sys

                                try:
                                    subprocess.check_call(
                                        [sys.executable, str(spy_path), '--min-conf', str(spy_min_conf)],
                                    )
                                    print('[AUTOPILOT] SPY extractor completed')
                                except Exception as e:
                                    print(f"[AUTOPILOT] SPY extractor failed: {e}")
                        except Exception as e:
                            print(f"[AUTOPILOT] post-OPS analysis failed: {e}")
                except Exception as e:
                    print(f"[AUTOPILOT] OPS execution failed: {e}")

        # If triumverate recommends pushing a branch & opening a PR, attempt to use gh cli.
        if action == 'push_pr':
            try:
                import shutil
                import subprocess

                # try to create a PR with gh if available
                print('[AUTOPILOT] Attempting to create GitHub PR using gh CLI...')
                # run in repo root
                repo_root = Path(__file__).resolve().parents[2]
                # include latest decision JSON in PR body if available
                dec_dir = repo_root / 'artifacts' / 'decisions'
                body_file = None
                if dec_dir.exists():
                    decs = sorted(
                        [p for p in dec_dir.iterdir() if p.is_file()],
                        key=lambda p: p.stat().st_mtime,
                        reverse=True,
                    )
                    if decs:
                        latest_dec = decs[0]
                        # create a temporary body file that includes decision JSON
                        tf = tempfile.NamedTemporaryFile('w', delete=False, suffix='.md', prefix='pr_body_')
                        try:
                            tf.write('# Autopilot Decision\n\n')
                            tf.write('The following decision artifact was produced by the autopilot run:\n\n')
                            with latest_dec.open('r', encoding='utf-8') as fh:
                                tf.write('```json\n')
                                tf.write(fh.read())
                                tf.write('\n```\n')
                            tf.flush()
                            body_file = tf.name
                        finally:
                            tf.close()

                # if gh isn't on PATH, skip trying to run it and fall back to printing compare URL
                if shutil.which('gh') is None:
                    print('[AUTOPILOT] gh CLI not found; skipping gh PR creation and printing compare URL.')
                    br = subprocess.check_output(
                        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                        cwd=str(repo_root),
                        encoding='utf-8',
                    ).strip()
                    origin = subprocess.check_output(
                        ['git', 'remote', 'get-url', 'origin'],
                        cwd=str(repo_root),
                        encoding='utf-8',
                    ).strip()
                    if origin.endswith('.git'):
                        origin = origin[:-4]
                    if origin.startswith('git@'):
                        origin = origin.replace(':', '/').replace('git@', 'https://')
                    compare = f"{origin}/compare/main...{br}?expand=1"
                    print(f'[AUTOPILOT] PR compare URL: {compare}')
                    if body_file:
                        print('\n--- Decision preview ---')
                        print(open(body_file, encoding='utf-8').read())
                        print('--- End decision preview ---\n')
                else:
                    # use --body-file to include decision; fall back to --fill
                    cmd = ['gh', 'pr', 'create']
                    if body_file:
                        cmd += ['--body-file', body_file, '--fill']
                    else:
                        cmd += ['--fill', '--web']
                    res = subprocess.run(cmd, cwd=str(repo_root))
                    if res.returncode == 0:
                        print('[AUTOPILOT] gh CLI launched PR creation flow (or created PR).')
                    else:
                        print('[AUTOPILOT] gh CLI failed; printing compare URL instead.')
                        br = subprocess.check_output(
                            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                            cwd=str(repo_root),
                            encoding='utf-8',
                        ).strip()
                        origin = subprocess.check_output(
                            ['git', 'remote', 'get-url', 'origin'],
                            cwd=str(repo_root),
                            encoding='utf-8',
                        ).strip()
                        # normalise origin url to https://github.com/<owner>/<repo>.git
                        if origin.endswith('.git'):
                            origin = origin[:-4]
                        if origin.startswith('git@'):
                            origin = origin.replace(':', '/').replace('git@', 'https://')
                        compare = f"{origin}/compare/main...{br}?expand=1"
                        print(f'[AUTOPILOT] PR compare URL: {compare}')
                        if body_file:
                            print('\n--- Decision preview ---')
                            with open(body_file, encoding='utf-8') as f:
                                print(f.read())
                            print('--- End decision preview ---\n')
            except Exception as e:
                print(f"[AUTOPILOT] Failed to create PR automatically: {e}")

    # if plan provided, append a small plan note to Q prompt
    if plan_text and "Q" in personas:
        personas["Q"] = personas["Q"] + f"\n\n# PLAN_CHECK: {plan_text}\n"
        # simple parsing: if plan asks to run crib_weight_sweep, or OPS_RUN env var set, invoke OPS
        plan_lower = (plan_text or '').lower()
        wants_run = 'crib_weight_sweep' in plan_lower or ('run' in plan_lower and 'crib' in plan_lower)
        ops_run_env = os.environ.get('OPS_RUN', '')
        if wants_run or ops_run_env.lower() in ('1', 'true', 'yes'):
            # make OPS aware of the run request
            personas["OPS"] = personas.get("OPS", "") + f"\n\n# PLAN_CHECK: {plan_text}\n"
            # execute OPS tuning run (dry-run by default)
            try:
                print("Invoking OPS tuning run...")
                run_path = orch.ops_run_tuning()
                if run_path:
                    print(f"OPS wrote tuning artifacts to: {run_path}")
                    # After run, try to pick best weight and compute spy threshold, then run spy_extractor
                    try:
                        import importlib.util

                        repo_root = Path(__file__).resolve().parents[2]
                        pick_path = repo_root / 'scripts' / 'tuning' / 'pick_best_weight.py'
                        best_w = None
                        if pick_path.exists():
                            spec = importlib.util.spec_from_file_location('pick_best', str(pick_path))
                            mod = importlib.util.module_from_spec(spec) if spec else None
                            if spec and mod:
                                spec.loader.exec_module(mod)  # type: ignore
                                try:
                                    best_w, _stats = mod.pick_best(Path(run_path))
                                    print(f"[PLAN_CHECK] pick_best_weight selected weight={best_w}")
                                except Exception:
                                    best_w = None

                        spy_min_conf = os.environ.get('SPY_MIN_CONF')
                        spy_eval_path = repo_root / 'scripts' / 'tuning' / 'spy_eval.py'
                        if not spy_min_conf and spy_eval_path.exists():
                            try:
                                spec2 = importlib.util.spec_from_file_location('spy_eval', str(spy_eval_path))
                                mod2 = importlib.util.module_from_spec(spec2) if spec2 else None
                                if spec2 and mod2:
                                    spec2.loader.exec_module(mod2)  # type: ignore
                                    labels = Path(repo_root) / 'data' / 'spy_eval_labels.csv'
                                    runs = Path(repo_root) / 'artifacts' / 'tuning_runs'
                                    spy_min_conf = str(mod2.select_best_threshold(labels, runs))
                                    print(f"[PLAN_CHECK] spy_eval suggested min_conf={spy_min_conf}")
                            except Exception:
                                spy_min_conf = None
                        if not spy_min_conf:
                            spy_min_conf = '0.25'
                        spy_path = repo_root / 'scripts' / 'dev' / 'spy_extractor.py'

                        # decision logging helper
                        def _write_decision(decision: dict) -> None:
                            droot = repo_root / 'artifacts' / 'decisions'
                            droot.mkdir(parents=True, exist_ok=True)
                            ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                            fname = droot / f'decision_{ts}.json'
                            with fname.open('w', encoding='utf-8') as fh:
                                json.dump(decision, fh, indent=2)

                        # run SPY extractor and then evaluate precision; enforce safety gate
                        if spy_path.exists():
                            try:
                                import subprocess
                                import sys

                                print('[PLAN_CHECK] Invoking SPY extractor on run artifacts...')
                                subprocess.check_call([sys.executable, str(spy_path), '--min-conf', str(spy_min_conf)])
                                print('[PLAN_CHECK] SPY extractor completed')
                                # try to evaluate precision using spy_eval if available
                                prec = None
                                try:
                                    spy_eval_path = repo_root / 'scripts' / 'tuning' / 'spy_eval.py'
                                    if spy_eval_path.exists():
                                        spec3 = importlib.util.spec_from_file_location('spy_eval', str(spy_eval_path))
                                        mod3 = importlib.util.module_from_spec(spec3) if spec3 else None
                                        if spec3 and mod3:
                                            spec3.loader.exec_module(mod3)  # type: ignore
                                            labels = Path(repo_root) / 'data' / 'spy_eval_labels.csv'
                                            runs = Path(repo_root) / 'artifacts' / 'tuning_runs'
                                            ev = mod3.evaluate(labels, runs)
                                            # fetch precision at our chosen threshold
                                            th = float(spy_min_conf)
                                            if th in ev:
                                                prec = ev[th][0]
                                except Exception:
                                    prec = None

                                decision = {
                                    'time': datetime.utcnow().isoformat(),
                                    'run_dir': str(run_path),
                                    'best_weight': best_w,
                                    'spy_min_conf': float(spy_min_conf),
                                    'spy_precision': prec,
                                }
                                # Holdout validation: re-score a small set to ensure the chosen weight
                                # does not regress overall. Use scoring utilities from the sweep.
                                try:
                                    # lazy import scoring same as sweep
                                    try:
                                        from kryptos.src.k4 import scoring as hold_scoring
                                    except Exception:
                                        try:
                                            from src.k4 import scoring as hold_scoring
                                        except Exception:
                                            if str(Path(__file__).resolve().parents[2] / 'src') not in sys.path:
                                                sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
                                            from k4 import scoring as hold_scoring

                                    # allow a configurable holdout file at data/holdout.csv
                                    holdout_file = Path(repo_root) / 'data' / 'holdout.csv'
                                    HOLDOUT: list[str]
                                    if holdout_file.exists():
                                        HOLDOUT = []
                                        with holdout_file.open('r', encoding='utf-8') as hf:
                                            for r in hf:
                                                t = r.strip()
                                                if t:
                                                    HOLDOUT.append(t)
                                    else:
                                        HOLDOUT = [
                                            'IN THE QUIET AFTERNOON THE SHADOWS GREW LONG ON THE FLOOR',
                                            'THE SECRET MESSAGE WAS HIDDEN IN PLAIN SIGHT AMONG THE TEXT',
                                        ]
                                    hold_stats = []
                                    chosen_w = float(best_w) if best_w is not None else None
                                    for s in HOLDOUT:
                                        base = hold_scoring.combined_plaintext_score(s)
                                        if chosen_w is not None:
                                            withc = hold_scoring.combined_plaintext_score_with_external_cribs(
                                                s,
                                                external_cribs=[],
                                                crib_weight=chosen_w,
                                            )
                                        else:
                                            withc = base
                                        hold_stats.append(
                                            {'sample': s, 'base': base, 'with': withc, 'delta': withc - base},
                                        )
                                    # compute mean delta across holdout
                                    mean_delta = None
                                    try:
                                        vals = [h['delta'] for h in hold_stats if h.get('delta') is not None]
                                        mean_delta = float(sum(vals) / len(vals)) if vals else None
                                    except Exception:
                                        mean_delta = None
                                    decision['holdout'] = {'samples': hold_stats, 'mean_delta': mean_delta}
                                    # enforce regression threshold (default 0.0 => no regression allowed)
                                    max_reg = float(os.environ.get('AUTOPILOT_MAX_REGRESSION', '0.0'))
                                    holdout_pass = True
                                    if mean_delta is not None and mean_delta < -abs(max_reg):
                                        holdout_pass = False
                                    decision['holdout_pass'] = holdout_pass
                                except Exception:
                                    decision['holdout'] = None
                                _write_decision(decision)

                                # safety gate: require precision >= 0.9 to auto-apply (if we have a precision)
                                SAFE_PREC = float(os.environ.get('AUTOPILOT_SAFE_PREC', '0.9'))
                                if prec is not None and prec < SAFE_PREC:
                                    print('[PLAN_CHECK] Safety gate: precision below threshold; not auto-applying')
                                else:
                                    print('[PLAN_CHECK] Safety gate passed or no precision available')
                            except Exception as e:
                                print(f'[PLAN_CHECK] SPY extractor failed: {e}')
                    except Exception as e:
                        print(f'[PLAN_CHECK] post-OPS analysis failed: {e}')
                else:
                    print("OPS run completed but no run path was detected.")
            except Exception as e:
                print(f"OPS failed to run tuning: {e}")
    out = orch.run_exchange(personas, rounds=1)
    print(f"Wrote log: {out}")
    # read the last few entries
    try:
        with open(out, encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception as e:
        print(f"Failed to read log {out}: {e}")
        return
    print("\n--- Persona responses ---")
    for ln in lines:
        print(ln.strip())


def _parse_weights(s: str | None) -> list[float] | None:
    if not s:
        return None
    try:
        return [float(x.strip()) for x in s.split(',') if x.strip()]
    except Exception:
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Autopilot triumverate runner')
    parser.add_argument('--plan', type=str, default=None, help='Plan text to append to Q prompt')
    parser.add_argument('--weights', type=str, default=None, help='Comma-separated weights to pass to OPS')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='Run OPS in dry-run mode')
    parser.add_argument('--no-autopilot', dest='autopilot', action='store_false', help="Don't auto-query triumverate")
    args = parser.parse_args()

    weights = _parse_weights(args.weights)
    run_plan_check(args.plan, autopilot=args.autopilot, weights=weights, dry_run=args.dry_run)
