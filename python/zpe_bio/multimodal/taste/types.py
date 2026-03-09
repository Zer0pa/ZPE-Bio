from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List, Sequence, Tuple

from ..diagram.quantize import DrawDir, MoveTo

QUALITY_VECTOR_SIZE = 5


def _validate_uint3(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if not 0 <= value <= 7:
        raise ValueError(f"{name} must be in [0, 7], got {value}")


def validate_quality_vector(vector: Sequence[int]) -> tuple[int, ...]:
    if len(vector) != QUALITY_VECTOR_SIZE:
        raise ValueError("quality_vector must have length 5: (sweet, sour, salt, bitter, umami)")
    normalized = []
    for idx, value in enumerate(vector):
        _validate_uint3(f"quality_vector[{idx}]", int(value))
        normalized.append(int(value))
    return tuple(normalized)


class TasteQuality(IntEnum):
    SWEET = 0
    SOUR = 1
    SALT = 2
    BITTER = 3
    UMAMI = 4


class TemporalPhase(IntEnum):
    ONSET = 0
    PEAK = 1
    PLATEAU = 2
    DECAY = 3
    ONSET_EARLY = 4
    ONSET_LATE = 5
    PEAK_SUSTAIN = 6
    DECAY_LATE = 7


class DurationClass(IntEnum):
    SHORT = 0
    LONG = 1


class TasteZLevel(IntEnum):
    QUALITY = 0
    INTENSITY = 1
    TEMPORAL = 2
    FLAVOR = 3


@dataclass(frozen=True)
class TasteEvent:
    """A single gustatory perception at one temporal moment."""

    quality_vector: tuple[int, ...]
    dominant_quality: TasteQuality
    dominant_intensity: int
    direction: int
    temporal_phase: TemporalPhase = TemporalPhase.PEAK
    duration: DurationClass = DurationClass.SHORT

    def __post_init__(self) -> None:
        object.__setattr__(self, "quality_vector", validate_quality_vector(self.quality_vector))

        if not isinstance(self.dominant_quality, TasteQuality):
            raise TypeError("dominant_quality must be a TasteQuality")

        _validate_uint3("dominant_intensity", self.dominant_intensity)
        _validate_uint3("direction", self.direction)

        if not isinstance(self.temporal_phase, TemporalPhase):
            raise TypeError("temporal_phase must be a TemporalPhase")
        if not isinstance(self.duration, DurationClass):
            raise TypeError("duration must be a DurationClass")


@dataclass
class TasteStroke:
    """Sequence of taste events forming a tasting trajectory."""

    commands: List[MoveTo | DrawDir]
    dominant_quality: TasteQuality = TasteQuality.SWEET
    quality_vector: tuple[int, ...] = (0, 0, 0, 0, 0)

    def __post_init__(self) -> None:
        if not isinstance(self.dominant_quality, TasteQuality):
            raise TypeError("dominant_quality must be a TasteQuality")

        self.quality_vector = validate_quality_vector(self.quality_vector)

        if not isinstance(self.commands, list):
            raise TypeError("commands must be a list")
        if not self.commands:
            raise ValueError("commands must contain at least one MoveTo")
        if not isinstance(self.commands[0], MoveTo):
            raise ValueError("commands must start with MoveTo")
        for cmd in self.commands[1:]:
            if not isinstance(cmd, DrawDir):
                raise TypeError(f"unsupported command type: {type(cmd).__name__}")
            _validate_uint3("direction", cmd.direction)

    @property
    def draw_count(self) -> int:
        return sum(1 for cmd in self.commands if isinstance(cmd, DrawDir))

    def directions(self) -> list[int]:
        return [cmd.direction for cmd in self.commands if isinstance(cmd, DrawDir)]


def _validate_temporal_directions(directions: Sequence[int]) -> tuple[int, ...]:
    if len(directions) != 8:
        raise ValueError(f"temporal_directions must contain exactly 8 entries, got {len(directions)}")
    normalized: list[int] = []
    for idx, direction in enumerate(directions):
        _validate_uint3(f"temporal_directions[{idx}]", int(direction))
        normalized.append(int(direction))
    return tuple(normalized)


def _validate_flavor_link(flavor_link: Tuple[int, int] | None) -> Tuple[int, int] | None:
    if flavor_link is None:
        return None
    if not isinstance(flavor_link, tuple) or len(flavor_link) != 2:
        raise TypeError("flavor_link must be a tuple[int, int] or None")
    left, right = int(flavor_link[0]), int(flavor_link[1])
    _validate_uint3("flavor_link[0]", left)
    _validate_uint3("flavor_link[1]", right)
    return left, right


@dataclass(frozen=True)
class ZLayeredTasteEvent:
    """Taste event split across semantic Z-layers."""

    dominant_quality: TasteQuality
    secondary_quality: TasteQuality
    intensity: int
    intensity_direction: int
    temporal_directions: tuple[int, ...]
    duration: DurationClass = DurationClass.SHORT
    flavor_link: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.dominant_quality, TasteQuality):
            raise TypeError("dominant_quality must be a TasteQuality")
        if not isinstance(self.secondary_quality, TasteQuality):
            raise TypeError("secondary_quality must be a TasteQuality")
        _validate_uint3("intensity", self.intensity)
        _validate_uint3("intensity_direction", self.intensity_direction)
        if not isinstance(self.duration, DurationClass):
            raise TypeError("duration must be a DurationClass")
        object.__setattr__(
            self,
            "temporal_directions",
            _validate_temporal_directions(self.temporal_directions),
        )
        object.__setattr__(self, "flavor_link", _validate_flavor_link(self.flavor_link))
