"""Physical geometry of the Kryptos sculpture, honestly tracked.

A typed landing spot for measurements this project needs but mostly does
not yet have -- the compass rose's bearing, the lodestone's deflection,
the tableau's reading orientation -- so that (a) future attack code has
one place to pull real numbers from once they exist, instead of a new
hardcoded guess per script, and (b) it is structurally impossible to
mistake "we haven't measured this" for "this is zero" or any other
silently-wrong default, because every field is `None` until a source says
otherwise.

Do not add a numeric value here without a `source` citation. This module
exists specifically to prevent the trap this project's own discipline
already warns against elsewhere: a plausible number quietly treated as a
fact. See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed"
section for the outreach (FOIA, Elonka Dunin) this data is waiting on.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Measurement:
    """A single physical fact: a value, or an honest admission it isn't known yet."""

    value: float | None
    unit: str
    source: str | None = None
    uncertainty: float | None = None

    @property
    def is_known(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        if not self.is_known:
            return f"unmeasured ({self.unit})"
        unc = f" ± {self.uncertainty}" if self.uncertainty is not None else ""
        return f"{self.value}{unc} {self.unit} [{self.source}]"


UNKNOWN_DEGREES = Measurement(value=None, unit="degrees")


@dataclass(frozen=True)
class CompassRoseGeometry:
    """The compass rose stone at the Kryptos site (distinct from the sculpture's own copper-screen tableau)."""

    true_bearing: Measurement = UNKNOWN_DEGREES
    secondary_estimate: Measurement = Measurement(
        value=220.0,
        unit="degrees",
        source="elonka.com/kryptos/KryptosAerial.html -- explicitly flagged 'not exact' by its own source",
        uncertainty=None,  # the source gives no error bound; treat the whole figure as indicative only
    )


@dataclass(frozen=True)
class LodestoneGeometry:
    """The lodestone co-located with the compass rose (CIA's own description)."""

    deflection: Measurement = UNKNOWN_DEGREES
    position_relative_to_compass_center: Measurement = Measurement(value=None, unit="meters")


@dataclass(frozen=True)
class TableauOrientation:
    """The copper-screen Vigenère tableau's physical reading direction."""

    reading_direction: str = "back"
    source: str = (
        "cia.gov/legacy/headquarters/kryptos-sculpture -- "
        "'In Kryptos this chart has been intentionally flipped so it can "
        "only be read from the back of the sculpture.' Checked directly, "
        "2026-09-03."
    )
    measured: bool = True  # this one really is confirmed, unlike the rest of this module


@dataclass(frozen=True)
class KryptosPhysicalGeometry:
    compass_rose: CompassRoseGeometry = CompassRoseGeometry()
    lodestone: LodestoneGeometry = LodestoneGeometry()
    tableau: TableauOrientation = TableauOrientation()


CURRENT: KryptosPhysicalGeometry = KryptosPhysicalGeometry()


def known_measurements() -> dict[str, Measurement | TableauOrientation]:
    """Every field in `CURRENT` that actually has data, keyed by dotted path."""
    result: dict[str, Any] = {}
    if CURRENT.compass_rose.true_bearing.is_known:
        result["compass_rose.true_bearing"] = CURRENT.compass_rose.true_bearing
    if CURRENT.compass_rose.secondary_estimate.is_known:
        result["compass_rose.secondary_estimate"] = CURRENT.compass_rose.secondary_estimate
    if CURRENT.lodestone.deflection.is_known:
        result["lodestone.deflection"] = CURRENT.lodestone.deflection
    if CURRENT.lodestone.position_relative_to_compass_center.is_known:
        result["lodestone.position_relative_to_compass_center"] = CURRENT.lodestone.position_relative_to_compass_center
    if CURRENT.tableau.measured:
        result["tableau.reading_direction"] = CURRENT.tableau
    return result


def unmeasured_fields() -> list[str]:
    """Every field in `CURRENT` still waiting on a real source."""
    all_fields = {
        "compass_rose.true_bearing": CURRENT.compass_rose.true_bearing.is_known,
        "compass_rose.secondary_estimate": CURRENT.compass_rose.secondary_estimate.is_known,
        "lodestone.deflection": CURRENT.lodestone.deflection.is_known,
        "lodestone.position_relative_to_compass_center": (
            CURRENT.lodestone.position_relative_to_compass_center.is_known
        ),
        "tableau.reading_direction": CURRENT.tableau.measured,
    }
    return [name for name, known in all_fields.items() if not known]


def status_report() -> str:
    """Human-readable summary -- what this project actually knows about the sculpture's geometry, vs. not."""
    known = known_measurements()
    missing = unmeasured_fields()
    lines = [f"Known ({len(known)}):"]
    for name, val in known.items():
        lines.append(f"  {name}: {val}")
    lines.append(f"Unmeasured ({len(missing)}):")
    for name in missing:
        lines.append(f"  {name}")
    return "\n".join(lines)


__all__ = [
    "CURRENT",
    "CompassRoseGeometry",
    "KryptosPhysicalGeometry",
    "LodestoneGeometry",
    "Measurement",
    "TableauOrientation",
    "known_measurements",
    "status_report",
    "unmeasured_fields",
]
