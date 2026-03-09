from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .types import BodyRegion


@dataclass(frozen=True)
class AnatomyCoordinate:
    """Coarse anatomical coordinate (x=lateral, y=cranial-caudal, z=depth band)."""

    x: int
    y: int
    z: int


# Dermatome-inspired coarse coordinate map for the 16 touch body regions.
ANATOMY_COORDINATES: Dict[BodyRegion, AnatomyCoordinate] = {
    BodyRegion.THUMB_TIP: AnatomyCoordinate(x=2, y=1, z=0),
    BodyRegion.INDEX_TIP: AnatomyCoordinate(x=3, y=1, z=0),
    BodyRegion.MIDDLE_TIP: AnatomyCoordinate(x=4, y=1, z=0),
    BodyRegion.RING_TIP: AnatomyCoordinate(x=5, y=1, z=0),
    BodyRegion.PINKY_TIP: AnatomyCoordinate(x=6, y=1, z=0),
    BodyRegion.PALM_THENAR: AnatomyCoordinate(x=3, y=2, z=1),
    BodyRegion.PALM_HYPOTHENAR: AnatomyCoordinate(x=6, y=2, z=1),
    BodyRegion.PALM_CENTER: AnatomyCoordinate(x=4, y=2, z=1),
    BodyRegion.DORSAL_HAND: AnatomyCoordinate(x=4, y=3, z=1),
    BodyRegion.WRIST_FOREARM: AnatomyCoordinate(x=4, y=4, z=2),
    BodyRegion.LIPS: AnatomyCoordinate(x=4, y=0, z=0),
    BodyRegion.TONGUE: AnatomyCoordinate(x=4, y=0, z=1),
    BodyRegion.FACE: AnatomyCoordinate(x=4, y=0, z=2),
    BodyRegion.TORSO: AnatomyCoordinate(x=4, y=5, z=2),
    BodyRegion.ARM_LEG: AnatomyCoordinate(x=4, y=6, z=2),
    BodyRegion.FOOT_SOLE: AnatomyCoordinate(x=4, y=7, z=1),
}

_COORD_TO_REGION: Dict[Tuple[int, int, int], BodyRegion] = {
    (coord.x, coord.y, coord.z): region
    for region, coord in ANATOMY_COORDINATES.items()
}


def region_to_coordinate(region: BodyRegion) -> AnatomyCoordinate:
    return ANATOMY_COORDINATES[region]


def coordinate_to_region(coord: AnatomyCoordinate) -> BodyRegion:
    key = (coord.x, coord.y, coord.z)
    if key not in _COORD_TO_REGION:
        raise ValueError(f"unknown anatomy coordinate {key}")
    return _COORD_TO_REGION[key]
