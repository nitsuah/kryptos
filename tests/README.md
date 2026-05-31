# Test Suite

Tests are organized into three tiers. Run all tiers with `pytest` from the project root.

```
pytest                        # all tiers
pytest tests/smoke/           # smoke only (fast, ≤ a few seconds)
pytest tests/functional/      # unit/functional only
pytest tests/e2e/             # end-to-end / integration only
pytest -m "not slow"          # skip explicitly slow tests in any tier
```

---

## smoke/

Fast sanity checks — CLI entry points, K1-K3 correctness, quick coverage passes. Should finish in seconds.

| File | What it covers |
|------|---------------|
| test_cli.py | CLI entrypoint smoke |
| test_cli_logging.py | CLI logging basic run |
| test_cli_subcommands.py | CLI subcommand dispatch |
| test_composite_3layer.py | 3-layer composite smoke |
| test_k1_k2_k3_reliability.py | Basic correctness for K1–K3 |
| test_k1_k2_monte_carlo.py | Quick Monte Carlo (gated on env flag) |
| test_hypothesis_sanity.py | Hypothesis property sanity checks |
| test_deprecation_warning.py | Deprecation warning smoke |
| test_fast_coverage_*.py | Targeted quick-coverage passes for various modules |

---

## functional/

Single-module or single-feature unit tests. Each file exercises one function, class, or subsystem in isolation (or near-isolation).

Key groupings:

- **Ciphers**: test_ciphers.py, test_ciphers_*.py, test_adfgvx.py, test_nihilist.py, test_transposition*.py, test_vigenere_key_recovery.py
- **Hill cipher**: test_hill_cipher_edge.py, test_hill_genetic.py, test_hill_search_module.py
- **Scoring**: test_scoring*.py, test_crib_aware_scoring.py, test_rarity_weighted_crib_bonus.py, test_positional_letter_deviation.py
- **Cribs**: test_cribs_functions.py, test_crib_store.py
- **Attacks**: test_attack_extractor.py, test_attack_generator.py, test_attack_provenance.py, test_ops_attack_generation.py
- **Agents**: test_linguist.py, test_ops_agent.py, test_q_agent.py, test_spy_*.py
- **K4 features**: test_k4_adaptive_weights.py, test_k4_attempt_logging.py, test_k4_berlin_clock.py, test_k4_cribs.py, test_k4_decrypt_best.py, test_k4_entropy.py, test_k4_hill_cipher.py, test_k4_hypotheses.py, test_k4_instructional_scorer.py, test_k4_inverse_transposition_sweep.py, test_k4_keyed_alphabet_realignment.py, test_k4_keystream_validator.py, test_k4_masking.py, test_k4_performance.py, test_k4_positional_crib_bonus.py, test_k4_quadgrams.py, test_k4_scaffolding.py, test_k4_scoring*.py, test_k4_transposition*.py, test_k4_tuning*.py
- **Pipeline stages**: test_pipeline_*.py
- **Composite**: test_composite_adaptive_reporting.py, test_composite_branch_coverage.py, test_composite_chains.py, test_composite_chain_thresholds.py, test_composite_report_no_weights.py
- **Infrastructure**: test_logging_setup.py, test_paths_helpers.py, test_public_api.py, test_report_module.py, test_reporting_artifacts.py, test_search_space*.py, test_solver_config.py, test_stage_interface.py
- **Misc**: test_analysis_edge_cases.py, test_cross_run_memory.py, test_docs_breadcrumbs.py, test_examples_*.py, test_literature_bridge.py, test_multiproc_helpers.py, test_ops_llm_integration.py, test_ops_sim.py, test_paper_search.py, test_q_research.py, test_strategic_coverage.py

---

## e2e/

Full-workflow and multi-component integration tests. These cover campaign orchestration, autonomous coordinators, checkpointing, full pipeline runs, and multi-process execution.

| File | What it covers |
|------|---------------|
| test_autonomous_coordinator.py | Autonomous coordinator full cycle |
| test_checkpoint_system.py | Checkpoint system integration |
| test_multiproc_campaign.py | Full campaign orchestration (multiprocessing) |
| test_k4_composite_pipeline.py | K4 composite pipeline end-to-end |
| test_k4_composite_sweep.py | K4 composite sweep |
| test_k4_demo.py | K4 demo run |
| test_k4_eureka.py | K4 eureka detection flow |
| test_k4_fusion.py | K4 fusion pipeline |
| test_k4_pipeline_stage.py | K4 pipeline stage integration |
| test_sections_api.py | Sections API full flow |
| test_sections_decrypt.py | Sections decrypt full flow |
| test_autopilot_crib_update.py | Autopilot crib-update flow |
| test_autopilot_demo.py | Autopilot demo run |
| test_autopilot_flow.py | Autopilot full workflow |
| test_calibration_harness.py | Calibration harness integration |
| test_k3_autonomous_solving.py | K3 autonomous solving campaign |
| test_k3_monte_carlo_comprehensive.py | K3 comprehensive Monte Carlo |
| test_meta_coordinator.py | Meta-coordinator orchestration |
