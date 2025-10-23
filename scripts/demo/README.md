# K4 Demo

This folder contains a tiny demo runner that exercises a short K4 composite pipeline and writes
artifacts under `artifacts/demo/run_<ts>/`.

Usage (local):

``` pwsh
python scripts/demo/run_k4_demo.py --limit 10
```

The demo is intentionally small and fast so it can be run in CI or locally without heavy compute.
