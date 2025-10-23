# Kryptos Sections API

This document defines the unified public interface for working with the four sections of Kryptos
(K1–K4). The goal is a predictable, minimal surface that lets higher‑level tooling (CLI, pipelines,
notebooks) enumerate sections and invoke appropriate decrypt or solve routines without bespoke
imports.

## Design Principles

* Symmetry: Each section has a module `kryptos.kN` exporting at least a
`decrypt` function (where feasible today).
* Indirection: `kryptos.sections.SECTIONS` provides a mapping `{"K1": fn, ...}`
so orchestration code can iterate deterministically.
* Thin Wrappers: K1/K2 Vigenère wrappers delegate to the canonical keyed
implementation; K3 delegates to the published double rotational transposition.
* Progressive Exposure: K4 currently exposes rich solver components under
`kryptos.k4.*` but is intentionally not bound into the simple `SECTIONS` mapping for bulk iteration
until the public search interface stabilizes.

## Current Status

| Section | Module          | Public Helper         | Notes |
|---------|-----------------|-----------------------|-------|
| K1      | `kryptos.k1`    | `decrypt(cipher,key)` | Keyed Vigenère |
| K2      | `kryptos.k2`    | `decrypt(cipher,key)` | Keyed Vigenère |
| K3      | `kryptos.k3`    | `decrypt(cipher)`     | Double rotational transposition |
| K4      | `kryptos.k4`    | `decrypt_best(cipher)`| Composite multi-stage search (returns `DecryptResult`) |

## Mapping

```python
from kryptos.sections import SECTIONS

for name, fn in SECTIONS.items():
    if name in {"K1", "K2"}:
        plaintext = fn(CIPHERTEXTS[name], "PALIMPSEST")
    elif name == "K3":
        plaintext = fn(CIPHERTEXTS[name])
    else:  # K4 returns DecryptResult
        result = fn(CIPHERTEXTS[name], limit=25)
        plaintext = result.plaintext
    print(name, plaintext[:50])
```

## Usage Examples

For an end-to-end sample use the CLI or call the composite helper directly:

```bash
kryptos sections
kryptos k4-decrypt --cipher path/to/k4.txt --limit 30 --adaptive --report
```

Or invoke programmatically with `kryptos.k4.decrypt_best` for K4.

### Decrypt K1 with a Candidate Key

```python
from kryptos.k1 import decrypt as decrypt_k1

plaintext = decrypt_k1(K1_CIPHERTEXT, "PALIMPSEST")
```

### Iterate K1/K2 Keys

```python
from kryptos.sections import SECTIONS
candidate_keys = ["PALIMPSEST", "ABSCISSA", "KRYPTOS"]

ct_k1 = "..."  # 63 chars
ct_k2 = "..."  # length as published

for key in candidate_keys:
    p1 = SECTIONS["K1"](ct_k1, key)
    p2 = SECTIONS["K2"](ct_k2, key)
```

### Decrypt K3

```python
from kryptos.k3 import decrypt as decrypt_k3
plaintext_k3 = decrypt_k3(K3_CIPHERTEXT)
```

### K4 Composite Decrypt

```python
from kryptos.k4 import decrypt_best

result = decrypt_best(K4_CIPHERTEXT, limit=40, adaptive=True, report=True)
print(result.plaintext, result.score)
for cand in result.candidates[:5]:
  print(cand.get('score'), cand.get('text')[:60])
```

`decrypt_best` returns a `DecryptResult` dataclass with: `plaintext`, `score`, `candidates`,
`profile`, optional `artifacts`, `attempt_log`, and `lineage`.

## Roadmap

1. Add uniform exception types (`KryptosDecryptError`). 2. Add stricter Protocol & typing for
heterogeneous section callables. 3. Document deterministic test vectors for each section. 4. Wire
CLI subcommands: `kryptos decrypt k1 --key PALIMPSEST ...` & `kryptos decrypt k4`. 5. Persist
standardized artifact bundle schema & version in `DecryptResult.metadata`.

## Deprecations

Legacy direct imports (e.g. `from kryptos.ciphers import vigenere_decrypt`) are still supported but
will be discouraged in favor of the uniform section modules for high-level usage. Low-level research
/ experimentation can continue to use the primitives module.

---

Last updated: (auto) section scaffolding phase, unify-packages milestone.
