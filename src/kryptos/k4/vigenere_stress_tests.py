"""Stress-testing harness for K1/K2 Vigenère key recovery.

``kryptos.k4.vigenere_key_recovery.recover_key_by_frequency`` has only been
validated on clean K1/K2 ciphertext at the correct key length
(``docs/analysis/K1_K2_VALIDATION_RESULTS.md``: deterministic 100% recovery
for both PALIMPSEST and ABSCISSA). This is the "Stress tests for K1/K2" item
from ROADMAP.md (Phase 4: Validation & hardening), covering the three
dimensions that document explicitly flagged as untested:

- **Noise**: random single-character substitutions in the ciphertext.
- **Wrong key length**: recovery attempted at lengths other than the true key length.
- **Partial ciphertext**: recovery attempted on a truncated prefix of the ciphertext.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Verified K1 ciphertext/plaintext (tests/smoke/test_k1_k2_k3_reliability.py)
K1_CIPHERTEXT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_KEY = "PALIMPSEST"
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

# K2 ciphertext (tests/smoke/test_k1_k2_k3_reliability.py); plaintext derived by
# decrypting with the known key ABSCISSA, used here as the ground truth that
# recover_key_by_frequency is expected to reproduce under stress.
K2_CIPHERTEXT = (
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIM"
    "VMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZE"
    "TKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFE"
    "ZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUA"
    "ECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFCHOBSSPH"
    "FLLOXQRZXGZQAAVTTEXOLIQQTIVWHHMQAUQZMASMRVLQJNWB"
)
K2_KEY = "ABSCISSA"
K2_PLAINTEXT = vigenere_decrypt(K2_CIPHERTEXT, K2_KEY)


def inject_noise(ciphertext: str, noise_rate: float, rng: random.Random) -> str:
    """Replace each alphabetic character with a uniformly random A-Z letter with probability ``noise_rate``."""
    return "".join(rng.choice(ALPHABET) if ch.isalpha() and rng.random() < noise_rate else ch for ch in ciphertext)


def _match_ratio(a: str, b: str) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(1 for x, y in zip(a, b, strict=True) if x == y) / len(a)


@dataclass(frozen=True)
class NoiseStressRun:
    noise_rate: float
    trial: int
    recovered_key: str | None
    key_match: bool
    plaintext_match_ratio: float


def run_noise_stress_test(
    ciphertext: str,
    key: str,
    plaintext: str,
    noise_rates: tuple[float, ...] = (0.0, 0.05, 0.10, 0.20),
    trials_per_rate: int = 2,
    seed: int = 42,
    top_n: int = 5,
) -> list[NoiseStressRun]:
    """Inject random-character noise at increasing rates and check whether key recovery survives."""
    rng = random.Random(seed)
    runs = []
    for noise_rate in noise_rates:
        for trial in range(trials_per_rate):
            noisy = inject_noise(ciphertext, noise_rate, rng)
            candidates = recover_key_by_frequency(noisy, key_length=len(key), top_n=top_n)
            recovered_key = candidates[0] if candidates else None
            decrypted = vigenere_decrypt(noisy, recovered_key) if recovered_key else ""
            runs.append(
                NoiseStressRun(
                    noise_rate=noise_rate,
                    trial=trial,
                    recovered_key=recovered_key,
                    key_match=recovered_key == key,
                    plaintext_match_ratio=_match_ratio(decrypted, plaintext),
                )
            )
    return runs


@dataclass(frozen=True)
class KeyLengthStressRun:
    key_length: int
    is_correct_length: bool
    top_candidate: str | None
    correct_key_in_top: bool
    plaintext_match_ratio: float


def run_key_length_stress_test(
    ciphertext: str,
    key: str,
    plaintext: str,
    candidate_lengths: tuple[int, ...],
    top_n: int = 5,
) -> list[KeyLengthStressRun]:
    """Run key recovery at a range of key lengths, most of them deliberately wrong."""
    runs = []
    for kl in candidate_lengths:
        candidates = recover_key_by_frequency(ciphertext, key_length=kl, top_n=top_n)
        top_candidate = candidates[0] if candidates else None
        decrypted = vigenere_decrypt(ciphertext, top_candidate) if top_candidate else ""
        runs.append(
            KeyLengthStressRun(
                key_length=kl,
                is_correct_length=(kl == len(key)),
                top_candidate=top_candidate,
                correct_key_in_top=key in candidates,
                plaintext_match_ratio=_match_ratio(decrypted, plaintext),
            )
        )
    return runs


@dataclass(frozen=True)
class PartialCiphertextStressRun:
    fraction: float
    ciphertext_length: int
    recovered_key: str | None
    key_match: bool
    plaintext_match_ratio: float


def run_partial_ciphertext_stress_test(
    ciphertext: str,
    key: str,
    plaintext: str,
    fractions: tuple[float, ...] = (1.0, 0.75, 0.5, 0.25),
    top_n: int = 5,
) -> list[PartialCiphertextStressRun]:
    """Truncate the ciphertext to decreasing fractions and check whether key recovery survives."""
    runs = []
    for fraction in fractions:
        n = max(len(key), int(len(ciphertext) * fraction))
        partial = ciphertext[:n]
        candidates = recover_key_by_frequency(partial, key_length=len(key), top_n=top_n)
        recovered_key = candidates[0] if candidates else None
        decrypted = vigenere_decrypt(partial, recovered_key) if recovered_key else ""
        runs.append(
            PartialCiphertextStressRun(
                fraction=fraction,
                ciphertext_length=n,
                recovered_key=recovered_key,
                key_match=recovered_key == key,
                plaintext_match_ratio=_match_ratio(decrypted, plaintext[:n]),
            )
        )
    return runs


def run_k1_k2_stress_suite(
    noise_rates: tuple[float, ...] = (0.0, 0.05, 0.10, 0.20),
    noise_trials_per_rate: int = 2,
    key_length_offsets: tuple[int, ...] = (-2, -1, 0, 1, 2),
    partial_fractions: tuple[float, ...] = (1.0, 0.75, 0.5, 0.25),
    seed: int = 42,
    top_n: int = 5,
    results_path: Path | str | None = None,
) -> dict:
    """Run noise / wrong-key-length / partial-ciphertext stress tests for both K1 and K2."""
    sections = {}
    for label, ciphertext, key, plaintext in (
        ("K1", K1_CIPHERTEXT, K1_KEY, K1_PLAINTEXT),
        ("K2", K2_CIPHERTEXT, K2_KEY, K2_PLAINTEXT),
    ):
        candidate_lengths = tuple(
            sorted({len(key) + offset for offset in key_length_offsets if len(key) + offset >= 2})
        )
        sections[label] = {
            "noise": [
                asdict(r)
                for r in run_noise_stress_test(
                    ciphertext, key, plaintext, noise_rates, noise_trials_per_rate, seed, top_n
                )
            ],
            "key_length": [
                asdict(r) for r in run_key_length_stress_test(ciphertext, key, plaintext, candidate_lengths, top_n)
            ],
            "partial_ciphertext": [
                asdict(r)
                for r in run_partial_ciphertext_stress_test(ciphertext, key, plaintext, partial_fractions, top_n)
            ],
        }

    summary = {
        "attack": "k1_k2_stress_tests",
        "run_params": {
            "noise_rates": list(noise_rates),
            "noise_trials_per_rate": noise_trials_per_rate,
            "key_length_offsets": list(key_length_offsets),
            "partial_fractions": list(partial_fractions),
            "seed": seed,
            "top_n": top_n,
        },
        "results": sections,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if results_path is not None:
        path = Path(results_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2))

    return summary
