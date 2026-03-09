from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .types import (
    BodyRegion,
    DrawDir,
    MoveTo,
    ReceptorType,
    TouchStroke,
)


@dataclass(frozen=True)
class ReceptorCharacteristics:
    name: str
    supports_direction: bool
    supports_pressure: bool
    supports_vibration: bool
    notes: str


RECEPTOR_MODEL: Dict[ReceptorType, ReceptorCharacteristics] = {
    ReceptorType.SA_I: ReceptorCharacteristics(
        name="Merkel (SA-I)",
        supports_direction=True,
        supports_pressure=True,
        supports_vibration=False,
        notes="Primary edge/pressure channel for contour following.",
    ),
    ReceptorType.RA_I: ReceptorCharacteristics(
        name="Meissner (RA-I)",
        supports_direction=True,
        supports_pressure=True,
        supports_vibration=False,
        notes="Motion/slip-sensitive, useful for dynamic tracing.",
    ),
    ReceptorType.RA_II: ReceptorCharacteristics(
        name="Pacinian (RA-II)",
        supports_direction=False,
        supports_pressure=False,
        supports_vibration=True,
        notes="Vibrotactile texture channel (40-800 Hz).",
    ),
    ReceptorType.SA_II: ReceptorCharacteristics(
        name="Ruffini (SA-II)",
        supports_direction=True,
        supports_pressure=True,
        supports_vibration=False,
        notes="Skin stretch/force direction channel.",
    ),
}


def get_receptor_characteristics(receptor: ReceptorType) -> ReceptorCharacteristics:
    return RECEPTOR_MODEL[receptor]


def build_contour_following_trace(
    region: BodyRegion = BodyRegion.PALM_CENTER,
    receptor: ReceptorType = ReceptorType.SA_I,
    start: Tuple[int, int] = (0, 0),
    loops: int = 1,
) -> TouchStroke:
    """Synthetic contour-following path using all 8 directions."""
    direction_loop = [0, 1, 2, 3, 4, 5, 6, 7]
    directions = direction_loop * max(1, loops)
    commands = [MoveTo(*start)] + [DrawDir(direction) for direction in directions]
    pressure_profile = [4 for _ in directions]
    return TouchStroke(
        commands=commands,
        receptor=receptor,
        region=region,
        pressure_profile=pressure_profile,
    )


def build_press_release_trace(
    region: BodyRegion = BodyRegion.INDEX_TIP,
    receptor: ReceptorType = ReceptorType.SA_I,
    peak_pressure: int = 7,
    ascent_steps: int = 4,
) -> TouchStroke:
    """Synthetic press/release path encoded as Up then Down direction steps."""
    ascent_steps = max(1, ascent_steps)
    ascent_pressures = _linear_levels(0, peak_pressure, ascent_steps)
    descent_pressures = _linear_levels(peak_pressure, 0, ascent_steps)
    directions = [2] * ascent_steps + [6] * ascent_steps
    pressures = ascent_pressures + descent_pressures
    commands = [MoveTo(0, 0)] + [DrawDir(direction) for direction in directions]
    return TouchStroke(
        commands=commands,
        receptor=receptor,
        region=region,
        pressure_profile=pressures,
    )


def _linear_levels(start: int, end: int, steps: int) -> List[int]:
    if steps == 1:
        return [int(round(end))]
    levels: List[int] = []
    for idx in range(steps):
        t = idx / (steps - 1)
        value = int(round(start + (end - start) * t))
        levels.append(max(0, min(7, value)))
    return levels


def receptor_ids() -> List[int]:
    return [int(receptor.value) for receptor in ReceptorType]
