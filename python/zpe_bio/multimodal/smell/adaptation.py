from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptationParams:
    """4-bit half-life + 4-bit floor adaptation model parameters."""

    half_life: int
    floor: int

    def __post_init__(self) -> None:
        if not 0 <= int(self.half_life) <= 15:
            raise ValueError("half_life must be in [0, 15]")
        if not 0 <= int(self.floor) <= 15:
            raise ValueError("floor must be in [0, 15]")


def encode_adaptation_params(params: AdaptationParams) -> int:
    return ((int(params.half_life) & 0xF) << 4) | (int(params.floor) & 0xF)


def decode_adaptation_params(code: int) -> AdaptationParams:
    value = int(code) & 0xFF
    half_life = (value >> 4) & 0xF
    floor = value & 0xF
    return AdaptationParams(half_life=half_life, floor=floor)


def apply_adaptation(initial_intensity: int, sniff_index: int, params: AdaptationParams) -> int:
    """Compute adapted intensity for sniff index using a simple half-life decay model."""
    if not 0 <= int(initial_intensity) <= 7:
        raise ValueError("initial_intensity must be in [0, 7]")
    if int(sniff_index) < 0:
        raise ValueError("sniff_index must be >= 0")
    if int(sniff_index) == 0:
        return int(initial_intensity)

    hl = max(1, int(params.half_life))
    floor_0_7 = min(7, int(round((int(params.floor) / 15.0) * 7.0)))

    delta = max(0.0, float(initial_intensity) - float(floor_0_7))
    decay = 0.5 ** (float(sniff_index) / float(hl))
    adapted = float(floor_0_7) + delta * decay
    return max(0, min(7, int(round(adapted))))
