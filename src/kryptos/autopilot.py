"""Unified autopilot orchestration utilities.

This module consolidates the scattered logic from the legacy dev scripts:
  - scripts/dev/ask_triumverate.py (single exchange + recommendation)
  - scripts/dev/autopilot_daemon.py (loop + safety gate)
  - scripts/dev/manager_daemon.py (parameter sweep shim)
  - scripts/dev/cracker_daemon.py (decision writing + acceptance threshold)

The goal is to provide a stable, importable API that the CLI can call while we
delete the legacy scripts. All heavy lifting (actual cryptanalysis, tuning,
SPY extraction) remains in dedicated package modules; this file only wires
them together and applies simple safety / decision heuristics.

Public entry points (initial minimal surface):
  run_exchange(plan_text: str | None, autopilot: bool, dry_run: bool) -> Path
  recommend_next_action() -> tuple[str, str, dict]
  run_autopilot_loop(
      iterations: int,
      interval: int,
      plan: str | None,
      dry_run: bool,
      force: bool
  ) -> int

The CLI subcommand will wrap these.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from pathlib import Path

from kryptos.log_setup import setup_logging
from kryptos.paths import (
    get_artifacts_root,
    get_decisions_dir,
    get_logs_dir,
    get_repo_root,
    get_tuning_runs_root,
)

# Centralized path references via kryptos.paths
REPO_ROOT = get_repo_root()
LOG_DIR = get_logs_dir()
DECISIONS_DIR = get_decisions_dir()
STATE_PATH = get_artifacts_root() / "state.json"


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _persona_prompts() -> dict[str, str]:
    """Load persona prompt stubs (dev friendly / test safe)."""
    agents_dir = REPO_ROOT / "agents"
    mapping: dict[str, str] = {}
    state = _load_state()
    for fname in ("spy.prompt", "q.prompt", "ops.prompt"):
        path = agents_dir / fname
        if path.exists():
            txt = path.read_text(encoding="utf-8")
            if fname.startswith("q") and state.get("learned"):
                notes = " ".join(f"{n['persona']}:{n['note']}" for n in state.get("learned", []))
                txt += f"\n\n# LEARNED_SUMMARY: {notes}\n"
            mapping[fname.split(".", maxsplit=1)[0].upper()] = txt
    # Conservative fallbacks for CI/tests
    mapping.setdefault("Q", "Q_PLACEHOLDER: Provide short recommendation or review.")
    mapping.setdefault("OPS", "OPS_PLACEHOLDER: Manage tuning runs; idle.")
    mapping.setdefault("SPY", "SPY_PLACEHOLDER: Extract conservative cribs; none found.")
    return mapping


def recommend_next_action() -> tuple[str, str, dict]:
    """Return recommendation, justification, structured plan dict.

    Minimal plan schema:
      {'action': 'run_ops'|'analyze_artifacts'|'push_pr'|'noop', 'params': {...}, 'metadata': {...}}
    """
    tr_dir = get_tuning_runs_root()
    has_artifacts = tr_dir.exists() and any(d.is_dir() for d in tr_dir.iterdir())
    # Detect presence of migrated spy extractor package instead of legacy script
    try:
        import kryptos.spy.extractor as _spy_mod  # noqa: F401

        has_spy = True
    except (ImportError, ModuleNotFoundError):
        has_spy = False
    # ops availability heuristic: presence of consolidated tuning script
    has_ops = (REPO_ROOT / "scripts" / "tuning.py").exists()
    metadata = {
        "has_artifacts": bool(has_artifacts),
        "has_spy": bool(has_spy),
        "has_ops": bool(has_ops),
        "tuning_runs_dir": str(tr_dir),
    }
    if not has_ops:
        rec = "finish OPS automation"
        just = "OPS not available programmatically yet; enable end-to-end tuning."
        plan = {"action": "noop", "params": {}, "metadata": metadata}
        return rec, just, plan
    if has_artifacts and not has_spy:
        rec = "implement SPY extractor"
        just = "Artifacts exist but no SPY extraction to summarize conservative cribs."
        plan = {"action": "analyze_artifacts", "params": {"run_dir": str(tr_dir)}, "metadata": metadata}
        return rec, just, plan
    rec = "push branch & open PR"
    just = "Code + artifacts present; opening PR captures current progress for review."
    plan = {"action": "push_pr", "params": {}, "metadata": metadata}
    return rec, just, plan


def _simulate_action(name: str, prompt: str) -> str:
    # Deterministic placeholder simulation keeping prior semantics.
    if name == "SPY":
        if "PLAN_CHECK:" in prompt:
            plan = prompt.split("PLAN_CHECK:", 1)[1].strip()
            return (
                f"SPY_SUMMARY:\tReviewed plan -> {plan}. "
                "Extracted 0 conservative crib candidates. LEARN: no_cribs_found"
            )
        return "SPY_SUMMARY:\tExtracted 0 conservative crib candidates. LEARN: no_cribs_found"
    if name == "Q":
        if "PLAN_CHECK:" in prompt:
            rec, just, _plan = recommend_next_action()
            plan = prompt.split("PLAN_CHECK:", 1)[1].strip()
            return f"Q_SUMMARY:\tPlan reviewed -> {plan}. " f"Recommendation -> {rec}. {just} LEARN: tooling_ready"
        return "Q_SUMMARY:\tPrepared tooling scaffold (placeholder). LEARN: tooling_ready"
    if name == "OPS":
        if "PLAN_CHECK:" in prompt and "crib_weight_sweep" in prompt:
            return "OPS_SUMMARY:\tReceived run request for crib_weight_sweep (placeholder)."
        return "OPS_SUMMARY:\tNo runs executed yet (placeholder)."
    return "UNKNOWN_PERSONA"


def _update_cribs_from_spy(run_id: str) -> dict[str, int]:
    """Extract SPY observations and promote cribs.

    Args:
        run_id: Identifier for this run (e.g., timestamp).

    Returns:
        Dictionary mapping promoted token -> count of distinct runs.
    """
    from kryptos.spy.crib_store import load_promoted_cribs, promote_cribs

    # Mock/stub: in real implementation, would scan tuning run artifacts
    # For now, return empty observations to establish the hook
    observations = []
    # Future: scan latest tuning run for high-confidence tokens
    # observations = extract_from_tuning_run(get_tuning_runs_root() / run_id)
    promoted_before = load_promoted_cribs()
    promoted_after = promote_cribs(observations)
    new_count = len(promoted_after) - len(promoted_before)
    return {"cribs_total": len(promoted_after), "new": max(0, new_count)}


def run_exchange(plan_text: str | None = None, autopilot: bool = True) -> Path:
    """Run a single multi-persona exchange.

    Writes a jsonl log file under artifacts/logs and returns the path.
    """
    personas = _persona_prompts()
    if autopilot and not plan_text:
        rec, just, plan = recommend_next_action()
        plan_text = f"Recommendation: {rec}. Reason: {just}"
        # Structured one-line JSON plan for downstream tools
        structured = {
            "action": plan.get("action"),
            "recommendation": rec,
            "justification": just,
            "timestamp": datetime.utcnow().isoformat(),
        }
        print(json.dumps(structured))
    if plan_text and "Q" in personas:
        personas["Q"] += f"\n\n# PLAN_CHECK: {plan_text}\n"
        personas["OPS"] += f"\n\n# PLAN_CHECK: {plan_text}\n"
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = LOG_DIR / f"run_{ts}.jsonl"
    state = _load_state()
    with out_path.open("w", encoding="utf-8") as fh:
        for r in range(1, 2):  # single round for now
            for name, prompt in personas.items():
                act = _simulate_action(name, prompt)
                entry = {"round": r, "persona": name, "action": act, "time": datetime.utcnow().isoformat()}
                fh.write(json.dumps(entry) + "\n")
                print(entry)
                if "LEARN:" in act:
                    learn_text = act.split("LEARN:", 1)[1].strip()
                    state.setdefault("learned", []).append(
                        {"persona": name, "note": learn_text, "time": datetime.utcnow().isoformat()},
                    )
    # Update cribs from SPY extractions
    try:
        crib_update = _update_cribs_from_spy(run_id=ts)
        crib_log = json.dumps({"event": "cribs_updated", **crib_update, "timestamp": ts})
        print(crib_log)
        with out_path.open("a", encoding="utf-8") as fh:
            fh.write(crib_log + "\n")
    except (OSError, ValueError) as exc:
        # Log but don't fail exchange if crib update fails
        print(f"Warning: crib update failed: {exc}")
    _save_state(state)
    return out_path


def _latest_decision() -> Path | None:
    if not DECISIONS_DIR.exists():
        return None
    files = [p for p in DECISIONS_DIR.iterdir() if p.is_file()]
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _decision_safe(decision: dict, safe_precision: float) -> bool:
    hold_ok = bool(decision.get("holdout_pass", True))
    prec = decision.get("spy_precision")
    if prec is not None:
        try:
            return hold_ok and float(prec) >= safe_precision
        except (TypeError, ValueError):
            return False
    return hold_ok


def run_autopilot_loop(
    iterations: int = 0,
    interval: int = 300,
    plan: str | None = None,
) -> int:
    """Run repeated exchanges until a safe decision is detected or iteration cap reached.

    Currently minimal: invokes run_exchange each loop; decision safety will depend on
    external tooling populating decision artifacts.
    """
    logger = setup_logging(logger_name="kryptos.autopilot")
    safe_prec = float(os.environ.get("AUTOPILOT_SAFE_PREC", "0.9"))
    it = 0
    while True:
        it += 1
        logger.info("Autopilot loop iteration %d", it)
        try:
            run_exchange(plan_text=plan, autopilot=True)
        except (RuntimeError, ValueError, OSError) as exc:
            logger.exception("run_exchange failed (recoverable): %s", exc)
        latest = _latest_decision()
        if latest:
            try:
                decision = json.loads(latest.read_text(encoding="utf-8"))
            except (OSError, ValueError, json.JSONDecodeError):
                decision = {}
            if _decision_safe(decision, safe_prec):
                logger.info("Decision %s passes safety criteria; exiting.", latest.name)
                return 0
            logger.info("Decision not yet safe; continuing. (file=%s)", latest.name)
        if iterations and it >= iterations:
            logger.info("Reached iteration cap (%d); exiting.", iterations)
            return 0
        logger.info("Sleeping %d seconds", interval)
        time.sleep(interval)
    return 0


__all__ = [
    "run_exchange",
    "recommend_next_action",
    "run_autopilot_loop",
]
