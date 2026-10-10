> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) <!-- nav -->

# Open5 Frontier: Bounded Diagnostics for the Remaining K4 Families

**Status:** diagnostic primitives and planted tests added; this is not a family-wide elimination.

This module is intentionally honest about what the confirmed EAST, NORTHEAST, BERLIN and CLOCK cribs can establish. A candidate-generation helper is not a cipher hypothesis until the transformation order, source, parameters and physical assumptions are specified independently.

## Implemented in `kryptos.k4.open5_frontier`

- `align_crib_with_edits`: exact monotone alignment enumeration for a caller-supplied crib window and bounded inserted ciphertext symbols / missing crib symbols. It preserves index pairs and distinguishes the two edit types. It does **not** search arbitrary transposition plus edits; callers must preserve original K4 coordinates and validate all cribs together.
- `hill_partial_block_coverage`: reports the partial output-row equations available for Hill sizes 6–10 under each block alignment. It deliberately reports the evidence geometry, not a fabricated matrix solution. A useful next step is a named transposition family that repositions crib blocks, followed by modular equation solving over both 2 and 13.
- `keyed_lookup_streams`: derives candidate per-position streams from a caller-supplied ordered list of labels (first/last letter, initials, or label length). It never sorts labels or fabricates missing Weltzeituhr plates. Actual plate order and time-zone semantics remain a physical-source dependency.
- `bearing_seed_candidates`: enumerates explicit degree/tenths/hundredths scalar encodings modulo named candidate domains. It does not assume the bearing defines a route. A seed is only useful when paired with a separately justified cipher construction.

The functional tests include planted insertion/deletion alignments, partial Hill evidence, ordered lookup streams, and modular bearing seeds. They check that the helpers behave as specified, not that any helper decrypts K4.

## Open5 status

| Open family | What this pass adds | What remains open |
|---|---|---|
| Hill 6×6 and larger | Alignment-by-alignment partial-block evidence report for n=6–10 | No exhaustive invertible-matrix search; the crib constraints are sparse. Needs a named transposition or stronger crib blocks. |
| Long keys / non-English running keys | Explicitly separates key-source enumeration from claims of Englishness | Still needs a finite source corpus or generation rule plus a named transposition; arbitrary unknown-language text is not falsifiable as an unrestricted family. |
| Length-changing masking | Exact bounded local crib alignment with original-position mapping | No combined global search over edit patterns, key families and transpositions yet; nulls need shuffled controls and positive controls at the full pipeline level. |
| Per-letter lookup key | Deterministic streams from the *supplied* ordered label list | The actual remaining clock plates, order, date-line plate and wind-rose orientation are not fully sourced. No physical order is inferred. |
| Compass-rose bearing as non-route seed | Named scalar encodings and moduli | No arbitrary cipher construction is tested by a seed list alone. A measured primary-source bearing is still needed; existing route/dial sweeps do not eliminate other bearing uses. |

## Other chat hypotheses retained

- The Weltzeituhr could supply not only a steady dial state but a different city/time-zone/label-derived symbol for each ciphertext position.
- The clock/rose orientation may define an alphabet or a cipher setting, not merely a travel direction.
- K1–K3 may contribute a combined key or running source; known PALIMPSEST/ABSCISSA/KRYPTOS combinations are only a subset of possible generation rules.
- The compass bearing could seed a non-route transformation. Existing whole-degree route scans do not rule that out.
- Missing or deliberate misspellings, dropped/inserted letters, plate order and front/back reading are distinct variables and should not be bundled into one unconstrained search.


### Geometry/orientation hypothesis carried forward from the investigation

The working interpretation discussed alongside this branch is that the compass rose's ENE direction (67.5° on a 16-point rose) may determine an orientation or key/alphabet setting, not necessarily a route. A geographic ray from the CIA installation toward the Russian Far East/Kamchatka is a separate consequence to map-check; it is not evidence that K4 uses a route cipher. Likewise, the Weltzeituhr faceplate/clock orientation may define a phase, alphabet rotation, or reading order. These are candidate variables to enumerate only once the actual faceplate orientation and the relevant bearing are sourced. Existing whole-degree route and steady-dial scans do not eliminate these non-route orientation constructions.

## Reproduction

```bash
pytest tests/functional/test_k4_open5_frontier.py -q
pytest tests/functional/test_k4_keyed_columnar_frontier.py -q
```

A null result from these helpers is not evidence against any broad Open5 family. Promotion to an eliminated or statistical ledger tier requires a complete, bounded search, a planted positive control, and where applicable shuffled-ciphertext controls, consistent with `docs/GOVERN.md`.
