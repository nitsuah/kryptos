"""DEPRECATED wrapper: use `ask_triumverate.py` directly or forthcoming CLI subcommand.

Will be removed after logging migration completes (tracked in TECHDEBT.md).
"""

import logging
import os
from pathlib import Path


def main() -> None:
    """Ask the triumverate for the best next action."""
    os.environ['PLAN'] = (
        "Please review the current repository status and recommend the single best next action:"
        " options: (1) push the 'cribs-sanborn' branch and open a PR, (2) finish OPS automation so the"
        " triumverate can run tuning end-to-end, or (3) implement SPY's conservative crib extractor."
        " Provide a 1-line recommendation and one sentence justification."
    )

    # Prefer package import; fall back to inserting repo root on sys.path
    # Always load ask_triumverate by file path to avoid fragile package imports.
    repo = Path(__file__).resolve().parents[2]
    ask_path = repo / 'scripts' / 'dev' / 'ask_triumverate.py'
    import importlib.util

    spec = importlib.util.spec_from_file_location('ask_triumverate_mod', str(ask_path))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        run_plan_check = getattr(mod, 'run_plan_check', None)
    else:
        raise RuntimeError(f'Failed to load ask_triumverate at {ask_path}')
    if run_plan_check is None:
        raise RuntimeError('run_plan_check not found in ask_triumverate module')

    logging.warning('[DEPRECATED] ask_best_next.py will be removed; call ask_triumverate.run_plan_check directly.')
    logging.info('Asking triumverate for best next action...')
    run_plan_check(os.environ['PLAN'])
    logging.info('Done')


if __name__ == '__main__':
    main()
