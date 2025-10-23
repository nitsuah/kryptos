"""Copy of orchestrator placed under scripts/dev for canonical dev tooling location."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

AGENTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'agents')
REPO_ROOT = os.path.dirname(os.path.dirname(AGENTS_DIR))
LOG_DIR_ARTIFACTS = os.path.join(REPO_ROOT, 'artifacts', 'logs')
os.makedirs(LOG_DIR_ARTIFACTS, exist_ok=True)
ARTIFACTS_STATE = os.path.join(os.path.dirname(AGENTS_DIR), 'artifacts', 'state.json')
STATE_PATH = ARTIFACTS_STATE if os.path.exists(ARTIFACTS_STATE) else os.path.join(AGENTS_DIR, 'state.json')
LEARNED_MD = os.path.join(AGENTS_DIR, 'LEARNED.md')


def _load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding='utf-8') as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return {}
    return {}


def _save_state(state: dict) -> None:
    with open(STATE_PATH, 'w', encoding='utf-8') as fh:
        json.dump(state, fh, indent=2)


def _append_learned(note: str) -> None:
    with open(LEARNED_MD, 'a', encoding='utf-8') as fh:
        fh.write(f"- {datetime.utcnow().isoformat()} {note}\n")


def load_personas() -> dict[str, str]:
    mapping = {}
    state = _load_state()
    for fname in ('spy.prompt', 'q.prompt', 'ops.prompt'):
        path = os.path.join(AGENTS_DIR, fname)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                text = fh.read()
                if fname.startswith('q') and state.get('learned'):
                    notes = ' '.join([f"{n['persona']}:{n['note']}" for n in state.get('learned', [])])
                    text = text + f"\n\n# LEARNED_SUMMARY: {notes}\n"
                mapping[fname.split('.')[0].upper()] = text
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
                rec, just = recommend_next_action()
                return f"Q_SUMMARY:\tRecommendation -> {rec}. {just} LEARN: tooling_ready"
            return f"Q_SUMMARY:\tPlan reviewed -> {plan}. Prepared tooling scaffold (placeholder). LEARN: tooling_ready"
        return "Q_SUMMARY:\tPrepared tooling scaffold (placeholder). LEARN: tooling_ready"
    if 'OPS' in persona_name:
        # OPS can be instructed to run tuning jobs via orchestrator.ops_run_tuning
        if 'PLAN_CHECK:' in persona_text and 'run: crib_weight_sweep' in persona_text:
            return "OPS_SUMMARY:\tReceived run request for crib_weight_sweep (will execute)."
        return "OPS_SUMMARY:\tNo runs executed yet (placeholder)."
    return "UNKNOWN_PERSONA"


def recommend_next_action() -> tuple[str, str]:
    """Return a short (1-line) recommendation and a one-sentence justification.

    Deterministic quick policy used for fast triage:
      - If OPS automation isn't present, recommend finishing OPS automation.
      - Else if there are tuning artifacts but no SPY extractor, recommend implementing SPY extractor.
      - Otherwise recommend pushing the branch and opening a PR.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    tr_dir = os.path.join(repo_root, 'artifacts', 'tuning_runs')
    has_artifacts = os.path.exists(tr_dir) and any(os.path.isdir(os.path.join(tr_dir, d)) for d in os.listdir(tr_dir))
    # detect a simple SPY extractor presence
    spy_extractor_path = os.path.join(repo_root, 'scripts', 'dev', 'spy_extractor.py')
    has_spy = os.path.exists(spy_extractor_path)
    # detect ops_run_tuning presence
    has_ops = hasattr(sys.modules.get(__name__), 'ops_run_tuning')

    if not has_ops:
        return (
            'finish OPS automation',
            'OPS automation is not available programmatically yet, so enable OPS to run tuning end-to-end.',
        )
    if has_artifacts and not has_spy:
        return (
            'implement SPY extractor',
            'there are tuning artifacts to analyze but no SPY extractor to summarize conservative cribs.',
        )
    return (
        "push branch & open PR",
        "the code, tests, and basic automation are in place; opening a PR captures the changes and requests review.",
    )


def ops_run_tuning(weights: list[float] | None = None, dry_run: bool = True) -> str:
    """Run the crib_weight_sweep script programmatically.

    Returns the run directory path as a string. By default this is a dry run (no network or external
    side-effects beyond writing artifacts) — the underlying script is already safe and writes to
    `artifacts/tuning_runs/run_<ts>/`.
    """
    import subprocess
    from pathlib import Path

    # repository root is two parents above this file (scripts/dev -> scripts -> repo)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sweep_path = os.path.join(repo_root, 'scripts', 'tuning', 'crib_weight_sweep.py')

    # build subprocess command to run the sweep script with optional args
    cmd = [sys.executable, sweep_path]
    if weights:
        cmd += ['--weights', ','.join(str(w) for w in weights)]
    if dry_run:
        cmd += ['--dry-run']

    # run the external script; it will write artifacts under artifacts/tuning_runs/
    subprocess.check_call(cmd, cwd=repo_root)
    tr_dir = Path(repo_root) / 'artifacts' / 'tuning_runs'
    if not tr_dir.exists():
        return ''
    runs = [p for p in tr_dir.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return ''
    latest = max(runs, key=lambda p: p.stat().st_mtime)
    return str(latest)


def run_exchange(personas: dict[str, str], rounds: int = 2):
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    fname = f'run_{ts}.jsonl'
    out_path_artifacts = os.path.join(LOG_DIR_ARTIFACTS, fname)
    state = _load_state()
    with open(out_path_artifacts, 'w', encoding='utf-8') as out_art:
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
