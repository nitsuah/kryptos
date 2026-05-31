from kryptos.k4.solver_config import (
    SolverConfig,
    make_ci_solver_config,
    make_exploration_solver_config,
)


def test_solver_config_defaults_are_empty():
    config = SolverConfig()

    assert config.rng_seed is None
    assert config.vigenere_max_candidates is None
    assert config.sa_num_restarts is None
    assert config.sa_max_iterations is None
    assert config.sa_initial_temp is None
    assert config.sa_cooling_rate is None
    assert config.hc_max_iterations is None


def test_make_ci_solver_config_uses_deterministic_defaults():
    config = make_ci_solver_config()

    assert config.rng_seed == 42
    assert config.vigenere_max_candidates == 100_000
    assert config.sa_num_restarts is None
    assert config.sa_max_iterations is None


def test_make_exploration_solver_config_overrides_seed_and_budget():
    config = make_exploration_solver_config(seed=123)

    assert config.rng_seed == 123
    assert config.sa_num_restarts == 20
    assert config.sa_max_iterations == 200_000
    assert config.sa_initial_temp == 75.0
    assert config.sa_cooling_rate == 0.9997
    assert config.vigenere_max_candidates == 500_000
