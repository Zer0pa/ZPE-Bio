from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional, Tuple, Union

# Shared 8-direction vectors: (R, UR, U, UL, L, DL, D, DR)
DIRS: Tuple[Tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)


@dataclass(frozen=True)
class MoveTo:
    x: int
    y: int


@dataclass(frozen=True)
class DrawDir:
    direction: int

    def __post_init__(self) -> None:
        if not 0 <= self.direction <= 7:
            raise ValueError(f"direction must be in [0, 7], got {self.direction}")

    def delta(self) -> Tuple[int, int]:
        return DIRS[self.direction]


class ReceptorType(IntEnum):
    SA_I = 0
    RA_I = 1
    RA_II = 2
    SA_II = 3


class RAIIEnvelope(IntEnum):
    STEADY = 0
    ATTACK_DECAY = 1
    PULSE = 2
    BURST = 3


class BodyRegion(IntEnum):
    THUMB_TIP = 0
    INDEX_TIP = 1
    MIDDLE_TIP = 2
    RING_TIP = 3
    PINKY_TIP = 4
    PALM_THENAR = 5
    PALM_HYPOTHENAR = 6
    PALM_CENTER = 7
    DORSAL_HAND = 8
    WRIST_FOREARM = 9
    LIPS = 10
    TONGUE = 11
    FACE = 12
    TORSO = 13
    ARM_LEG = 14
    FOOT_SOLE = 15


class TouchZLevel(IntEnum):
    SURFACE = 0
    DERMAL = 1
    ANATOMICAL = 2
    PROPRIOCEPTIVE = 3


@dataclass(frozen=True)
class RAIIDescriptor:
    frequency_band: int
    amplitude: int
    envelope: int

    def __post_init__(self) -> None:
        if not 0 <= self.frequency_band <= 15:
            raise ValueError(
                f"frequency_band must be in [0, 15], got {self.frequency_band}"
            )
        if not 0 <= self.amplitude <= 15:
            raise ValueError(f"amplitude must be in [0, 15], got {self.amplitude}")
        if not 0 <= self.envelope <= 15:
            raise ValueError(f"envelope must be in [0, 15], got {self.envelope}")


@dataclass(frozen=True)
class TouchEvent:
    receptor: ReceptorType
    region: BodyRegion
    direction: int
    pressure: int
    velocity: int = 0
    vibrotactile_freq: int = 0
    temperature_delta: int = 0
    timestamp_ms: int = 0
    raii: Optional[RAIIDescriptor] = None

    def __post_init__(self) -> None:
        if not 0 <= self.direction <= 7:
            raise ValueError(f"direction must be in [0, 7], got {self.direction}")
        if not 0 <= self.pressure <= 7:
            raise ValueError(f"pressure must be in [0, 7], got {self.pressure}")
        if not 0 <= self.velocity <= 3:
            raise ValueError(f"velocity must be in [0, 3], got {self.velocity}")
        if not 0 <= self.vibrotactile_freq <= 7:
            raise ValueError(
                f"vibrotactile_freq must be in [0, 7], got {self.vibrotactile_freq}"
            )
        if not -3 <= self.temperature_delta <= 3:
            raise ValueError(
                f"temperature_delta must be in [-3, 3], got {self.temperature_delta}"
            )
        if not 0 <= self.timestamp_ms <= 4095:
            raise ValueError(f"timestamp_ms must be in [0, 4095], got {self.timestamp_ms}")
        if self.raii is not None and self.receptor != ReceptorType.RA_II:
            raise ValueError("raii descriptor is only valid for RA_II receptor events")


TouchCommand = Union[MoveTo, DrawDir]


@dataclass
class TouchStroke:
    commands: List[TouchCommand]
    receptor: ReceptorType = ReceptorType.SA_I
    region: BodyRegion = BodyRegion.INDEX_TIP
    pressure_profile: Optional[List[int]] = None

    def __post_init__(self) -> None:
        for command in self.commands:
            if not isinstance(command, (MoveTo, DrawDir)):
                raise TypeError(f"unsupported command {command!r}")

        if self.pressure_profile is None:
            self.pressure_profile = []

        for pressure in self.pressure_profile:
            if not 0 <= pressure <= 7:
                raise ValueError(f"pressure level must be in [0, 7], got {pressure}")

        if len(self.pressure_profile) > self.draw_count:
            raise ValueError(
                "pressure_profile length cannot exceed number of DrawDir commands"
            )

    @property
    def draw_count(self) -> int:
        return sum(1 for command in self.commands if isinstance(command, DrawDir))

    def directions(self) -> List[int]:
        return [command.direction for command in self.commands if isinstance(command, DrawDir)]

    def events(self) -> List[TouchEvent]:
        events: List[TouchEvent] = []
        directions = self.directions()
        for index, direction in enumerate(directions):
            pressure = self.pressure_profile[index] if index < len(self.pressure_profile) else 0
            events.append(
                TouchEvent(
                    receptor=self.receptor,
                    region=self.region,
                    direction=direction,
                    pressure=pressure,
                )
            )
        return events


def ensure_body_region(region: int | BodyRegion) -> BodyRegion:
    return region if isinstance(region, BodyRegion) else BodyRegion(region)


def ensure_receptor_type(receptor: int | ReceptorType) -> ReceptorType:
    return receptor if isinstance(receptor, ReceptorType) else ReceptorType(receptor)
