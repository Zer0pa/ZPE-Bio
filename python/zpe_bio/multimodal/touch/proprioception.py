from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence


class JointID(IntEnum):
    NECK = 0
    LEFT_SHOULDER = 1
    RIGHT_SHOULDER = 2
    LEFT_ELBOW = 3
    RIGHT_ELBOW = 4
    LEFT_WRIST = 5
    RIGHT_WRIST = 6
    LEFT_HIP = 7
    RIGHT_HIP = 8
    LEFT_KNEE = 9
    RIGHT_KNEE = 10
    LEFT_ANKLE = 11
    RIGHT_ANKLE = 12
    SPINE = 13


@dataclass(frozen=True)
class ProprioSample:
    joint: JointID
    angle_deg: float
    tension_level: int

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.angle_deg) <= 180.0:
            raise ValueError(f"angle_deg must be in [0, 180], got {self.angle_deg}")
        if not 0 <= int(self.tension_level) <= 15:
            raise ValueError(f"tension_level must be in [0, 15], got {self.tension_level}")


def quantize_joint_angle(angle_deg: float) -> int:
    if not 0.0 <= angle_deg <= 180.0:
        raise ValueError(f"angle_deg must be in [0, 180], got {angle_deg}")
    return int(round((angle_deg / 180.0) * 255.0))


def dequantize_joint_angle(angle_q: int) -> float:
    if not 0 <= angle_q <= 255:
        raise ValueError(f"angle_q must be in [0, 255], got {angle_q}")
    return (angle_q / 255.0) * 180.0


def quantize_proprio_sample(sample: ProprioSample) -> tuple[int, int, int]:
    return int(sample.joint.value), quantize_joint_angle(float(sample.angle_deg)), int(sample.tension_level)


def dequantize_proprio_sample(joint_id: int, angle_q: int, tension: int) -> ProprioSample:
    return ProprioSample(
        joint=JointID(joint_id),
        angle_deg=dequantize_joint_angle(angle_q),
        tension_level=tension,
    )


def max_angle_error(encoded: Sequence[ProprioSample], decoded: Sequence[ProprioSample]) -> float:
    if len(encoded) != len(decoded):
        raise ValueError("encoded and decoded sequences must have equal length")
    if not encoded:
        return 0.0
    return max(abs(float(a.angle_deg) - float(b.angle_deg)) for a, b in zip(encoded, decoded))
