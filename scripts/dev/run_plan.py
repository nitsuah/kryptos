import os
import sys
from pathlib import Path


def main() -> None:
    # set a safe plan and force OPS to run
    os.environ['PLAN'] = 'please run crib_weight_sweep; dry_run'
    os.environ['OPS_RUN'] = '1'

    # ensure repo root (project root) is on sys.path
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))

    # import and run the plan check after adjusting sys.path
    from scripts.dev.ask_triumverate import run_plan_check

    print('Running plan check (runner)')
    run_plan_check(os.environ['PLAN'])
    print('Runner finished')


if __name__ == '__main__':
    main()
