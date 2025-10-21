# Plan for Tomorrow - 2025-10-21

Next steps to implement skipped items:

- Hill hypothesis: add function generating candidate Hill keys + decrypt loop; replace skip with assertions on result count and best score.
- Transposition constraint hypothesis: wrap search_with_multiple_cribs_positions across column ranges; test for at least one candidate and position bonus presence.
- Berlin clock Vigenère hypothesis: integrate clock shift enumeration + optional Vigenère key trial loop; test that candidates list non-empty and includes shift metadata.
- Full K4 ciphertext integration: create end-to-end pipeline assembly using all stages; assert fused output length, presence of adaptive diagnostics, artifact paths.
- Tell me which one to start and I’ll add code + tests.
