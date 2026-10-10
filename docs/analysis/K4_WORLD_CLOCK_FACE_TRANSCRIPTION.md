# World Clock Face Transcription (2017 Snapshot)

**Status:** provisional ordered input data; not a confirmed 1990 transcription and not a K4 result.

## Why this exists

Issue [#244](https://github.com/nitsuah/kryptos/issues/244) links to Thanos Zekios's independent [K4 eliminations repository](https://github.com/zeyeteam-debug/kryptos-k4-eliminations). Its README includes a per-face, top-to-bottom transcription of the Alexanderplatz Weltzeituhr from user-submitted photos (mostly 2017, with some later screenshots). This is more useful for testing per-letter clock lookup ideas than the existing flat list of confirmed city names, because the ordering of labels on each side of a face is preserved.

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

## Follow-up work

- Find a readable pre-1997 face transcription or original photographs, especially for old city names and zone assignments.
- Recover the complete physical face order and the clock's relevant rotation/orientation at the hypothesized time.
- Only then run explicit per-letter lookup streams with a declared traversal and exact crib constraints.
- Separately reproduce and audit the other bounded elimination claims in issue #244 before treating them as coverage in this repository.
