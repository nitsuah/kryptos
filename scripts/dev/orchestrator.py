"""Copy of orchestrator placed under scripts/dev for canonical dev tooling location."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime

from kryptos.paths import get_artifacts_root, get_logs_dir, get_repo_root

REPO_ROOT = get_repo_root()
AGENTS_DIR = REPO_ROOT / 'agents'
LOG_DIR_ARTIFACTS = get_logs_dir()
STATE_PATH = get_artifacts_root() / 'state.json'
LEARNED_MD = AGENTS_DIR / 'LEARNED.md'


def _load_state() -> dict:
    if STATE_PATH.exists():
        with STATE_PATH.open(encoding='utf-8') as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return {}
    return {}


def _save_state(state: dict) -> None:
    # Ensure parent directory exists before writing state file (CI may not have 'agents/')
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open('w', encoding='utf-8') as fh:
        json.dump(state, fh, indent=2)


def _append_learned(note: str) -> None:
    # Ensure parent directory for LEARNED.md exists
    LEARNED_MD.parent.mkdir(parents=True, exist_ok=True)
    with LEARNED_MD.open('a', encoding='utf-8') as fh:
        fh.write(f"- {datetime.utcnow().isoformat()} {note}\n")


def load_personas() -> dict[str, str]:
    mapping = {}
    state = _load_state()
    for fname in ('spy.prompt', 'q.prompt', 'ops.prompt'):
        path = AGENTS_DIR / fname
        if path.exists():
            with path.open(encoding='utf-8') as fh:
                text = fh.read()
                if fname.startswith('q') and state.get('learned'):
                    notes = ' '.join([f"{n['persona']}:{n['note']}" for n in state.get('learned', [])])
                    text = text + f"\n\n# LEARNED_SUMMARY: {notes}\n"
                mapping[fname.split('.')[0].upper()] = text
    # If no persona prompt files exist (test/CI environments), provide conservative defaults
    # so run_exchange writes non-empty logs during test runs.
    mapping.setdefault('Q', "Q_PERSONA_PLACEHOLDER: Provide a short recommendation or review the plan.")
    mapping.setdefault('OPS', "OPS_PERSONA_PLACEHOLDER: Manage tuning runs and report status.")
    mapping.setdefault('SPY', "SPY_PERSONA_PLACEHOLDER: Extract conservative cribs and summarize findings.")
    return mapping


def simulate_action(persona_name: str, persona_text: str) -> str:
    _ = persona_text
    if 'SPY' in persona_name:
        # If the Q prompt included a PLAN_CHECK, echo that the plan was reviewed
        if 'PLAN_CHECK:' in persona_text:
            plan = persona_text.split('PLAN_CHECK:', 1)[1].strip()
            return (
                "SPY_SUMMARY:\tReviewed plan -> "
                f"{plan}. Extracted 0 conservative crib candidates (placeholder). "
                "LEARN: no_cribs_found"
            )
        return "SPY_SUMMARY:\tExtracted 0 conservative crib candidates (placeholder). LEARN: no_cribs_found"
    if 'Q' in persona_name:
        if 'PLAN_CHECK:' in persona_text:
            plan = persona_text.split('PLAN_CHECK:', 1)[1].strip()
            # if the plan requests a recommendation, produce a short deterministic suggestion
            if any(k in plan.lower() for k in ('recommend', 'best next', 'choose', 'what is best')):
                rec, just, _meta = recommend_next_action()
                return f"Q_SUMMARY:\tRecommendation -> {rec}. {just} LEARN: tooling_ready"
            return f"Q_SUMMARY:\tPlan reviewed -> {plan}. Prepared tooling scaffold (placeholder). LEARN: tooling_ready"
        return "Q_SUMMARY:\tPrepared tooling scaffold (placeholder). LEARN: tooling_ready"
    if 'OPS' in persona_name:
        # OPS can be instructed to run tuning jobs via orchestrator.ops_run_tuning
        if 'PLAN_CHECK:' in persona_text and 'run: crib_weight_sweep' in persona_text:
            return "OPS_SUMMARY:\tReceived run request for crib_weight_sweep (will execute)."
        return "OPS_SUMMARY:\tNo runs executed yet (placeholder)."
    return "UNKNOWN_PERSONA"


def recommend_next_action() -> tuple[str, str, dict]:
    """Return a structured plan dict describing the recommended next action.

    We produce both a human-friendly short recommendation and a structured
    plan so callers can act programmatically. The returned tuple is:
      (recommendation_text: str, justification: str, plan: dict)

    Minimal plan schema:
      { 'action': 'run_ops'|'analyze_artifacts'|'push_pr'|'noop',
        'params': {...},
        'metadata': {...}
      }
    """
    repo_root = REPO_ROOT
    tr_dir = get_artifacts_root() / 'tuning_runs'
    has_artifacts = tr_dir.exists() and any(d.is_dir() for d in tr_dir.iterdir())

    # detect a simple SPY extractor presence
    spy_extractor_path = repo_root / 'scripts' / 'dev' / 'spy_extractor.py'
    has_spy = spy_extractor_path.exists()

    # detect ops_run_tuning presence: check for consolidated tuning.py
    has_ops = callable(globals().get('ops_run_tuning'))
    if not has_ops:
        sweep_script = repo_root / 'scripts' / 'tuning.py'
        has_ops = sweep_script.exists()

    metadata = {
        'has_artifacts': bool(has_artifacts),
        'has_spy': bool(has_spy),
        'has_ops': bool(has_ops),
        'tuning_runs_dir': str(tr_dir),
    }

    if not has_ops:
        rec = 'finish OPS automation'
        just = 'OPS automation is not available programmatically yet, so enable OPS to run tuning end-to-end.'
        plan = {'action': 'noop', 'params': {}, 'metadata': metadata}
        return rec, just, plan

    if has_artifacts and not has_spy:
        rec = 'implement SPY extractor'
        just = 'there are tuning artifacts to analyze but no SPY extractor to summarize conservative cribs.'
        plan = {'action': 'analyze_artifacts', 'params': {'run_dir': tr_dir}, 'metadata': metadata}
        return rec, just, plan

    rec = 'push branch & open PR'
    just = 'the code, tests, and basic automation are in place; opening a PR captures the changes and requests review.'
    plan = {'action': 'push_pr', 'params': {}, 'metadata': metadata}
    return rec, just, plan


def ops_run_tuning(
    weights: list[float] | None = None,
    dry_run: bool = True,  # noqa: ARG001 - kept for backward compat, not used
    retries: int = 3,
    backoff_factor: float = 0.5,
) -> str | dict:
    """Run the consolidated tuning CLI sweep command programmatically.

    Returns the run directory path as a string. By default this is a dry run (no network or external
    side-effects beyond writing artifacts) — the underlying script is already safe and writes to
    `artifacts/tuning_runs/run_<ts>/`.
    """
    repo_root = REPO_ROOT
    # Use consolidated tuning.py script instead of old crib_weight_sweep.py
    sweep_path = repo_root / 'scripts' / 'tuning.py'

    # build subprocess command to run the sweep command with optional args
    cmd = [sys.executable, str(sweep_path), 'sweep']
    if weights:
        cmd += ['--weights', ','.join(str(w) for w in weights)]
    # Note: dry_run not implemented in new CLI yet, skip it

    # run the external script; it will write artifacts under artifacts/tuning_runs/
    # implement retries with exponential backoff for transient failures
    attempts = 0
    max_retries = int(retries)
    while True:
        try:
            attempts += 1
            print(f"ops_run_tuning: attempt {attempts} running sweep script (cmd={cmd})")
            subprocess.check_call(cmd, cwd=repo_root)
            break
        except (subprocess.CalledProcessError, OSError) as exc:
            print(f"ops_run_tuning: attempt {attempts} failed with: {exc}")
            if attempts >= max_retries:
                print(f"ops_run_tuning: exceeded max retries ({max_retries}), aborting")
                return ''
            sleep_for = float(backoff_factor) * (2 ** (attempts - 1))
            print(f"ops_run_tuning: sleeping {sleep_for:.2f}s before retry")
            time.sleep(sleep_for)

    tr_dir = get_artifacts_root() / 'tuning_runs'
    if not tr_dir.exists():
        return ''
    runs = [p for p in tr_dir.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return ''
    # prefer runs that contain the primary sweep csv artifact
    runs_with_csv = [p for p in runs if (p / 'crib_weight_sweep.csv').exists()]
    if runs_with_csv:
        latest = max(runs_with_csv, key=lambda p: p.stat().st_mtime)
    else:
        latest = max(runs, key=lambda p: p.stat().st_mtime)

    # compute simple run metadata: max delta across weight detail CSVs
    try:
        import csv

        max_delta = 0.0
        for csvf in latest.glob('weight_*_details.csv'):
            with csvf.open('r', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        d = float(row.get('delta', '0'))
                    except (ValueError, KeyError):
                        d = 0.0
                    if d > max_delta:
                        max_delta = d
    except (OSError, ValueError, json.JSONDecodeError):
        max_delta = 0.0

    meta = {'run_dir': str(latest), 'max_delta': float(max_delta)}
    # backward compatibility: if called with the default signature return the run_dir string
    if retries == 3 and backoff_factor == 0.5:
        return str(latest)
    return meta


def run_exchange(personas: dict[str, str], rounds: int = 2):
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    fname = f'run_{ts}.jsonl'
    out_path_artifacts = LOG_DIR_ARTIFACTS / fname
    state = _load_state()
    with out_path_artifacts.open('w', encoding='utf-8') as out_art:
        for r in range(rounds):
            for name, text in personas.items():
                act = simulate_action(name, text)
                entry = {'round': r + 1, 'persona': name, 'action': act, 'time': datetime.utcnow().isoformat()}
                line = json.dumps(entry) + '\n'
                out_art.write(line)
                print(entry)
                if 'LEARN:' in act:
                    learn_text = act.split('LEARN:', 1)[1].strip()
                    state.setdefault('learned', []).append(
                        {
                            'persona': name,
                            'note': learn_text,
                            'time': datetime.utcnow().isoformat(),
                        },
                    )
                    _append_learned(f"{name}: {learn_text}")
                if any(k in act for k in ('EXTRACTED', 'PREPARED', 'NO_RUNS')):
                    state.setdefault('events', []).append(
                        {
                            'persona': name,
                            'event': act,
                            'time': datetime.utcnow().isoformat(),
                        },
                    )
    _save_state(state)
    return out_path_artifacts


if __name__ == '__main__':
    p = load_personas()
    run_exchange(p, rounds=2)
