from __future__ import annotations

from typing import List

from .types import DirectionProfile, SymmetryOrder, direction_modulus


def _rotation_steps(
    symmetry: SymmetryOrder, profile: DirectionProfile = DirectionProfile.COMPASS_8
) -> List[int]:
    if profile == DirectionProfile.COMPASS_8:
        if symmetry == SymmetryOrder.D1:
            return [0]
        if symmetry == SymmetryOrder.D2:
            return [0, 4]
        if symmetry == SymmetryOrder.D4:
            return [0, 2, 4, 6]
        if symmetry == SymmetryOrder.D6:
            # Legacy approximate mapping on the 8-direction lattice.
            return [0, 1, 3, 4, 5, 7]
    else:
        # Exact rotational mappings on a 12-direction (30-degree) profile.
        if symmetry == SymmetryOrder.D1:
            return [0]
        if symmetry == SymmetryOrder.D2:
            return [0, 6]
        if symmetry == SymmetryOrder.D4:
            return [0, 3, 6, 9]
        if symmetry == SymmetryOrder.D6:
            return [0, 2, 4, 6, 8, 10]
    raise ValueError(f"unsupported symmetry order/profile pair: {symmetry}/{profile}")


def _rotate_sequence(
    base_directions: List[int],
    shift: int,
    profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[int]:
    modulus = direction_modulus(profile)
    return [((d + shift) % modulus) for d in base_directions]


def apply_symmetry(
    base_directions: List[int],
    symmetry: SymmetryOrder,
    profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> List[List[int]]:
    """Apply a rotational symmetry group to a direction sequence."""

    modulus = direction_modulus(profile)
    for d in base_directions:
        if d < 0 or d >= modulus:
            raise ValueError(
                f"direction must be in [0,{modulus - 1}] for profile {profile.name}, got {d}"
            )

    steps = _rotation_steps(symmetry, profile=profile)
    return [_rotate_sequence(base_directions, shift, profile=profile) for shift in steps]


def verify_symmetry(
    directions: List[int],
    expected: SymmetryOrder,
    profile: DirectionProfile = DirectionProfile.COMPASS_8,
) -> bool:
    """Check whether concatenated directional blocks satisfy expected rotational symmetry."""

    modulus = direction_modulus(profile)
    if any((d < 0 or d >= modulus) for d in directions):
        return False

    steps = _rotation_steps(expected, profile=profile)
    copies = len(steps)
    if copies == 1:
        return True
    if len(directions) == 0 or len(directions) % copies != 0:
        return False

    block_size = len(directions) // copies
    base = directions[:block_size]
    expected_blocks = apply_symmetry(base, expected, profile=profile)

    for i in range(copies):
        candidate = directions[i * block_size : (i + 1) * block_size]
        if candidate != expected_blocks[i]:
            return False
    return True
