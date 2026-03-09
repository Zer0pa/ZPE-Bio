from __future__ import annotations

from typing import Iterable, Sequence

COARSE_MODE = "coarse"
FINE_MODE = "fine"

CARDINAL_TO_CODE = {
    0: 0,  # east
    2: 1,  # north
    4: 2,  # west
    6: 3,  # south
}

CODE_TO_CARDINAL = {value: key for key, value in CARDINAL_TO_CODE.items()}



def _validate_uint3_directions(directions: Sequence[int], expected_len: int = 8) -> tuple[int, ...]:
    if len(directions) != expected_len:
        raise ValueError(f"directions must contain exactly {expected_len} entries")

    normalized: list[int] = []
    for index, value in enumerate(directions):
        ivalue = int(value)
        if not 0 <= ivalue <= 7:
            raise ValueError(f"directions[{index}] must be in [0, 7], got {ivalue}")
        normalized.append(ivalue)
    return tuple(normalized)


def encode_temporal_coarse(directions: Sequence[int]) -> tuple[int, int]:
    """Pack exactly 8 cardinal directions into 16 bits (2 bytes)."""
    normalized = _validate_uint3_directions(directions)

    packed = 0
    for index, direction in enumerate(normalized):
        if direction not in CARDINAL_TO_CODE:
            raise ValueError("coarse mode supports only cardinal directions {0,2,4,6}")
        packed |= (CARDINAL_TO_CODE[direction] & 0x3) << (index * 2)

    return packed & 0xFF, (packed >> 8) & 0xFF


def decode_temporal_coarse(chunk0: int, chunk1: int) -> tuple[int, ...]:
    packed = (chunk0 & 0xFF) | ((chunk1 & 0xFF) << 8)
    return tuple(CODE_TO_CARDINAL[(packed >> (index * 2)) & 0x3] for index in range(8))


def encode_temporal_fine(directions: Sequence[int]) -> tuple[int, int, int]:
    """Pack exactly 8 directions into 24 bits (3 bytes)."""
    normalized = _validate_uint3_directions(directions)

    packed = 0
    for index, direction in enumerate(normalized):
        packed |= (direction & 0x7) << (index * 3)

    return packed & 0xFF, (packed >> 8) & 0xFF, (packed >> 16) & 0xFF


def decode_temporal_fine(chunk0: int, chunk1: int, chunk2: int) -> tuple[int, ...]:
    packed = (chunk0 & 0xFF) | ((chunk1 & 0xFF) << 8) | ((chunk2 & 0xFF) << 16)
    return tuple((packed >> (index * 3)) & 0x7 for index in range(8))


def auto_select_resolution(profile_or_directions: Iterable[int] | dict) -> str:
    """Select coarse only when an exact lossless coarse representation is possible."""
    if isinstance(profile_or_directions, dict):
        directions = profile_or_directions.get("temporal_directions", [])
    else:
        directions = list(profile_or_directions)

    normalized = _validate_uint3_directions(list(directions))
    unique = set(normalized)

    if unique.issubset(set(CARDINAL_TO_CODE.keys())) and len(unique) <= 4:
        return COARSE_MODE
    return FINE_MODE
