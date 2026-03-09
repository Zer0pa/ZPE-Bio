from __future__ import annotations

from typing import List

from .symmetry import apply_symmetry
from .types import (
    DrawDir,
    DirectionProfile,
    FormClass,
    MentalStroke,
    MoveTo,
    SymmetryOrder,
    direction_modulus,
)


def _clamp_u3(value: int) -> int:
    return max(0, min(7, int(value)))


def _stroke_from_dirs(
    start: tuple[int, int],
    directions: List[int],
    form_class: FormClass,
    symmetry: SymmetryOrder,
    spatial_frequency: int,
    drift_speed: int = 1,
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> MentalStroke:
    modulus = direction_modulus(direction_profile)
    commands = [MoveTo(start[0], start[1])] + [
        DrawDir(d % modulus, profile=direction_profile) for d in directions
    ]
    return MentalStroke(
        commands=commands,
        form_class=form_class,
        symmetry=symmetry,
        direction_profile=direction_profile,
        spatial_frequency=_clamp_u3(spatial_frequency),
        drift_speed=max(0, min(3, drift_speed)),
    )


def generate_tunnel(
    center: tuple[int, int],
    radius: int,
    symmetry: SymmetryOrder = SymmetryOrder.D4,
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[MentalStroke]:
    """Generate radial expansion/contraction strokes for tunnel/funnel patterns."""

    stride = max(1, radius // 8)
    base = [0] * stride + [4] * stride
    copies = apply_symmetry(base, symmetry, profile=direction_profile)
    spatial_frequency = _clamp_u3(radius // 8)
    return [
        _stroke_from_dirs(
            start=center,
            directions=dirs,
            form_class=FormClass.TUNNEL,
            symmetry=symmetry,
            spatial_frequency=spatial_frequency,
            direction_profile=direction_profile,
        )
        for dirs in copies
    ]


def generate_spiral(
    center: tuple[int, int],
    turns: int,
    chirality: int = 1,
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[MentalStroke]:
    """Generate a rotating trajectory for spiral form constants."""

    modulus = direction_modulus(direction_profile)
    steps = max(modulus, turns * modulus)
    sign = 1 if chirality >= 0 else -1
    directions = [((i * sign) % modulus) for i in range(steps)]
    spatial_frequency = _clamp_u3(turns)
    return [
        _stroke_from_dirs(
            start=center,
            directions=directions,
            form_class=FormClass.SPIRAL,
            symmetry=SymmetryOrder.D4,
            spatial_frequency=spatial_frequency,
            direction_profile=direction_profile,
        )
    ]


def generate_lattice(
    origin: tuple[int, int],
    spacing: int,
    rows: int,
    cols: int,
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[MentalStroke]:
    """Generate grid-like trajectories for lattice/checkerboard constants."""

    row_steps = max(1, cols - 1) * max(1, spacing)
    col_steps = max(1, rows - 1) * max(1, spacing)

    directions: List[int] = []
    # Horizontal scan pattern with row transitions.
    for r in range(max(1, rows)):
        if r % 2 == 0:
            directions.extend([0] * row_steps)
        else:
            directions.extend([4] * row_steps)
        if r != rows - 1:
            directions.extend([6] * max(1, spacing))

    # Add vertical pass to reinforce cross-hatch structure.
    directions.extend([2] * col_steps)
    directions.extend([6] * col_steps)

    spatial_frequency = _clamp_u3(max(1, spacing))
    return [
        _stroke_from_dirs(
            start=origin,
            directions=directions,
            form_class=FormClass.LATTICE,
            symmetry=SymmetryOrder.D2,
            spatial_frequency=spatial_frequency,
            direction_profile=direction_profile,
        )
    ]


def generate_cobweb(
    center: tuple[int, int],
    branches: int,
    depth: int,
    direction_profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[MentalStroke]:
    """Generate branching filigree trajectories for cobweb-like constants."""

    branch_count = max(1, branches)
    depth_steps = max(1, depth)
    modulus = direction_modulus(direction_profile)
    spatial_frequency = _clamp_u3(depth_steps)
    strokes: List[MentalStroke] = []

    for b in range(branch_count):
        primary = (b * modulus) // branch_count
        split_left = (primary - 1) % modulus
        split_right = (primary + 1) % modulus
        return_dir = (primary + (modulus // 2)) % modulus

        dirs = [primary] * depth_steps
        dirs.extend([split_left] * max(1, depth_steps // 2))
        dirs.extend([split_right] * max(1, depth_steps // 2))
        dirs.extend([return_dir] * max(1, depth_steps // 2))

        strokes.append(
            _stroke_from_dirs(
                start=center,
                directions=dirs,
                form_class=FormClass.COBWEB,
                symmetry=SymmetryOrder.D4,
                spatial_frequency=spatial_frequency,
                direction_profile=direction_profile,
            )
        )

    return strokes
