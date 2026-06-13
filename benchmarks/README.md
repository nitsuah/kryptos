# Attack-sweep benchmarks

Timing and search-space throughput for the fast K4 attack sweeps, so changes
to scoring/pruning can be compared run over run.

## Run locally (Docker)

```bash
docker run --rm -u root -v "$(pwd)/benchmarks:/app/benchmarks" \
  kryptos-agent-review kryptos benchmark --out-dir benchmarks
```

Writes `results.json` and `results.csv` here (gitignored — results are
per-machine, not repo state). Subset with `--cases beaufort_sweep,quagmire_sweep`.

## CI

The `benchmarks` job in `.github/workflows/ci-fast.yml` runs the full set on
every push/PR, prints the table to the job step summary, and uploads
`results.json`/`results.csv` as the `benchmark-results` build artifact.

## Cases

Defined in `kryptos.benchmarks.BENCHMARK_CASES`:

| case | attack |
|------|--------|
| `beaufort_sweep` | `kryptos.k4.beaufort_sweep.run_beaufort_sweep` |
| `quagmire_sweep` | `kryptos.k4.quagmire_sweep.run_quagmire_sweep` |
| `clock_hill` | `kryptos.k4.clock_hill_attack.run_clock_hill_attack` |
| `clock_vigenere` | `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack` |
| `clock_subrow` | `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack` |
| `clock_transposition` | `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack` |

`space_reduction` is the fraction of the enumerated space pruned by an
attack's pre-filter (e.g. the clock→Hill invertibility filter); `—` when the
attack has no pre-filter stage.
