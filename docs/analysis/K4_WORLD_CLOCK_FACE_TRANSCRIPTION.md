# World Clock Face Transcription (2017 Snapshot)

> 🧭 [kryptos](../../README.md) <!-- nav -->

**Status:** provisional ordered input data; not a confirmed 1990 transcription and not a K4 result.

## Why this exists

Issue [#244](https://github.com/nitsuah/kryptos/issues/244) links to Thanos Zekios's independent [K4 eliminations repository](https://github.com/zeyeteam-debug/kryptos-k4-eliminations). Its README includes a per-face, top-to-bottom transcription of the Alexanderplatz Weltzeituhr labels from user-submitted photos (mostly 2017, with some later screenshots). This is more useful for testing per-letter clock lookup ideas than the existing flat list of confirmed city names, because the ordering of labels on each side of a face is preserved.

The transcription is stored in `kryptos.k4.world_clock_faces_2017`. It records top and bottom sides separately and keeps three states distinct:

- a tuple of labels: names were transcribed in the reported order;
- an empty tuple: the source reports a confirmed blank side;
- `None`: that side was unreadable or not established.

The caller must choose face order and traversal direction. The code does not sort the names or infer missing labels.

## Provenance and limits

The table is attributed to the README's author and its photo-based transcription; it is not independently verified against the original photographs in this repository. The source reports the clearest order for offsets −6 through +5 and lower confidence for the order within +6 through +10. The source's five `+30′` city annotations are preserved separately as `HALF_HOUR_MARKED_LABELS_2017` so they are not silently treated as part of a city's spelling or label length. See the [source section](https://github.com/zeyeteam-debug/kryptos-k4-eliminations#11-weltzeituhr-alexanderplatz-face-transcription-2017-state-and-the-1990-problem).

Most importantly, the clock was renovated in 1997, after Kryptos was dedicated in 1990. The source notes changes to city names and zone assignments, including Leningrad/St. Petersburg, Alma Ata/Almaty, Bratislava/Pressburg, and cities added after renovation. Thus the data is a candidate source for experiments, not evidence of what Sanborn could have used in 1990. The grouped `-12/-11/-10/-9` entry is intentionally left unknown rather than assigning unreadable labels to individual faces.

The source repository reports null results for several tests using city names as keyed alphabets/keys. This PR does not independently reproduce those searches, import their negative claims into the project's hypothesis ledger, or claim to eliminate a clock-based cipher.

## How to use it

`face_labels(offset, side)` returns the labels in the source's stated order. `ordered_face_labels(offsets, side)` flattens a caller-supplied offset order, preserving blanks and returning `None` if any requested face is unknown. The resulting labels can be passed to the existing `kryptos.k4.open5_frontier.keyed_lookup_streams` helper to generate explicitly named first/last/length streams.

Example:

```python
from kryptos.k4.open5_frontier import keyed_lookup_streams
from kryptos.k4.world_clock_faces_2017 import ordered_face_labels

labels = ordered_face_labels(("+1", "+2", "+3"), "top")
if labels is not None:
    streams = keyed_lookup_streams(labels, length=97)
```

This is candidate generation only. The stream transform, starting face, direction, and choice of top/bottom still need independent justification; a crib-consistent result should be checked against planted controls and a shuffled null before promotion.

## New historical-source findings

The follow-up research is recorded in [K4_WORLD_CLOCK_HISTORICAL_SOURCES.md](K4_WORLD_CLOCK_HISTORICAL_SOURCES.md). The most useful leads are:

- A freely accessible 2,329 × 3,054 photograph dated 31 January 1970, attributed to Jörg Blobelt and licensed CC BY-SA 4.0: [Wikimedia Commons original and metadata](https://commons.wikimedia.org/wiki/File:19700131040NR_Berlin_Weltzeituhr_am_Alexanderplatz.jpg).
- A high-resolution Erhard Pansegrau catalogue image dated approximately 1986/1990: [AKG Images record](https://www.akg-images.de/asset/668482/Berlin%2C-Weltzeituhr--Foto-um-1986). Access and reuse may require licensing.
- A photo archive from the Verein für die Geschichte Berlins lists several earlier full-frame views, including a 1980s slide (Mi-A 245) and a 1976 full-frame view (Mi-A I615): [digital photo archive](https://www.diegeschichteberlins.de/geschichteberlins/datenbanken/digitales-fotoarchiv.html?start=650).
- The official history states that the clock originally had 80 city names, while its current description lists 146. This does not reconcile with the frequently reported “20 places added in 1997” summary; do not reconstruct the original list by subtracting a guessed set of additions.

These are archival leads, not a completed transcription. No city name has been added to the source data based only on a blurry image or an inferred DDR-era list. The physical clock's middle hour dial rotates; do not assume the city-name plates themselves rotate through a reading position without a source supporting that mechanism.

## Follow-up work

- Inspect the 1970 Commons image at full resolution and transcribe only directly readable labels.
- Request research access to the near-1990 Pansegrau image and the high-resolution 1980s / 1976 archive views.
- Find an original 1969 label schedule or 1997 restoration/change list to resolve the original-80 versus current-146 count discrepancy.
- Recover the complete physical face order and relevant orientation from source-backed geometry.
- Only then run explicit per-letter lookup streams with declared traversal, exact crib constraints and planted controls.
- Separately reproduce and audit the other bounded elimination claims in issue #244 before treating them as coverage in this repository. See [K4_EXTERNAL_ELIMINATION_AUDIT.md](K4_EXTERNAL_ELIMINATION_AUDIT.md).
