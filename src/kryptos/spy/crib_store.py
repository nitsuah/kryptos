"""Dynamic crib promotion and storage.

Cribs observed across multiple high-confidence SPY extractions are promoted
to a persistent store for use in scoring functions.

Promotion rules:
- Token must be A-Z only (uppercase)
- Length >= 3
- Confidence >= 0.8
- Observed in >= 2 distinct runs

File format (one per line): TOKEN\tOBSERVATIONS\tCONFIDENCE_AVG
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass

from kryptos.paths import get_artifacts_root

PROMOTED_CRIBS_PATH = get_artifacts_root() / "spy" / "promoted_cribs.txt"
OBSERVATIONS_PATH = get_artifacts_root() / "spy" / "observations.jsonl"

MAX_CRIBS_SIZE_BYTES = 10 * 1024


@dataclass(slots=True)
class CribObservation:
    token: str
    run_id: str
    confidence: float


def _is_valid_token(token: str) -> bool:
    return len(token) >= 3 and token.isalpha() and token.isupper()


def load_observations() -> list[CribObservation]:
    if not OBSERVATIONS_PATH.exists():
        return []
    observations = []
    with OBSERVATIONS_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                observations.append(
                    CribObservation(
                        token=data["token"],
                        run_id=data["run_id"],
                        confidence=data["confidence"],
                    ),
                )
            except (json.JSONDecodeError, KeyError):
                continue
    return observations


def save_observation(token: str, run_id: str, confidence: float) -> None:
    OBSERVATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OBSERVATIONS_PATH.open("a", encoding="utf-8") as fh:
        record = {"token": token, "run_id": run_id, "confidence": confidence}
        fh.write(json.dumps(record) + "\n")


def load_promoted_cribs() -> set[str]:
    if not PROMOTED_CRIBS_PATH.exists():
        return set()
    cribs = set()
    with PROMOTED_CRIBS_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            parts = line.strip().split("\t")
            if parts:
                cribs.add(parts[0])
    return cribs


def save_promoted_cribs(cribs: dict[str, tuple[int, float]]) -> None:
    if not cribs:
        return
    PROMOTED_CRIBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for token in sorted(cribs.keys()):
        count, avg_conf = cribs[token]
        lines.append(f"{token}\t{count}\t{avg_conf:.3f}\n")
    content = "".join(lines)
    if len(content.encode("utf-8")) > MAX_CRIBS_SIZE_BYTES:
        sorted_items = sorted(cribs.items(), key=lambda x: x[1][1], reverse=True)
        lines = []
        size = 0
        for token, (count, avg_conf) in sorted_items:
            line = f"{token}\t{count}\t{avg_conf:.3f}\n"
            line_bytes = len(line.encode("utf-8"))
            if len(lines) == 0:
                lines.append(line)
                size += line_bytes
            elif size + line_bytes <= MAX_CRIBS_SIZE_BYTES:
                lines.append(line)
                size += line_bytes
            else:
                break
    with PROMOTED_CRIBS_PATH.open("w", encoding="utf-8") as fh:
        fh.writelines(lines)


def promote_cribs(new_observations: list[CribObservation]) -> dict[str, int]:
    all_obs = load_observations()
    for obs in new_observations:
        if _is_valid_token(obs.token) and obs.confidence >= 0.8:
            save_observation(obs.token, obs.run_id, obs.confidence)
            all_obs.append(obs)
    token_stats: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for obs in all_obs:
        if _is_valid_token(obs.token) and obs.confidence >= 0.8:
            token_stats[obs.token][obs.run_id].append(obs.confidence)
    promoted = {}
    for token, run_map in token_stats.items():
        if len(run_map) >= 2:
            all_confs = [c for confs in run_map.values() for c in confs]
            avg_conf = sum(all_confs) / len(all_confs)
            promoted[token] = (len(run_map), avg_conf)
    save_promoted_cribs(promoted)
    return {token: count for token, (count, _) in promoted.items()}
