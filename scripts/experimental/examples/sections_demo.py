"""Demo script: iterate K1-K3 decrypt attempts & generate simple reports.

Run with: python -m kryptos.examples.sections_demo

K4 omitted here; use kryptos.k4.decrypt_best for composite search.
"""

from __future__ import annotations

import json
from pathlib import Path

from kryptos.analysis import check_cribs, frequency_analysis
from kryptos.reporting import generate_report
from kryptos.sections import SECTIONS


def run(config_path: str = "config/config.json") -> None:
    path = Path(config_path)
    with path.open(encoding="utf-8") as f:
        config = json.load(f)
    ciphertexts = config.get("ciphertexts", {})
    cribs = config.get("cribs", [])
    parameters = config.get("parameters", {})
    keys = parameters.get("vigenere_keys", [])

    for section, decrypt_fn in SECTIONS.items():
        if section == "K4":  # skip heavy pipeline
            continue
        ct = ciphertexts.get(section)
        if not ct:
            print(f"[WARN] No ciphertext for {section}; skipping")
            continue
        section_results = {"frequencies": {}, "cribs": {}}
        if not keys:
            print(f"[WARN] No candidate keys provided; skipping key trials for {section}")
            continue
        for key in keys:
            try:
                pt = decrypt_fn(ct, key) if section in {"K1", "K2"} else decrypt_fn(ct)
            except Exception as exc:  # broad for demo
                print(f"[ERROR] Decrypt failed for {section} key='{key}': {exc}")
                continue
            freqs = frequency_analysis(pt)
            matches = check_cribs(pt, cribs)
            section_results["frequencies"][key] = freqs
            section_results["cribs"][key] = matches
        generate_report(section_results, section)


if __name__ == "__main__":  # pragma: no cover
    run()
