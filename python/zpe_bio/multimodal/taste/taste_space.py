from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from ..diagram.quantize import DIRS, DrawDir, MoveTo

from .types import (
    DurationClass,
    TasteEvent,
    TasteQuality,
    TasteStroke,
    TemporalPhase,
    ZLayeredTasteEvent,
    validate_quality_vector,
)

Point = Tuple[int, int]

# Canonical prototypes: (sweet, sour, salt, bitter, umami) in [0, 7]
QUALITY_PROTOTYPES: Dict[TasteQuality, tuple[int, int, int, int, int]] = {
    TasteQuality.SWEET: (7, 1, 1, 0, 3),
    TasteQuality.SOUR: (1, 7, 2, 1, 1),
    TasteQuality.SALT: (1, 2, 7, 1, 1),
    TasteQuality.BITTER: (0, 1, 1, 7, 1),
    TasteQuality.UMAMI: (2, 1, 1, 2, 7),
}

# PCA-1 surrogate weights emphasizing sweet/umami vs bitter/sour/salt.
PCA1_WEIGHTS: tuple[float, float, float, float, float] = (1.00, -0.35, -0.20, -1.10, 0.45)

# PCA-2 surrogate weights emphasizing sour/salt vs umami/sweet separation.
PCA2_WEIGHTS: tuple[float, float, float, float, float] = (-0.15, 1.00, 0.35, -0.45, 0.95)


def _clamp_uint3(value: float) -> int:
    return max(0, min(7, int(round(value))))


def _normalize_weighted_sum(weights: Sequence[float], values: Sequence[float]) -> float:
    min_sum = sum(min(0.0, w) for w in weights)
    max_sum = sum(max(0.0, w) for w in weights)
    raw = sum(w * v for w, v in zip(weights, values))
    span = max_sum - min_sum
    if span <= 0:
        return 0.0
    return (raw - min_sum) / span


def dominant_quality_from_vector(quality_vector: Sequence[int]) -> TasteQuality:
    vector = validate_quality_vector(quality_vector)
    dominant_idx = max(range(5), key=lambda i: (vector[i], -i))
    return TasteQuality(dominant_idx)


def secondary_quality_from_vector(quality_vector: Sequence[int]) -> TasteQuality:
    vector = validate_quality_vector(quality_vector)
    ranked = sorted(((value, -idx, idx) for idx, value in enumerate(vector)), reverse=True)
    return TasteQuality(ranked[1][2])


def dominant_intensity_from_vector(quality_vector: Sequence[int]) -> int:
    vector = validate_quality_vector(quality_vector)
    return max(vector)


def intensity_trend_direction(start: int, end: int) -> int:
    """Encode intensity trend into 8-direction vocabulary: up/down/stable."""
    if end > start:
        return 2  # upward trend
    if end < start:
        return 6  # downward trend
    return 0  # stable


def project_quality_vector_to_pca1(quality_vector: Sequence[int]) -> float:
    """Project 5D gustatory vector to scalar sweet↔bitter axis in [0.0, 1.0]."""
    vector = validate_quality_vector(quality_vector)
    normalized = [v / 7.0 for v in vector]
    return _normalize_weighted_sum(PCA1_WEIGHTS, normalized)


def pca1_to_axis_level(pca1_value: float) -> int:
    return _clamp_uint3(float(pca1_value) * 7.0)


def project_quality_vector_to_pca2(quality_vector: Sequence[int]) -> Point:
    """Project 5D gustatory vector to 2D surrogate PCA plane in uint3 coordinates."""
    vector = validate_quality_vector(quality_vector)
    normalized = [v / 7.0 for v in vector]

    axis_x = pca1_to_axis_level(_normalize_weighted_sum(PCA1_WEIGHTS, normalized))
    axis_y = pca1_to_axis_level(_normalize_weighted_sum(PCA2_WEIGHTS, normalized))
    return axis_x, axis_y


def quality_vector_to_taste_time_point(quality_vector: Sequence[int], time_index: int) -> Point:
    if not isinstance(time_index, int):
        raise TypeError("time_index must be int")
    x = max(0, min(7, time_index))
    y = pca1_to_axis_level(project_quality_vector_to_pca1(quality_vector))
    return x, y


def quality_vector_to_taste_plane_point(quality_vector: Sequence[int]) -> Point:
    return project_quality_vector_to_pca2(quality_vector)


def _axis_to_grid(point: Point) -> Point:
    x, y = point
    return x, 7 - y


def _grid_to_axis(point: Point) -> Point:
    x, y = point
    return x, 7 - y


def nearest_direction_step(start: Point, end: Point) -> int:
    """Nearest 8-direction step from start to end in taste-time space."""
    sx, sy = _axis_to_grid(start)
    ex, ey = _axis_to_grid(end)

    dx = ex - sx
    dy = ey - sy

    if dx == 0 and dy == 0:
        # Stationary step uses direction 0 (right) as canonical no-op token.
        return 0

    step_dx = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_dy = 0 if dy == 0 else (1 if dy > 0 else -1)

    try:
        return DIRS.index((step_dx, step_dy))
    except ValueError as exc:
        raise ValueError(f"invalid direction delta ({step_dx}, {step_dy})") from exc


def apply_direction(point: Point, direction: int) -> Point:
    if not 0 <= direction <= 7:
        raise ValueError(f"direction must be in [0, 7], got {direction}")

    gx, gy = _axis_to_grid(point)
    dx, dy = DIRS[direction]
    nx = max(0, min(7, gx + dx))
    ny = max(0, min(7, gy + dy))
    return _grid_to_axis((nx, ny))


def trajectory_from_pca2(quality_vector: Sequence[int], phase_count: int = 8) -> list[int]:
    """Generate an 8-direction trajectory from PCA-2 coordinates.

    First half moves toward the PCA-2 target point. Second half relaxes toward
    neutral center to represent decay/aftertaste dynamics.
    """
    if phase_count <= 0:
        raise ValueError("phase_count must be positive")

    target = quality_vector_to_taste_plane_point(quality_vector)
    center = (4, 4)
    point = (1, 4)

    directions: list[int] = []
    split = max(1, phase_count // 2)

    for _ in range(split):
        step = nearest_direction_step(point, target)
        directions.append(step)
        point = apply_direction(point, step)

    for _ in range(phase_count - split):
        step = nearest_direction_step(point, center)
        directions.append(step)
        point = apply_direction(point, step)

    return directions


def zlayered_event_from_vector(
    quality_vector: Sequence[int],
    temporal_directions: Sequence[int] | None = None,
    intensity_end: int | None = None,
    flavor_link: tuple[int, int] | None = None,
) -> ZLayeredTasteEvent:
    """Construct a validated Z-layered taste event from scalar/vector inputs."""
    vector = validate_quality_vector(quality_vector)
    dominant = dominant_quality_from_vector(vector)
    secondary = secondary_quality_from_vector(vector)
    intensity = dominant_intensity_from_vector(vector)
    intensity_end_value = intensity if intensity_end is None else max(0, min(7, int(intensity_end)))
    trend = intensity_trend_direction(intensity, intensity_end_value)
    temporal = tuple(temporal_directions) if temporal_directions is not None else tuple(_phase_pattern_8(dominant))
    duration = DurationClass.LONG if intensity >= 4 else DurationClass.SHORT
    return ZLayeredTasteEvent(
        dominant_quality=dominant,
        secondary_quality=secondary,
        intensity=intensity,
        intensity_direction=trend,
        temporal_directions=temporal,
        duration=duration,
        flavor_link=flavor_link,
    )


def _phase_pattern_4(quality: TasteQuality) -> list[int]:
    # Heuristic temporal signatures:
    # sweet fast onset, bitter persistent, sour quick decay, umami long sustain.
    if quality == TasteQuality.SWEET:
        return [1, 0, 0, 6]
    if quality == TasteQuality.SOUR:
        return [0, 0, 6, 6]
    if quality == TasteQuality.SALT:
        return [0, 7, 6, 0]
    if quality == TasteQuality.BITTER:
        return [7, 6, 0, 0]
    return [1, 1, 0, 0]  # UMAMI


def _phase_pattern_8(quality: TasteQuality) -> list[int]:
    if quality == TasteQuality.SWEET:
        return [1, 1, 0, 0, 0, 7, 6, 6]
    if quality == TasteQuality.SOUR:
        return [0, 0, 0, 6, 6, 6, 0, 0]
    if quality == TasteQuality.SALT:
        return [0, 7, 7, 6, 6, 0, 0, 0]
    if quality == TasteQuality.BITTER:
        return [7, 7, 6, 6, 0, 0, 0, 0]
    return [1, 1, 1, 0, 0, 0, 6, 6]  # UMAMI


def _phase_enum_sequence(phase_count: int) -> list[TemporalPhase]:
    if phase_count == 4:
        return [
            TemporalPhase.ONSET,
            TemporalPhase.PEAK,
            TemporalPhase.PLATEAU,
            TemporalPhase.DECAY,
        ]
    if phase_count == 8:
        return [
            TemporalPhase.ONSET_EARLY,
            TemporalPhase.ONSET_LATE,
            TemporalPhase.ONSET,
            TemporalPhase.PEAK,
            TemporalPhase.PEAK_SUSTAIN,
            TemporalPhase.PLATEAU,
            TemporalPhase.DECAY,
            TemporalPhase.DECAY_LATE,
        ]
    raise ValueError("phase_count must be 4 or 8")


def synthetic_taste_events(quality: TasteQuality, phase_count: int = 4) -> List[TasteEvent]:
    if not isinstance(quality, TasteQuality):
        raise TypeError("quality must be a TasteQuality")

    vector = QUALITY_PROTOTYPES[quality]
    dominant = dominant_quality_from_vector(vector)
    intensity = dominant_intensity_from_vector(vector)
    duration = DurationClass.LONG if quality in (TasteQuality.BITTER, TasteQuality.UMAMI) else DurationClass.SHORT

    phases = _phase_enum_sequence(phase_count)
    directions = _phase_pattern_4(quality) if phase_count == 4 else _phase_pattern_8(quality)

    events: List[TasteEvent] = []
    for phase, direction in zip(phases, directions):
        events.append(
            TasteEvent(
                quality_vector=vector,
                dominant_quality=dominant,
                dominant_intensity=intensity,
                direction=direction,
                temporal_phase=phase,
                duration=duration,
            )
        )
    return events


def synthetic_taste_stroke(quality: TasteQuality, phase_count: int = 4) -> TasteStroke:
    events = synthetic_taste_events(quality, phase_count=phase_count)
    first_event = events[0]
    start_point = quality_vector_to_taste_time_point(first_event.quality_vector, time_index=1)

    commands: List[MoveTo | DrawDir] = [MoveTo(*start_point)]
    for event in events:
        commands.append(DrawDir(event.direction))

    return TasteStroke(
        commands=commands,
        dominant_quality=first_event.dominant_quality,
        quality_vector=first_event.quality_vector,
    )


def synthetic_taste_stroke_8phase(quality: TasteQuality) -> TasteStroke:
    return synthetic_taste_stroke(quality, phase_count=8)


def synthetic_quality_profiles() -> Dict[TasteQuality, tuple[int, int, int, int, int]]:
    return dict(QUALITY_PROTOTYPES)
