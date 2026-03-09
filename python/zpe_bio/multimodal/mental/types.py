from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Union


# Eight cardinal/diagonal directions (R, UR, U, UL, L, DL, D, DR).
DIRS_8 = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)


class DirectionProfile(IntEnum):
    COMPASS_8 = 0
    D6_12 = 1


class D12(IntEnum):
    # 12-direction profile at 30-degree angular increments (clockwise on screen Y+ down).
    E = 0
    ENE = 1
    NE = 2
    NNE = 3
    N = 4
    NW = 5
    W = 6
    SW = 7
    S = 8
    SSE = 9
    SE = 10
    ESE = 11


# 12-direction profile used for exact D6 rotational symmetry (60-degree = 2-step).
DIRS_12 = (
    (1.0, 0.0),
    (0.8660254, -0.5),
    (0.5, -0.8660254),
    (0.0, -1.0),
    (-0.5, -0.8660254),
    (-0.8660254, -0.5),
    (-1.0, 0.0),
    (-0.8660254, 0.5),
    (-0.5, 0.8660254),
    (0.0, 1.0),
    (0.5, 0.8660254),
    (0.8660254, 0.5),
)

# Backward-compatible alias expected by existing imports.
DIRS = DIRS_8


def direction_modulus(profile: DirectionProfile) -> int:
    return 8 if profile == DirectionProfile.COMPASS_8 else 12


@dataclass(frozen=True)
class MoveTo:
    x: int
    y: int


@dataclass(frozen=True)
class DrawDir:
    direction: int
    profile: DirectionProfile = DirectionProfile.COMPASS_8

    def delta(self) -> tuple[float, float]:
        max_dir = direction_modulus(self.profile) - 1
        if self.direction < 0 or self.direction > max_dir:
            raise ValueError(
                f"direction must be in [0,{max_dir}] for profile {self.profile.name}, got {self.direction}"
            )
        if self.profile == DirectionProfile.COMPASS_8:
            dx, dy = DIRS_8[self.direction]
            return float(dx), float(dy)
        return DIRS_12[self.direction]


@dataclass
class StrokePath:
    commands: List[Union[MoveTo, DrawDir]]


class FormClass(IntEnum):
    TUNNEL = 0
    SPIRAL = 1
    LATTICE = 2
    COBWEB = 3


class SymmetryOrder(IntEnum):
    D1 = 0
    D2 = 1
    D4 = 2
    D6 = 3


# D6 is represented on an 8-direction lattice by nearest-angle quantization.
# This introduces bounded angular distortion relative to ideal 60-degree steps.
D6_MAX_ERROR_DEGREES = 15


@dataclass(frozen=True)
class EndogenousVisualEvent:
    """A single endogenous visual pattern specification."""

    form_class: FormClass
    symmetry: SymmetryOrder
    spatial_frequency: int
    drift_direction: int
    drift_speed: int
    contrast: float = 1.0

    def __post_init__(self) -> None:
        if not 0 <= self.spatial_frequency <= 7:
            raise ValueError(
                f"spatial_frequency must be in [0,7], got {self.spatial_frequency}"
            )
        if not 0 <= self.drift_direction <= 7:
            raise ValueError(
                f"drift_direction must be in [0,7], got {self.drift_direction}"
            )
        if not 0 <= self.drift_speed <= 3:
            raise ValueError(f"drift_speed must be in [0,3], got {self.drift_speed}")
        if not 0.0 <= self.contrast <= 1.0:
            raise ValueError(f"contrast must be in [0.0,1.0], got {self.contrast}")


@dataclass
class MentalStroke:
    """Sequence of direction commands representing a form-constant trajectory."""

    commands: List[Union[MoveTo, DrawDir]] = field(default_factory=list)
    form_class: FormClass = FormClass.TUNNEL
    symmetry: SymmetryOrder = SymmetryOrder.D4
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8
    spatial_frequency: int = 4
    drift_speed: int = 1
    frame_index: int | None = None
    delta_ms: int = 0

    def __post_init__(self) -> None:
        if self.direction_profile not in (
            DirectionProfile.COMPASS_8,
            DirectionProfile.D6_12,
        ):
            raise ValueError(f"unsupported direction_profile: {self.direction_profile}")
        if not 0 <= self.spatial_frequency <= 7:
            raise ValueError(
                f"spatial_frequency must be in [0,7], got {self.spatial_frequency}"
            )
        if not 0 <= self.drift_speed <= 3:
            raise ValueError(f"drift_speed must be in [0,3], got {self.drift_speed}")
        if self.frame_index is not None and not 0 <= self.frame_index <= 255:
            raise ValueError(f"frame_index must be in [0,255], got {self.frame_index}")
        if not 0 <= self.delta_ms <= 255:
            raise ValueError(f"delta_ms must be in [0,255], got {self.delta_ms}")
