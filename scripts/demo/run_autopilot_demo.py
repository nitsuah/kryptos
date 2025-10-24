"""Autopilot dry-run demo.

Runs the triumverate planner in dry-run mode and prints the structured plan.
Artifacts are written under `artifacts/demo/run_<timestamp>_<rand>/` for review.
No network calls; purely local subprocess invocation.
"""

from __future__ import annotations

import json
import random
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "pyproject.toml").exists():  # fallback if layout changed
    ROOT = ROOT.parent

ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
rand = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
demo_dir = ROOT / "artifacts" / "demo" / f"run_{ts}_{rand}"
demo_dir.mkdir(parents=True, exist_ok=True)

cmd = [sys.executable, str(ROOT / "scripts" / "dev" / "ask_triumverate.py"), "--dry-run"]
print("[autopilot-demo] executing:", " ".join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print("[autopilot-demo] exit code:", proc.returncode)
(demo_dir / "stdout.txt").write_text(proc.stdout)
(demo_dir / "stderr.txt").write_text(proc.stderr)

plan = None
for line in proc.stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        maybe = json.loads(line)
        if isinstance(maybe, dict) and ("action" in maybe or "recommendation_text" in maybe):
            plan = maybe
            break
    except json.JSONDecodeError:
        continue

if plan is None:
    plan = {
        "recommendation_text": "No structured plan found (dry-run fallback)",
        "action": None,
        "persona": "AUTOPILOT",
        "status": "no-plan",
        "timestamp": ts,
    }
    print("[autopilot-demo] plan not found; using fallback JSON")

out_path = demo_dir / "plan.json"
out_path.write_text(json.dumps(plan, indent=2))
print("[autopilot-demo] saved plan to", out_path)
print(json.dumps(plan, indent=2))

if proc.returncode != 0:
    sys.exit(proc.returncode)
