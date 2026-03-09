from __future__ import annotations

from typing import Iterable, List, Sequence

from ..diagram.quantize import DrawDir, MoveTo

from .odor_space import apply_direction
from .pack import pack_odor_strokes, unpack_odor_words
from .types import OdorStroke, OlfactoryEvent, TemporalPhase


def events_to_stroke(events: Sequence[OlfactoryEvent]) -> OdorStroke:
    if not events:
        raise ValueError("events cannot be empty")

    first = events[0]
    commands: List[MoveTo | DrawDir] = [MoveTo(first.pleasantness, 7 - first.intensity)]
    for event in events:
        commands.append(DrawDir(event.direction))

    return OdorStroke(
        commands=commands,
        category=first.category,
        pleasantness_start=first.pleasantness,
        intensity_start=first.intensity,
    )


def stroke_to_events(stroke: OdorStroke) -> List[OlfactoryEvent]:
    events: List[OlfactoryEvent] = []
    current = (stroke.pleasantness_start, stroke.intensity_start)

    draw_idx = 0
    for cmd in stroke.commands[1:]:
        if not isinstance(cmd, DrawDir):
            continue
        phase = TemporalPhase(min(draw_idx, 3))
        events.append(
            OlfactoryEvent(
                category=stroke.category,
                pleasantness=current[0],
                intensity=current[1],
                direction=cmd.direction,
                temporal_phase=phase,
            )
        )
        current = apply_direction(current, cmd.direction)
        draw_idx += 1

    return events


def encode_smell_strokes(strokes: Iterable[OdorStroke], metadata: dict | None = None) -> List[int]:
    return pack_odor_strokes(strokes, metadata=metadata)


def decode_smell_words(words: Iterable[int]) -> tuple[dict | None, List[OdorStroke]]:
    return unpack_odor_words(words)
