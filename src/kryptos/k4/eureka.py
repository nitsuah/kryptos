"""Eureka capture protocol for K4 — K4-ATTACK-6.

On a 4-crib simultaneous match, writes a structured breakthrough snapshot
and raises EurekaSignal to halt the campaign immediately. The snapshot is
human-readable Markdown so it can be committed without post-processing.

The halt mechanism uses a sentinel exception rather than sys.exit() so that
callers can catch it, log it, and then decide whether to actually exit.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .keystream_validator import (
    K4_CRIBS,
    crib_hit_count,
    keystream_summary,
)

DEFAULT_SNAPSHOT_PATH = "K4_BREAKTHROUGH_SNAPSHOT.md"
EUREKA_THRESHOLD = 4  # all four confirmed cribs must match


class EurekaSignal(Exception):
    """Raised when all K4 cribs match simultaneously.

    Callers should catch this, persist state if needed, then re-raise or exit.
    Attributes:
        snapshot_path: Path where the breakthrough snapshot was written.
        result:        The full result dict that triggered the signal.
    """
    def __init__(self, snapshot_path: str, result: dict[str, Any]):
        self.snapshot_path = snapshot_path
        self.result = result
        super().__init__(f"EUREKA — 4-crib match. Snapshot: {snapshot_path}")


def check_eureka(
    candidate_text: str,
    cribs: dict | None = None,
    threshold: int = EUREKA_THRESHOLD,
) -> bool:
    """Return True if candidate_text matches at least `threshold` cribs."""
    if cribs is None:
        cribs = K4_CRIBS
    return crib_hit_count(candidate_text, cribs=cribs) >= threshold


def write_breakthrough_snapshot(
    candidate_text: str,
    key_info: dict[str, Any],
    extra: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_SNAPSHOT_PATH,
) -> str:
    """Write a Markdown snapshot capturing all context of a breakthrough.

    Args:
        candidate_text: The plaintext candidate that triggered eureka.
        key_info:        Key / permutation information dict (arbitrary structure).
        extra:           Any additional metadata to embed (attack params, etc.).
        path:            Destination file path.

    Returns:
        Absolute path of the written file as a string.
    """
    summary = keystream_summary(candidate_text)
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    crib_table_rows = []
    for label, info in summary.items():
        match_str = "✓ MATCH" if info["match"] else "✗ MISS"
        obs = info["observed_shifts"]
        exp = info["expected_shifts"]
        crib_table_rows.append(f"| {label:12s} | {match_str:8s} | {obs} | {exp} |")

    crib_table = "\n".join([
        "| Crib         | Status   | Observed shifts       | Expected shifts       |",
        "|:-------------|:---------|:----------------------|:----------------------|",
    ] + crib_table_rows)

    key_json = json.dumps(key_info, indent=2, default=str)
    extra_section = ""
    if extra:
        extra_json = json.dumps(extra, indent=2, default=str)
        extra_section = f"\n## Extra Metadata\n```json\n{extra_json}\n```\n"

    hits = sum(1 for info in summary.values() if info["match"])

    content = f"""# K4 BREAKTHROUGH SNAPSHOT

**Generated:** {ts}
**Crib hits:** {hits} / {len(summary)}
**Status:** {"🔑 ALL CRIBS MATCHED — CANDIDATE SOLUTION" if hits == len(summary) else f"⚠️ PARTIAL MATCH ({hits}/{len(summary)})"}

---

## Candidate Plaintext

```
{candidate_text}
```

## Crib Validation

{crib_table}

## Key / Permutation Info

```json
{key_json}
```
{extra_section}
## Raw Keystream Summary

```json
{json.dumps(summary, indent=2)}
```
"""

    out_path = Path(path)
    out_path.write_text(content, encoding="utf-8")
    return str(out_path.resolve())


def eureka_check_and_capture(
    candidate_text: str,
    key_info: dict[str, Any],
    extra: dict[str, Any] | None = None,
    snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    cribs: dict | None = None,
    threshold: int = EUREKA_THRESHOLD,
    raise_signal: bool = True,
) -> dict[str, Any] | None:
    """Check candidate for a eureka event; write snapshot and optionally raise.

    Call this after every candidate in the composite sweep. On a hit:
      1. Writes K4_BREAKTHROUGH_SNAPSHOT.md (or supplied path).
      2. Returns the result dict.
      3. If raise_signal=True (default), raises EurekaSignal to halt the loop.

    Args:
        candidate_text: Plaintext candidate.
        key_info:        Provenance dict (perm, alphabet, stage params, etc.).
        extra:           Additional metadata.
        snapshot_path:   Where to write the snapshot.
        cribs:           Crib dict (default K4_CRIBS).
        threshold:       Number of matching cribs required (default 4).
        raise_signal:    Whether to raise EurekaSignal on hit (default True).

    Returns:
        Result dict on hit (if raise_signal=False), None on miss.
    """
    if not check_eureka(candidate_text, cribs=cribs, threshold=threshold):
        return None

    written = write_breakthrough_snapshot(
        candidate_text, key_info, extra=extra, path=snapshot_path
    )
    result = {
        "candidate_text": candidate_text,
        "key_info": key_info,
        "snapshot_path": written,
        "crib_summary": keystream_summary(candidate_text),
    }

    if raise_signal:
        raise EurekaSignal(snapshot_path=written, result=result)

    return result


__all__ = [
    "EUREKA_THRESHOLD",
    "DEFAULT_SNAPSHOT_PATH",
    "EurekaSignal",
    "check_eureka",
    "write_breakthrough_snapshot",
    "eureka_check_and_capture",
]
