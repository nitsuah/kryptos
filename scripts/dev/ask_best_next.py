import os
import sys
from pathlib import Path


def main() -> None:
    os.environ['PLAN'] = (
        "Please review the current repository status and recommend the single best next action:"
        " options: (1) push the 'cribs-sanborn' branch and open a PR, (2) finish OPS automation so the"
        " triumverate can run tuning end-to-end, or (3) implement SPY's conservative crib extractor."
        " Provide a 1-line recommendation and one sentence justification."
    )

    # ensure repo root is on sys.path
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))

    from scripts.dev.ask_triumverate import run_plan_check

    print('Asking triumverate for best next action...')
    run_plan_check(os.environ['PLAN'])
    print('Done')


if __name__ == '__main__':
    main()
