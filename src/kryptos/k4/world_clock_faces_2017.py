"""Provisional 2017 World Clock face transcription for lookup-key experiments.

Transcribed by Thanos Zekios from user-submitted photos (2017) and later
screenshots; incorporated with attribution from
https://github.com/zeyeteam-debug/kryptos-k4-eliminations#11-weltzeituhr-alexanderplatz-face-transcription-2017-state-and-the-1990-problem

This is not a primary-source transcription and must not be treated as the
clock's 1990 state. Labels preserve the reported top-to-bottom order on each
side; spellings are normalized to ASCII for reproducible candidate generation.
None means unreadable/unknown, while an empty tuple means the source reports
a confirmed blank side. These states must not be conflated.
"""

from __future__ import annotations

from collections.abc import Iterable, Literal

FaceSide = Literal["top", "bottom"]

# The -12/-11/-10/-9 entry is intentionally grouped: the cited transcription
# could not reliably distinguish those individual faces.
WORLD_CLOCK_FACES_2017: dict[str, dict[FaceSide, tuple[str, ...] | None]] = {
    "-12/-11/-10/-9": {"top": None, "bottom": None},
    "-8": {"top": ("VANCOUVER", "DAWSON", "SAN FRANCISCO", "LOS ANGELES"), "bottom": ()},
    "-7": {"top": ("EDMONTON", "DENVER"), "bottom": ()},
    "-6": {"top": ("NEW ORLEANS", "MEXIKO-STADT"), "bottom": ("GUATEMALA-STADT", "MANAGUA", "GALAPAGOS I.")},
    "-5": {"top": ("MONTREAL", "WASHINGTON", "NEW YORK", "HAVANNA"), "bottom": ("PANAMA", "SANTAFE DE BOGOTA", "QUITO", "LIMA")},
    "-4": {"top": ("HALIFAX",), "bottom": ("CARACAS", "LA PAZ", "ASUNCION", "SANTIAGO DE CHILE")},
    "-3": {"top": ("WESTGROENLAND",), "bottom": ("BRASILIA", "RIO DE JANEIRO", "SAO PAULO", "MONTEVIDEO", "BUENOS AIRES")},
    "-2": {"top": ("OSTGROENLAND",), "bottom": None},
    "-1": {"top": ("AZOREN",), "bottom": ("KAP VERDE",)},
    "0": {"top": ("REYKJAVIK", "DUBLIN", "LONDON", "LISSABON", "MADEIRA", "BISSAU"), "bottom": ("CASABLANCA", "CONAKRY", "DAKAR", "BAMAKO", "ACCRA")},
    "+1": {"top": ("AMSTERDAM", "BERLIN", "BRUESSEL", "BUDAPEST", "MADRID", "PARIS", "PRAG", "STOCKHOLM", "WARSCHAU"), "bottom": ("OSLO", "KOPENHAGEN", "WIEN", "BERN", "PRESSBURG", "BELGRAD", "ROM", "TUNIS", "KINSHASA")},
    "+2": {"top": ("HELSINKI", "RIGA", "TALLINN", "WILNA", "MINSK", "KIEW", "BUKAREST", "SOFIA", "NIKOSIA"), "bottom": ("ANKARA", "ISTANBUL", "ATHEN", "TEL AVIV", "JERUSALEM", "BEIRUT", "DAMASKUS", "KAIRO", "KAPSTADT")},
    "+3": {"top": ("MURMANSK", "ST PETERSBURG", "MOSKAU"), "bottom": ("TEHERAN", "BAGDAD", "ADEN", "SANAA", "ADDIS ABEBA", "MOGADISCHU", "DARESSALAM", "ANTANANARIVO", "KUWAIT")},
    "+4": {"top": ("NISCHNIJ NOWGOROD", "WOLGOGRAD", "BAKU", "TIFLIS", "ERIWAN"), "bottom": ("KABUL", "MAURITIUS")},
    "+5": {"top": ("JEKATERINBURG", "ASCHGABAT", "BISCHKEK", "DUSCHANBE"), "bottom": ("NEW DELHI", "KARACHI", "COLOMBO")},
    "+6": {"top": ("OMSK", "ALMATY", "TASCHKENT", "NOWOSIBIRSK"), "bottom": ("RANGUN", "DHAKA")},
    "+7": {"top": ("KRASNOJARSK",), "bottom": ("HANOI", "BANGKOK", "PHNOM PENH", "JAKARTA")},
    "+8": {"top": ("IRKUTSK", "ULAN-BATOR"), "bottom": ("PEKING", "SHANGHAI", "MANILA", "PERTH", "HONGKONG", "KUALA LUMPUR", "SINGAPUR")},
    "+9": {"top": ("JAKUTSK",), "bottom": ("PJOENGJANG", "TOKYO", "SEOUL")},
    "+10": {"top": ("CHABAROWSK", "WLADIWOSTOK"), "bottom": ("SYDNEY", "CANBERRA", "MELBOURNE")},
    "+11": {"top": ("MAGADAN", "SACHALIN"), "bottom": ()},
    "+12": {"top": ("KAMTSCHATKA",), "bottom": ("DATUMSGRENZE", "WELLINGTON")},
}

TRANSCRIPTION_SOURCE = (
    "https://github.com/zeyeteam-debug/kryptos-k4-eliminations"
    "#11-weltzeituhr-alexanderplatz-face-transcription-2017-state-and-the-1990-problem"
)


def face_labels(utc_offset: str, side: FaceSide) -> tuple[str, ...] | None:
    """Return labels in reported engraving order; None means the face is unknown."""
    if side not in ("top", "bottom"):
        raise ValueError("side must be 'top' or 'bottom'")
    try:
        return WORLD_CLOCK_FACES_2017[utc_offset][side]
    except KeyError as exc:
        raise ValueError(f"unknown transcribed UTC offset: {utc_offset}") from exc


def ordered_face_labels(
    offsets: Iterable[str],
    side: FaceSide,
) -> list[str] | None:
    """Flatten labels in caller-supplied face order, preserving unknown-vs-blank.

    Returns None if any requested face side is unreadable. Confirmed blank faces
    contribute no labels. The caller, not this function, chooses direction/order.
    """
    result: list[str] = []
    for offset in offsets:
        labels = face_labels(offset, side)
        if labels is None:
            return None
        result.extend(labels)
    return result


__all__ = [
    "TRANSCRIPTION_SOURCE",
    "WORLD_CLOCK_FACES_2017",
    "face_labels",
    "ordered_face_labels",
]
