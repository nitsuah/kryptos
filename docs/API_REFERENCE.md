# Kryptos Public API Reference

Reference version: 2025-10-23

Breadcrumb: Overview > API > Reference ---

This document enumerates the stable, supported Python entry points and CLI subcommands. Items not listed here are
considered internal and may change without notice.

## Stability Policy

- Stable: Semantic compatibility guaranteed across minor versions (only additive changes).
- Experimental: May change or be removed after one minor version; marked with warning in docstring.
- Deprecated: Emits `DeprecationWarning`; scheduled removal appears in `DEPRECATIONS.md`.

## Python Modules

### Core

- `kryptos.paths` — helpers for artifact directories, provenance hashing.
- `kryptos.logging.setup_logging(level="INFO", logger_name=None, ...)` — set up a namespaced logger.

### Sections

- `kryptos.k1.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k2.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k3.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k4.decrypt_best(ciphertext: str, limit=25, adaptive=True, report=False) -> DecryptBatch`
- `kryptos.sections.SECTIONS` mapping {"K1": fn, ...}

### K4 Scoring

- `kryptos.k4.scoring.combined_plaintext_score(plaintext: str) -> float`
- `kryptos.k4.scoring.positional_letter_deviation_score(plaintext: str, period=5) -> float`
- `kryptos.k4.scoring.combined_plaintext_score_extended(plaintext: str) -> float`
- `kryptos.k4.scoring.composite_score_with_stage_analysis(stage1_plaintext, stage2_plaintext, stage1_score,
stage2_score, stage1_weight=0.3, stage2_weight=0.7) -> dict`

### K4 Hypotheses

The hypothesis framework provides pluggable cipher implementations for K4 cryptanalysis. Each hypothesis class
implements the `Hypothesis` protocol with a `generate_candidates()` method.

#### Base Classes

- `kryptos.k4.hypotheses.Hypothesis` (Protocol) — Abstract interface for all hypothesis implementations
- `kryptos.k4.hypotheses.CompositeHypothesis` — Base class for chaining two hypotheses sequentially

#### Single-Stage Hypotheses

- `kryptos.k4.hypotheses.HillCipher2x2Hypothesis(limit=100)` — Hill cipher with 2x2 matrix (exhaustive key search)
- `kryptos.k4.hypotheses.SimpleSubstitutionHypothesis(variants=28)` — Monoalphabetic substitution with frequency
analysis
- `kryptos.k4.hypotheses.VigenereHypothesis(max_key_length=15, candidates_per_length=10)` — Vigenère cipher with
Kasiski/IOC analysis
- `kryptos.k4.hypotheses.AutokeyHypothesis(max_key_length=12, candidates_per_length=10)` — Autokey variant of Vigenère
- `kryptos.k4.hypotheses.PlayfairHypothesis(max_generations=50, population_size=100)` — Playfair cipher with genetic
algorithm
- `kryptos.k4.hypotheses.FourSquareHypothesis(max_generations=50, population_size=100)` — Four-square cipher with
genetic algorithm
- `kryptos.k4.hypotheses.BifidHypothesis(periods=[5,6,7,8,9,10], candidates_per_period=5)` — Bifid cipher with period
search
- `kryptos.k4.hypotheses.BerlinClockTranspositionHypothesis(widths=[5,6,7,8,10,12], limit_per_width=20)` — Columnar
transposition constrained by Berlin Clock
- `kryptos.k4.hypotheses.BerlinClockVigenereHypothesis(max_key_length=12, candidates_per_length=10)` — Vigenère
constrained by Berlin Clock periods

#### Composite (Two-Stage) Hypotheses

- `kryptos.k4.hypotheses.TranspositionThenHillHypothesis(transposition_candidates=20, hill_limit=1000,
transposition_widths=None)` — Transposition followed by Hill 2x2
- `kryptos.k4.hypotheses.VigenereThenTranspositionHypothesis(vigenere_candidates=50, transposition_limit=100,
vigenere_max_key_length=12, transposition_widths=None)` — Vigenère followed by transposition
- `kryptos.k4.hypotheses.SubstitutionThenTranspositionHypothesis(substitution_variants=28, transposition_limit=100,
transposition_widths=None)` — Substitution followed by transposition
- `kryptos.k4.hypotheses.HillThenTranspositionHypothesis(hill_limit=1000, transposition_candidates=20,
transposition_widths=None)` — Hill 2x2 followed by transposition
- `kryptos.k4.hypotheses.AutokeyThenTranspositionHypothesis(autokey_candidates=30, transposition_limit=100,
autokey_max_key_length=12, transposition_widths=None)` — Autokey followed by transposition
- `kryptos.k4.hypotheses.PlayfairThenTranspositionHypothesis(playfair_candidates=20, transposition_limit=100,
playfair_max_generations=30, transposition_widths=None)` — Playfair followed by transposition
- `kryptos.k4.hypotheses.DoubleTranspositionHypothesis(stage1_candidates=20, stage2_limit=100, stage1_widths=None,
stage2_widths=None)` — Two sequential transposition stages
- `kryptos.k4.hypotheses.VigenereThenHillHypothesis(vigenere_candidates=30, hill_limit=1000,
vigenere_max_key_length=12)` — Vigenère followed by Hill 2x2

### K4 Pipeline

- `kryptos.k4.pipeline.build_default(limit=50, adaptive=True) -> Pipeline`
- `kryptos.k4.composite.run_pipeline(ciphertext: str, pipeline: Pipeline) -> DecryptBatch`

### K4 Tuning

- `kryptos.k4.tuning.run_crib_weight_sweep(weights: list[float], run_dir: Path|None=None) -> list[CribWeightRow]`
- `kryptos.k4.tuning.pick_best_weight_from_rows(rows: list[CribWeightRow]) -> float`
- `kryptos.k4.tuning.tiny_param_sweep() -> list[TinyParamResult]`
- `kryptos.k4.tuning.holdout_score(weight: float, run_dir: Path|None=None) -> HoldoutSummary`
- `kryptos.k4.tuning.artifacts.end_to_end_process(run_dir: Path) -> Path`

### Reporting

- `kryptos.k4.report.write_condensed_report(run_dir: Path) -> Path`
- `kryptos.k4.report.write_top_candidates_markdown(run_dir: Path, limit=10) -> Path`

### Spy Extraction / Evaluation

- `kryptos.spy.extractor.extract(run_dir: Path, min_conf: float=0.3) -> list[str]`
- `kryptos.spy.extractor.scan_run(run_dir: Path) -> RunExtraction`

### Autopilot (Experimental)

- `kryptos.autopilot.run(plan: AutopilotPlan) -> AutopilotResult` (EXPERIMENTAL)
- `kryptos.autopilot.recommend_next_action(state: AutopilotState) -> ActionRecommendation` (EXPERIMENTAL)

## CLI Subcommands

Run `kryptos --help` for full usage; stable subcommands listed here.

| Subcommand | Status | Description |
|------------|--------|-------------|
| `sections` | Stable | List sections and brief info |
| `k4-decrypt` | Stable | Run K4 pipeline decrypt attempt |
| `k4-attempts` | Stable | Flush in-memory attempt log to artifacts |
| `tuning-crib-weight-sweep` | Stable | Sweep crib weights and record deltas |
| `tuning-pick-best` | Stable | Select best crib weight from CSV |
| `tuning-summarize-run` | Stable | Summarize a tuning run directory |
| `tuning-tiny-param-sweep` | Stable | Deterministic small parameter sweep |
| `tuning-holdout-score` | Stable | Evaluate chosen crib weight on holdout sentences |
| `tuning-report` | Planned | Combined condensed + top candidates report (future) |
| `spy-eval` | Stable | Evaluate SPY predictions across runs |
| `spy-extract` | Stable | Extract SPY phrases meeting confidence threshold |
| `autopilot` | Experimental | Run autopilot loop with persona strategy |

## Deprecated / Pending Removal

See `DEPRECATIONS.md` for timeline.

## Versioning Notes

Public API changes recorded in `CHANGELOG.md`. Breaking change proposals require prior deprecation window.

## Examples

### Using Hypothesis Classes

#### Single-Stage Hypothesis

```python
from kryptos.k4.hypotheses import VigenereHypothesis

# Create hypothesis with custom parameters
hypothesis = VigenereHypothesis(
    max_key_length=15,
    candidates_per_length=10
)

# Generate candidates for K4 ciphertext
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
candidates = hypothesis.generate_candidates(K4_CIPHER, limit=25)

# Inspect results
for candidate in candidates[:5]:
    print(f"Score: {candidate.score:.2f}")
    print(f"Plaintext: {candidate.plaintext}")
    print(f"Key: {candidate.metadata.get('key')}")
    print()
```

#### Composite (Two-Stage) Hypothesis

```python
from kryptos.k4.hypotheses import TranspositionThenHillHypothesis

# Create composite hypothesis
hypothesis = TranspositionThenHillHypothesis(
    transposition_candidates=20,  # Top 20 transposition results
    hill_limit=1000,              # Test 1000 Hill 2x2 keys per stage1 result
    transposition_widths=[5, 6, 7, 8, 10]  # Column widths to try
)

# Generate candidates
candidates = hypothesis.generate_candidates(K4_CIPHER, limit=10)

# Examine composite metadata
best = candidates[0]
print(f"Transformation chain: {best.metadata['transformation_chain']}")
print(f"Stage1 plaintext: {best.metadata['stage1_plaintext']}")
print(f"Stage2 plaintext: {best.plaintext}")
```

### Custom Scoring Functions

```python
from kryptos.k4.scoring import (
    combined_plaintext_score,
    composite_score_with_stage_analysis
)

# Basic scoring
plaintext = "ITWASFOUNDUNDERGROUND"
score = combined_plaintext_score(plaintext)
print(f"Score: {score:.2f}")

# Stage-aware composite scoring
stage1_text = "QWERTYYUIOPASD..."
stage2_text = "ITWASFOUNDUNDERGROUND..."
stage1_score = combined_plaintext_score(stage1_text)
stage2_score = combined_plaintext_score(stage2_text)

result = composite_score_with_stage_analysis(
    stage1_text, stage2_text,
    stage1_score, stage2_score,
    stage1_weight=0.3,
    stage2_weight=0.7
)

print(f"Final score: {result['final_score']:.2f}")
print(f"IOC improvement bonus: {result['ioc_bonus']:.2f}")
print(f"Word pattern bonus: {result['word_bonus']:.2f}")
print(f"Frequency convergence bonus: {result['freq_bonus']:.2f}")
```

### Artifact Provenance Tracking

```python
from kryptos.paths import get_provenance_info
import json

# Capture environment state
provenance = get_provenance_info(include_params={
    'hypothesis': 'TranspositionThenHill',
    'transposition_candidates': 20,
    'hill_limit': 1000
})

# Save with artifact
artifact_data = {
    'provenance': provenance,
    'results': [...],
    'timestamp': provenance['timestamp']
}

with open('artifacts/my_run.json', 'w') as f:
    json.dump(artifact_data, f, indent=2)

# Provenance includes:
# - git_commit: Current commit hash
# - git_branch: Current branch name
# - git_dirty: Whether there are uncommitted changes
# - python_version: Full Python version string
# - platform: OS details
# - timestamp: ISO 8601 UTC timestamp
# - params: Custom run parameters
```

### Building Custom Hypotheses

To create a custom hypothesis, implement the `Hypothesis` protocol:

```python
from kryptos.k4.hypotheses import Hypothesis
from kryptos.k4.candidate import Candidate
from kryptos.k4.scoring import combined_plaintext_score

class MyCustomHypothesis:
    """Custom cipher hypothesis."""

    def __init__(self, my_param: int = 10):
        self.my_param = my_param

    def generate_candidates(
        self,
        ciphertext: str,
        limit: int = 10
    ) -> list[Candidate]:
        """Generate decryption candidates.

        Args:
            ciphertext: The text to decrypt
            limit: Maximum number of candidates to return

        Returns:
            List of Candidate objects, sorted by score (descending)
        """
        candidates = []

        # Your decryption logic here
        for key in self._generate_keys():
            plaintext = self._decrypt(ciphertext, key)
            score = combined_plaintext_score(plaintext)

            candidate = Candidate(
                id=f"MyCustom-{key}",
                plaintext=plaintext,
                score=score,
                metadata={
                    'hypothesis': 'MyCustomHypothesis',
                    'key': key,
                    'my_param': self.my_param
                }
            )
            candidates.append(candidate)

        # Sort by score and return top results
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:limit]

    def _generate_keys(self):
        """Generate possible keys."""
        # Your key generation logic
        pass

    def _decrypt(self, ciphertext: str, key) -> str:
        """Decrypt with given key."""
        # Your decryption logic
        pass
```

### Composite Hypothesis Chaining

The `CompositeHypothesis` base class handles two-stage decryption automatically:

```python
from kryptos.k4.hypotheses import CompositeHypothesis, VigenereHypothesis, SimpleSubstitutionHypothesis

class MyCompositeHypothesis(CompositeHypothesis):
    """Custom two-stage hypothesis."""

    def __init__(
        self,
        stage1_candidates: int = 30,
        stage2_limit: int = 100
    ):
        # Initialize stage1 hypothesis
        stage1 = VigenereHypothesis(
            max_key_length=12,
            candidates_per_length=stage1_candidates // 6
        )

        # Initialize stage2 hypothesis
        stage2 = SimpleSubstitutionHypothesis(variants=28)

        # Call parent constructor
        super().__init__(
            stage1_hypothesis=stage1,
            stage2_hypothesis=stage2,
            stage1_candidates=stage1_candidates,
            stage2_limit=stage2_limit,
            hypothesis_name="MyComposite"
        )

# Use it
hypothesis = MyCompositeHypothesis(stage1_candidates=50, stage2_limit=200)
candidates = hypothesis.generate_candidates(ciphertext, limit=10)
```

Last updated: 2025-10-24T03:55Z
