# Historical World Clock Photo Leads (Pre-1997)

> 🧭 [kryptos](../../README.md) <!-- nav -->

**Status:** sourced research leads; no complete face transcription or cipher result established.

## Why this matters

The existing `world_clock_faces_2017.py` transcription is explicitly provisional: it was assembled from later photographs and cannot establish the clock's 1990 city labels, time-zone assignments, physical orientation, or ring order. These earlier photo sources provide a path toward a historically appropriate model for testing the K4 “BERLIN CLOCK” clue.

## Sources

1. **Thomas Gade, Alexanderplatz photographs from 1990**  
   [Berlin. Alexanderplatz. 1990 — photo archive](https://medienarchiv.com/Berlin/Berlin-Mitte/Alexanderplatz/Alexanderplatz03.htm)  
   The archive indexes several photographs explicitly captioned as views at the Weltzeituhr, including June 1990 images. One view shows a substantial portion of the label cylinder and numbered hour bands. The images are useful visual evidence for the pre-renovation state, but the versions currently indexed here are too small and perspective-distorted to claim a complete, reliable transcription. Inspect individual full-resolution originals before entering labels into a machine-readable table.

2. **Jörg Blobelt, 31 January 1970**  
   [Wikimedia Commons: Urania-Weltzeituhr am Alexanderplatz](https://commons.wikimedia.org/wiki/File:19700131040NR_Berlin_Weltzeituhr_am_Alexanderplatz.jpg)  
   A dated early photograph of the clock, with the photographer, date, and location recorded on the file page. It provides an independent early-era reference, though the view is not a complete orthographic survey of all 24 sides.

3. **Contemporary reporting on the 1997 restoration**  
   [Berliner Zeitung, 12 December 1997: “Frisch poliert: Die Weltzeituhr dreht sich bald”](https://www.berliner-zeitung.de/article/20-staedtenamen-wurden-bei-der-restaurierung-ergaenzt-frisch-poliert-die-weltzeituhr-dreht-sich-bald-7079)  
   The report says 20 city names were added during restoration and that some city-to-time-zone assignments changed. This independently reinforces that a modern transcription must not be assumed to match the 1990 clock.

4. **Additional pre-renovation photo lead**  
   [AKG Images: Weltzeituhr, photographed circa 1986/1990](https://www.akg-images.de/asset/668482/Berlin%2C-Weltzeituhr--Foto-um-1986)  
   The catalog describes a photograph of the clock by Erhard Pansegrau. The catalog lists high-resolution image versions, but access/licensing may be restricted.

5. **Seitz / ullstein bild, 1996**  
   [Getty Images: “Weltzeituhr- 1996”](https://www.gettyimages.com.mx/detail/fotograf%C3%ADa-de-noticias/weltzeituhr-1996-fotograf%C3%ADa-de-noticias/545062933)  
   The catalog dates the image to 1996, before the restoration. It is another potential pre-restoration visual reference; licensing applies and the catalog page alone does not establish that every plate is readable.

6. **Lothar M. Peter / Süddeutsche Zeitung Photo, circa 1990**  
   [Bridgeman Images: “The World Clock in Berlin, 1990”](https://www.bridgemanimages.com/en/peter/the-world-clock-in-berlin-1990-photo/photograph/asset/11782728)  
   The catalog identifies the photographer, approximate shooting date, and a largest listed format of 5382 × 8224 pixels. This is a promising high-resolution pre-restoration lead for inspecting the cylinder's labels and local adjacency. The listed high-resolution image is offered under licensing terms; this entry records the source lead, not a locally copied image or a completed transcription.

## What can and cannot be inferred

- **Supported:** pre-1997 photographic records exist; the 1997 restoration changed city labels and time-zone assignments; at least one 1990 view exposes several adjacent sectors.
- **Not yet supported:** a complete pre-1997 list of city labels, the exact order of all 24 plates, the orientation of the ring relative to true north at a specific time, or the relation between that orientation and Kryptos's compass rose.
- A perspective photograph can help read labels and their adjacency, but by itself does not reliably establish a true-north bearing. That requires a known camera/viewpoint or other surveyed reference.
- Do not infer missing names from the post-1997 transcription. Keep unreadable labels unknown, and keep the photographed plate order separate from any assumed clockwise/counterclockwise traversal.

## Next reproducible steps

1. Obtain the largest available original files for the 1990 and circa-1986/1990 photographs.
2. Transcribe only legible labels, retaining image URL, image region, confidence, and whether a reading is direct or inferred.
3. Cross-check labels against the 1970 photograph and contemporaneous sources; flag additions/renamings known from the 1997 restoration.
4. Reconstruct face adjacency from overlapping views before assigning UTC offsets or compass azimuths.
5. Once a defensible 1990 sequence exists, test predeclared clock-derived streams against all four confirmed K4 cribs together (EAST, NORTHEAST, BERLIN, CLOCK) and compare against shuffled controls. Do not select a different rotation for each crib.

## Existing project context

See [K4 World Clock Face Transcription](K4_WORLD_CLOCK_FACE_TRANSCRIPTION.md), which documents the limitations of the 2017 snapshot, and [active K4 research state](K4_ACTIVE_RESEARCH.md), which lists historical World Clock photos and orientation as open sourcing work.
