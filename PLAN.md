# Plan for Tomorrow - 2025-10-21

GitHub Copilot

Sequence:

1. Hill hypothesis generator: low scope, adds missing branches (key generation + score loop). Define deterministic small key search space so test is stable.
2. Transposition constraint hypothesis: exercise multi-crib positional bonus lines; ensure test seeds cribs and column range to guarantee at least one hit.
3. Berlin clock + optional Vigenère trial: add metadata assertions (shift index, maybe key tried). Keep key list tiny to avoid slow tests.
4. Full K4 end‑to‑end pipeline: integrate all stages on a shortened or mock ciphertext segment for speed; assert diagnostics, fused scores, artifact path creation.
5. Scoring loader fallbacks: simulate missing n-gram files or configs to trigger fallback paths; assert default scores loaded correctly.

Considerations:

- Make hypothesis functions pure and injectable (accept ciphertext, params) for easy test control.
- Limit search spaces to keep runtime fast (<0.5s per test).
- Use fixtures for crib sets and sample ciphertext.
- Add coverage for failure/empty-return branches with a second negative test (e.g., no valid Hill keys).
- Ensure artifact writing mocked or directed to a temp directory for deterministic cleanup.

Next step after these: target remaining scoring loader fallbacks with simulated missing files/config.
