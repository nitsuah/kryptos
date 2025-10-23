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


def run_plan_check(plan_text: str | None = None):
    orch = load_orchestrator()
    personas = orch.load_personas()
    # if plan provided, append a small plan note to Q prompt
    if plan_text and "Q" in personas:
        personas["Q"] = personas["Q"] + f"\n\n# PLAN_CHECK: {plan_text}\n"
        # simple parsing: if plan asks to run crib_weight_sweep, or OPS_RUN env var set, invoke OPS
        plan_lower = (plan_text or '').lower()
        wants_run = 'crib_weight_sweep' in plan_lower
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
