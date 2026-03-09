from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from ..diagram.quantize import DIRS, DrawDir, MoveTo

from .types import OdorCategory, OdorStroke, OlfactoryEvent, TemporalPhase

Point = Tuple[int, int]

# Anchors encode canonical POM positions (pleasantness, intensity).
CATEGORY_ANCHORS: Dict[OdorCategory, Tuple[int, int, int]] = {
    OdorCategory.FLORAL: (6, 3, 2),
    OdorCategory.FRUITY: (6, 4, 2),
    OdorCategory.SPICY_HERBAL: (4, 4, 3),
    OdorCategory.WOODY_EARTHY: (3, 5, 5),
    OdorCategory.CHEMICAL_SOLVENT: (1, 6, 6),
    OdorCategory.MUSKY_ANIMAL: (5, 5, 5),
    OdorCategory.MINTY_CAMPHOR: (4, 6, 4),
    OdorCategory.PUTRID_DECAY: (0, 7, 6),
}

# Five-channel quality vector: floral, fruity, spicy, woody, chemical.
PLEASANTNESS_WEIGHTS = (0.95, 0.8, 0.15, -0.25, -1.0)
INTENSITY_WEIGHTS = (0.35, 0.45, 0.65, 0.75, 0.95)


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


def category_anchor(category: OdorCategory) -> Tuple[int, int]:
    if not isinstance(category, OdorCategory):
        raise ValueError("category must be an OdorCategory")
    pleasantness, intensity, _complexity = CATEGORY_ANCHORS[category]
    return pleasantness, intensity


def project_quality_vector_to_pom(quality: Sequence[float]) -> Tuple[int, int]:
    """Map a 5-channel quality vector to POM 2D (pleasantness, intensity)."""
    if len(quality) != 5:
        raise ValueError("quality vector must have length 5")

    clipped = [max(0.0, min(1.0, float(v))) for v in quality]
    pleasantness = _normalize_weighted_sum(PLEASANTNESS_WEIGHTS, clipped)
    intensity = _normalize_weighted_sum(INTENSITY_WEIGHTS, clipped)

    return _clamp_uint3(pleasantness * 7.0), _clamp_uint3(intensity * 7.0)


def project_odor_vector3_to_pom(vector3: Sequence[float]) -> Tuple[int, int]:
    """Project normalized (pleasantness, intensity, complexity) into POM 2D."""
    if len(vector3) != 3:
        raise ValueError("3D odor vector must have length 3")

    pleasantness, intensity, complexity = [max(0.0, min(1.0, float(v))) for v in vector3]

    # Complexity weakly skews both axes to emulate 3D -> 2D compression.
    pleasantness_adj = pleasantness - 0.15 * complexity
    intensity_adj = intensity + 0.1 * complexity
    return _clamp_uint3(pleasantness_adj * 7.0), _clamp_uint3(intensity_adj * 7.0)


def _pom_to_grid(point: Point) -> Point:
    x, y_intensity = point
    return x, 7 - y_intensity


def _grid_to_pom(point: Point) -> Point:
    x, y = point
    return x, 7 - y


def nearest_direction_step(start: Point, end: Point) -> int:
    """Return nearest 8-direction index from start POM point to end POM point."""
    sx, sy = _pom_to_grid(start)
    ex, ey = _pom_to_grid(end)
    dx = ex - sx
    dy = ey - sy
    step_dx = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_dy = 0 if dy == 0 else (1 if dy > 0 else -1)
    try:
        return DIRS.index((step_dx, step_dy))
    except ValueError as exc:
        raise ValueError(f"invalid direction delta ({step_dx}, {step_dy})") from exc


def apply_direction(point: Point, direction: int) -> Point:
    if not 0 <= direction <= 7:
        raise ValueError(f"direction must be in [0, 7], got {direction}")
    gx, gy = _pom_to_grid(point)
    dx, dy = DIRS[direction]
    nx = max(0, min(7, gx + dx))
    ny = max(0, min(7, gy + dy))
    return _grid_to_pom((nx, ny))


def _phase_pattern(category: OdorCategory) -> List[int]:
    pleasantness, _intensity = category_anchor(category)
    if pleasantness >= 5:
        return [2, 1, 0, 6]
    if pleasantness <= 2:
        return [2, 3, 4, 6]
    return [2, 2, 4, 6]


def synthetic_sniff_events(category: OdorCategory) -> List[OlfactoryEvent]:
    """Generate deterministic onset->peak->plateau->decay events."""
    pleasantness, intensity = category_anchor(category)
    directions = _phase_pattern(category)
    phases = [
        TemporalPhase.ONSET,
        TemporalPhase.PEAK,
        TemporalPhase.PLATEAU,
        TemporalPhase.DECAY,
    ]

    events: List[OlfactoryEvent] = []
    cur = (pleasantness, intensity)
    for phase, direction in zip(phases, directions):
        events.append(
            OlfactoryEvent(
                category=category,
                pleasantness=cur[0],
                intensity=cur[1],
                direction=direction,
                temporal_phase=phase,
            )
        )
        cur = apply_direction(cur, direction)
    return events


def synthetic_sniff_stroke(category: OdorCategory) -> OdorStroke:
    events = synthetic_sniff_events(category)
    first = events[0]
    commands: List[MoveTo | DrawDir] = [MoveTo(first.pleasantness, 7 - first.intensity)]
    for event in events:
        commands.append(DrawDir(event.direction))
    return OdorStroke(
        commands=commands,
        category=category,
        pleasantness_start=first.pleasantness,
        intensity_start=first.intensity,
    )
