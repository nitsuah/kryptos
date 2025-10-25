"""Autopilot dry-run demo (migrated).

Generates a simple recommendation plan using the autopilot module and
persists a plan.json under artifacts/demo/run_<ts>_<rand>/.
"""

from __future__ import annotations

import json
import logging
import random
import string
from datetime import datetime
from pathlib import Path

from kryptos.autopilot import recommend_next_action, run_exchange
from kryptos.log_setup import setup_logging
from kryptos.paths import get_artifacts_root


def run_autopilot_demo() -> Path:
    setup_logging(level=logging.INFO, logger_name="kryptos.autopilot_demo")
    log = logging.getLogger("kryptos.autopilot_demo")
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rand = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    demo_dir = get_artifacts_root() / "demo" / f"run_{ts}_{rand}"
    demo_dir.mkdir(parents=True, exist_ok=True)

    rec, just, plan = recommend_next_action()
    plan_record = {
        "recommendation": rec,
        "justification": just,
        "plan": plan,
        "timestamp": ts,
    }
    (demo_dir / "plan.json").write_text(json.dumps(plan_record, indent=2), encoding="utf-8")
    # produce an exchange log (jsonl) for realism
    try:
        run_exchange(plan_text=f"{rec}: {just}", autopilot=True)
    except (RuntimeError, ValueError, OSError) as exc:  # demo resilience
        log.warning("run_exchange failed (non-fatal for demo): %s", exc)
    log.info("Autopilot demo complete. Artifacts: %s", demo_dir)
    return demo_dir


def _main() -> None:  # pragma: no cover
    _ = run_autopilot_demo()


if __name__ == "__main__":  # pragma: no cover
    _main()
