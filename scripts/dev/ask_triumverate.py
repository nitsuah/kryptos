#!/usr/bin/env python3
"""Run a single exchange with the SPY/Q/OPS personas and print a concise summary.

This script uses the canonical orchestrator harness in `scripts/dev/orchestrator.py`.
It accepts an optional short plan text (via PLAN environment variable) which will be
appended to the Q persona prompt so Q can comment on the current plan.
"""

import importlib.util
import os
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
        rec, just = orch.recommend_next_action()
        plan_text = f"Recommendation: {rec}. Reason: {just}"
        print(f"[AUTOPILOT] Triumverate recommends: {rec} -- {just}")

        # Execute a small set of safe, idempotent actions automatically when recommended.
        rec_lower = rec.lower()
        # If triumverate wants an OPS run and ops_run_tuning is available, run it.
        if 'ops' in rec_lower or 'run' in rec_lower and 'crib' in rec_lower:
            if hasattr(orch, 'ops_run_tuning'):
                try:
                    print(f"[AUTOPILOT] Executing recommended OPS run (dry_run={dry_run})...")
                    run_path = orch.ops_run_tuning(weights=weights, dry_run=dry_run)
                    if run_path:
                        print(f"[AUTOPILOT] OPS wrote tuning artifacts to: {run_path}")
                        # run SPY extractor automatically if present
                        spy_path = Path(__file__).resolve().parents[2] / 'scripts' / 'dev' / 'spy_extractor.py'
                        if spy_path.exists():
                            import subprocess
                            import sys

                            try:
                                subprocess.check_call([sys.executable, str(spy_path)])
                                print('[AUTOPILOT] SPY extractor completed')
                            except Exception as e:
                                print(f"[AUTOPILOT] SPY extractor failed: {e}")
                except Exception as e:
                    print(f"[AUTOPILOT] OPS execution failed: {e}")

        # If triumverate recommends pushing a branch & opening a PR, attempt to use gh cli.
        if 'push' in rec_lower and 'pr' in rec_lower or 'open pr' in rec_lower:
            try:
                import subprocess

                # try to create a PR with gh if available
                print('[AUTOPILOT] Attempting to create GitHub PR using gh CLI...')
                # run in repo root
                repo_root = Path(__file__).resolve().parents[2]
                # use --fill to pre-populate title/body from last commit
                res = subprocess.run(['gh', 'pr', 'create', '--fill', '--web'], cwd=str(repo_root))
                if res.returncode == 0:
                    print('[AUTOPILOT] gh CLI launched PR creation flow (or created PR).')
                else:
                    print('[AUTOPILOT] gh CLI not available or failed; printing compare URL instead.')
                    # fallback: print compare URL using current branch name
                    # get current branch
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
            except Exception as e:
                print(f"[AUTOPILOT] Failed to create PR automatically: {e}")

    # if plan provided, append a small plan note to Q prompt
    if plan_text and "Q" in personas:
        personas["Q"] = personas["Q"] + f"\n\n# PLAN_CHECK: {plan_text}\n"
        # simple parsing: if plan asks to run crib_weight_sweep, or OPS_RUN env var set, invoke OPS
        plan_lower = (plan_text or '').lower()
        wants_run = 'crib_weight_sweep' in plan_lower or 'run' in plan_lower and 'crib' in plan_lower
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
                    # automatically run SPY extractor if present
                    spy_path = Path(__file__).resolve().parents[2] / 'scripts' / 'dev' / 'spy_extractor.py'
                    if spy_path.exists():
                        try:
                            import subprocess
                            import sys

                            print('Invoking SPY extractor on run artifacts...')
                            subprocess.check_call([sys.executable, str(spy_path)])
                            print('SPY extractor completed')
                        except Exception as e:
                            print(f'SPY extractor failed: {e}')
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


if __name__ == "__main__":
    plan = os.environ.get("PLAN", None)
    run_plan_check(plan)
