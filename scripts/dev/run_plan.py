"""DEPRECATED wrapper: use `ask_triumverate.py` directly with PLAN env or new CLI.

Scheduled for removal after unifying autopilot tooling.
"""

import logging
import os
from pathlib import Path


def main() -> None:
    # set a safe plan and force OPS to run
    os.environ['PLAN'] = 'please run crib_weight_sweep; dry_run'
    os.environ['OPS_RUN'] = '1'

    # Prefer package import; fall back to inserting repo root on sys.path
    # Direct file path import (avoid deprecated package path fallbacks)
    repo = Path(__file__).resolve().parents[2]
    ask_path = repo / 'scripts' / 'dev' / 'ask_triumverate.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('ask_triumverate_mod', str(ask_path))
    if not (spec and spec.loader):
        raise RuntimeError(f'Could not load ask_triumverate at {ask_path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    run_plan_check = getattr(mod, 'run_plan_check', None)
    if run_plan_check is None:
        raise RuntimeError('run_plan_check not found in ask_triumverate module')

    logging.warning('[DEPRECATED] run_plan.py will be removed; use ask_triumverate or cli autopilot subcommand.')
    logging.info('Running plan check (runner)')
    run_plan_check(os.environ['PLAN'])
    logging.info('Runner finished')


if __name__ == '__main__':
    main()
