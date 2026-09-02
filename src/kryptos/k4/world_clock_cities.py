"""World Clock (Weltzeituhr, Alexanderplatz) city list as a keyed-alphabet source -- Frontier Phase 7.

Same category of research as P11/P19's keyword expansion: an untested
external word source tried as a K4 keyed-alphabet seed, rather than a new
cipher mechanism.

Sourced facts, cross-checked across two independent-language Wikipedia
articles (English "World Clock (Alexanderplatz)", checked 2026-09-01;
German "Weltzeituhr (Alexanderplatz)", checked 2026-09-02, which quotes
its own primary text: "Sie enthaelt auf ihrer metallenen Rotunde die
Namen von 146 Orten sowie einen zusaetzlichen Eintrag zur Datumsgrenze"
-- 146 city names plus one additional, distinct
International Date Line entry): the clock's 24-sided rotating cylinder
displays **146 city names plus 1 IDL marker (147 total plate entries)**
across its 24 time-zone segments -- one segment per column of this
project's own 24-column grid, a genuine structural echo worth testing.
This resolves an earlier internal disagreement in this project's own
research (an English-secondary-source pass had recorded 148) in favor of
the two independent-language primary sources, which agree with each
other exactly.

A complete, authoritative city-by-city list is **not available from any
text source** checked -- neither Wikipedia edition, nor any other page
fetched, reproduces the full name list as text. But the clock is a public
sculpture, permanently photographed from every angle: this session read
the engraved plates directly off seven Wikimedia Commons photographs
(``Weltzeituhr_Detail_Alexanderplatz.jpg``, ``Weltzeituhr.jpg``,
``Die_Urania-Weltzeituhr_am_Alexanderplatz.jpg``,
``DSC_3226_Urania-Weltzeituhr_Berlin_I.jpg``,
``Weltzeituhr,_Berlin_(15910006062).jpg``,
``2009-04-07_Berlin_506.jpg``, and ``2009-04-07_Berlin_508.jpg`` -- all
public domain / CC, checked 2026-09-02), transcribing every legible plate
rather than relying on a secondary description. Where two photos covered
the same segment, both were read and cross-checked (this caught and
corrected one misread on a first pass -- see the Middle East/North Africa
segment below). This covers roughly 20 of the 24 segments (119
individually confirmed names, counting both the photographed set and a
handful of pre-/post-1997 name variants sourced from Wikipedia text
rather than a plate) -- still not the complete 146, but a large,
directly-verified jump from the 9 names available from text sources
alone. The remaining ~4 segments (Japan/Korea, Australia/NZ, and the
Pacific/Hawaii zones) were not found legibly photographed in this pass.
If a complete, sourced city list
is ever obtained, extend ``CONFIRMED_CITIES`` -- do not invent entries
for the remaining segments.
"""

from __future__ import annotations

from typing import Any

from .advisory_keywords import build_keyed_alphabet

# Read directly off the sculpture's own engraved plates via five
# Wikimedia Commons photographs (checked 2026-09-02, see module
# docstring) -- not a secondary source's summary. Names are grouped by
# the photographed segment they appear in (each segment covers one hour
# of the clock's 24 divisions). A few plate names combine multiple
# spellings of the same city where the pre-/post-1997-restoration label
# differs (tested separately, since which one the cipher would use, if
# either, is unknown).
CONFIRMED_CITIES: list[str] = [
    # -- Segment: HALIFAX
    "HALIFAX",
    # -- Segment: WESTGROENLAND / OSTGROENLAND / AZOREN
    "WESTGROENLAND",
    "OSTGROENLAND",
    "AZOREN",
    # -- Segment: REYKJAVIK / DUBLIN / LONDON / LISSABON / MADEIRA / BISSAU
    "REYKJAVIK",
    "DUBLIN",
    "LONDON",
    "LISSABON",
    "MADEIRA",
    "BISSAU",
    # -- Segment: AMSTERDAM / BERLIN / BRUESSEL / BUDAPEST / MADRID / PARIS / PRAG / STOCKHOLM / WARSCHAU
    "AMSTERDAM",
    "BERLIN",
    "BRUESSEL",
    "BUDAPEST",
    "MADRID",
    "PARIS",
    "PRAG",
    "STOCKHOLM",
    "WARSCHAU",
    # -- Segment: HELSINKI / RIGA / TALLINN / WILNA / MINSK / KIEW / BUKAREST / SOFIA / NIKOSIA
    "HELSINKI",
    "RIGA",
    "TALLINN",
    "WILNA",
    "MINSK",
    "KIEW",  # the clock's own (German) engraving; KYIV tested separately below
    "BUKAREST",
    "SOFIA",
    "NIKOSIA",
    # -- Segment: MURMANSK / ST. PETERSBURG / MOSKAU
    "MURMANSK",
    "SAINTPETERSBURG",
    "MOSKAU",
    # -- Segment: NISCHNIJ NOWGOROD / WOLGOGRAD / BAKU / TIFLIS / ERIWAN
    "NISCHNIJNOWGOROD",
    "WOLGOGRAD",
    "BAKU",
    "TIFLIS",
    "ERIWAN",
    # -- Segment: JEKATERINBURG / ASCHGABAT / BISCHKEK / DUSCHANBE
    "JEKATERINBURG",
    "ASCHGABAT",
    "BISCHKEK",
    "DUSCHANBE",
    # -- Segment: OMSK / ALMATY / TASCHKENT / NOWOSIBIRSK / KRASNOJARSK
    "OMSK",
    "ALMATY",
    "TASCHKENT",
    "NOWOSIBIRSK",
    "KRASNOJARSK",
    # -- Segment: ANKARA / ISTANBUL / ATHEN / TEL AVIV / JERUSALEM / BEIRUT / DAMASKUS
    # (read from a second, sharper photo after an initial pass misread this
    # segment; TELAVIV/JERUSALEM already listed above from Wikipedia text,
    # confirmed here as plate-engraved too)
    "ANKARA",
    "ISTANBUL",
    "ATHEN",
    "BEIRUT",
    "DAMASKUS",
    # -- Segment: TEHERAN +30' / BAGDAD / ADEN / SANAA / ADDIS ABEBA / MOGADISCHU / DAR ES SALAAM / ANTANANARIVO
    "TEHERAN",
    "BAGDAD",
    "ADEN",
    "SANAA",
    "ADDISABEBA",
    "MOGADISCHU",
    "DARESSALAM",
    "ANTANANARIVO",
    # -- Segment: KABUL +30' / MAURITIUS
    "KABUL",
    "MAURITIUS",
    # -- Segment: NEW DELHI / KARACHI / COLOMBO / RANGUN / DHAKA
    "NEWDELHI",
    "KARACHI",
    "COLOMBO",
    "RANGUN",
    "DHAKA",
    # -- Segment: HANOI / BANGKOK / PHNOM PENH / JAKARTA
    "HANOI",
    "BANGKOK",
    "PHNOMPENH",
    "JAKARTA",
    # -- Segment: PEKING / SHANGHAI / MANILA / PERTH / HONGKONG / KUALA LUMPUR / SINGAPUR
    "PEKING",
    "SHANGHAI",
    "MANILA",
    "PERTH",
    "HONGKONG",
    "KUALALUMPUR",
    "SINGAPUR",
    # -- Segment: NOME / FAIRBANKS / ANCHORAGE
    "NOME",
    "FAIRBANKS",
    "ANCHORAGE",
    # -- Segment: VANCOUVER / DAWSON / SAN FRANCISCO / LOS ANGELES
    "VANCOUVER",
    "DAWSON",
    "SANFRANCISCO",
    "LOSANGELES",
    # -- Segment: EDMONTON / DENVER
    "EDMONTON",
    "DENVER",
    # -- Segment: NEW ORLEANS / MEXIKO-STADT
    "NEWORLEANS",
    "MEXIKOSTADT",
    # -- Southern-hemisphere plate group (same photo as the AMSTERDAM/... segment above)
    "CARACAS",
    "LAPAZ",
    "ASUNCION",
    "SANTIAGODECHILE",
    "BRASILIA",
    "RIODEJANEIRO",
    "SAOPAULO",
    "MONTEVIDEO",
    "BUENOSAIRES",
    "KAPVERDE",
    "CASABLANCA",
    "CONAKRY",
    "DAKAR",
    "BAMAKO",
    "ACCRA",
    "OSLO",
    "KOPENHAGEN",
    "WIEN",
    "BERN",
    "PRESSBURG",  # the clock's actual (German-historical) engraving for Bratislava
    "BELGRAD",
    "ROM",
    "TUNIS",
    "KINSHASA",
    # -- Not directly photographed this pass, but individually sourced from
    # Wikipedia text (English/German, checked 2026-09-01/02) rather than
    # read off a plate -- kept distinct from the photographed set above.
    "LENINGRAD",  # pre-1997 name for the SAINTPETERSBURG segment
    "ALMAATA",  # pre-1997 name for the ALMATY segment
    "KYIV",  # modern spelling; clock itself engraves KIEW (see above)
    "TELAVIV",  # added 1997 (omitted originally for political reasons)
    "CAPETOWN",  # added 1997
    "SEOUL",  # added 1997
    "JERUSALEM",  # named in German Wikipedia, distinct from TELAVIV's segment
    "BRATISLAVA",  # the city's own modern name, distinct from the engraved PRESSBURG
]

# Sourced structural counts, not fabricated details. Two independent-
# language primary sources (English and German Wikipedia) converge on
# 146 city names + 1 International Date Line marker = 147 total plate
# entries -- see module docstring. An earlier English-secondary-source
# pass in this project had recorded 148; that figure is superseded.
TOTAL_CITY_COUNT = 146
TOTAL_PLATE_ENTRIES = 147  # includes the distinct IDL marker, not itself a city
TOTAL_SEGMENTS = 24  # already this project's own grid column count

WORLD_CLOCK_KEYED_ALPHABETS: dict[str, str] = {city: build_keyed_alphabet(city) for city in CONFIRMED_CITIES}


def world_clock_rotation_offsets() -> dict[str, int]:
    """Numeric parameters derived from the sourced structural counts.

    All three reduced mod the grid's own 24 columns -- the same treatment
    already given to every other geography-derived numeric fact in
    :func:`kryptos.k4.clock_rotation.geography_priority_offsets`. Both
    ``146`` (city names only) and ``147`` (including the IDL marker) are
    tested since which one is "the" structurally meaningful count is
    itself unresolved.
    """
    return {
        "world_clock_city_count_mod24": TOTAL_CITY_COUNT % TOTAL_SEGMENTS,
        "world_clock_plate_entries_mod24": TOTAL_PLATE_ENTRIES % TOTAL_SEGMENTS,
        "world_clock_segments": TOTAL_SEGMENTS % TOTAL_SEGMENTS,  # 0, kept for provenance/completeness
    }


def run_world_clock_city_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 86400,
    max_perms_per_grid: int = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str = "K4_WORLD_CLOCK_CITIES_NULL.json",
) -> dict[str, Any]:
    """Run the 3-layer composite with World-Clock-city keyed alphabets.

    Mirrors :func:`kryptos.k4.advisory_keywords.run_advisory_keyword_sweep`
    exactly -- same composite pipeline, only the keyword source differs.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds
    return run_three_layer_composite(
        subst_alphabets=WORLD_CLOCK_KEYED_ALPHABETS,
        grid_sizes=grid_sizes or [7, 8, 10],
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        progress_cb=progress_cb,
        null_artifact_path=null_artifact_path,
        eureka_snapshot_path="K4_WORLD_CLOCK_CITIES_EUREKA.md",
    )


__all__ = [
    "CONFIRMED_CITIES",
    "TOTAL_CITY_COUNT",
    "TOTAL_PLATE_ENTRIES",
    "TOTAL_SEGMENTS",
    "WORLD_CLOCK_KEYED_ALPHABETS",
    "run_world_clock_city_sweep",
    "world_clock_rotation_offsets",
]
