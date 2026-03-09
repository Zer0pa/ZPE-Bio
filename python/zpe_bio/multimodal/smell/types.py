from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List

from ..diagram.quantize import DrawDir, MoveTo


def _validate_uint3(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be int, got {type(value).__name__}")
    if not 0 <= value <= 7:
        raise ValueError(f"{name} must be in [0, 7], got {value}")


class OdorCategory(IntEnum):
    FLORAL = 0
    FRUITY = 1
    SPICY_HERBAL = 2
    WOODY_EARTHY = 3
    CHEMICAL_SOLVENT = 4
    MUSKY_ANIMAL = 5
    MINTY_CAMPHOR = 6
    PUTRID_DECAY = 7


class TemporalPhase(IntEnum):
    ONSET = 0
    PEAK = 1
    PLATEAU = 2
    DECAY = 3


class SmellZLevel(IntEnum):
    INSTANT = 0
    ADAPTATION = 1
    EPISODIC = 2


@dataclass(frozen=True)
class OlfactoryEvent:
    """A single odor perception at one temporal moment."""

    category: OdorCategory
    pleasantness: int
    intensity: int
    direction: int
    temporal_phase: TemporalPhase = TemporalPhase.PEAK

    def __post_init__(self) -> None:
        if not isinstance(self.category, OdorCategory):
            raise TypeError("category must be an OdorCategory")
        _validate_uint3("pleasantness", self.pleasantness)
        _validate_uint3("intensity", self.intensity)
        _validate_uint3("direction", self.direction)
        if not isinstance(self.temporal_phase, TemporalPhase):
            raise TypeError("temporal_phase must be a TemporalPhase")


@dataclass
class OdorStroke:
    """Sequence of olfactory events forming a sniff-cycle trajectory."""

    commands: List[MoveTo | DrawDir]
    category: OdorCategory = OdorCategory.FLORAL
    pleasantness_start: int = 4
    intensity_start: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.category, OdorCategory):
            raise TypeError("category must be an OdorCategory")
        _validate_uint3("pleasantness_start", self.pleasantness_start)
        _validate_uint3("intensity_start", self.intensity_start)
        if not isinstance(self.commands, list):
            raise TypeError("commands must be a list")
        if not self.commands:
            raise ValueError("commands must contain at least one MoveTo")
        if not isinstance(self.commands[0], MoveTo):
            raise ValueError("commands must start with MoveTo")
        for cmd in self.commands[1:]:
            if not isinstance(cmd, DrawDir):
                raise TypeError(f"unsupported command type: {type(cmd).__name__}")
