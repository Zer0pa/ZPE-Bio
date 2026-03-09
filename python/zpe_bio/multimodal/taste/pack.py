from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

from ..core.constants import DEFAULT_VERSION, Mode
from ..diagram.quantize import DrawDir, MoveTo

from .taste_space import (
    dominant_intensity_from_vector,
    dominant_quality_from_vector,
    quality_vector_to_taste_time_point,
)
from .temporal_codebook import (
    COARSE_MODE,
    FINE_MODE,
    auto_select_resolution,
    decode_temporal_coarse,
    decode_temporal_fine,
    encode_temporal_coarse,
    encode_temporal_fine,
)
from .types import (
    DurationClass,
    TasteQuality,
    TasteStroke,
    TasteZLevel,
    ZLayeredTasteEvent,
    validate_quality_vector,
)

TASTE_TYPE_BIT = 0x0400

VERSION_HEADER = 0
VERSION_PROFILE_A = 1
VERSION_PROFILE_B = 2
VERSION_STEP = 3

HIGH_TYPE_COLLISION_MASK = 0x8000 | 0x4000 | 0x2000 | 0x1000 | 0x0800 | 0x0200 | 0x0100
ADAPTIVE_COARSE_FLAG = 0x80


def _ext_word(version: int, payload: int) -> int:
    return (Mode.EXTENSION.value << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)


def _word_fields(word: int) -> tuple[int, int, int]:
    mode = (word >> 18) & 0x3
    version = (word >> 16) & 0x3
    payload = word & 0xFFFF
    return mode, version, payload


def _payload_from_byte(data_byte: int) -> int:
    payload = TASTE_TYPE_BIT | (data_byte & 0xFF)
    if payload & HIGH_TYPE_COLLISION_MASK:
        raise ValueError(f"payload collides with another modality bit: {payload:#06x}")
    return payload


def _encode_profile_vector(quality_vector: tuple[int, ...]) -> tuple[int, int]:
    packed = 0
    for idx, value in enumerate(quality_vector):
        packed |= (value & 0x7) << (idx * 3)
    low8 = packed & 0xFF
    high7 = (packed >> 8) & 0x7F
    return low8, high7


def _decode_profile_vector(low8: int, high7: int) -> tuple[int, int, int, int, int]:
    packed = (low8 & 0xFF) | ((high7 & 0x7F) << 8)
    return (
        (packed >> 0) & 0x7,
        (packed >> 3) & 0x7,
        (packed >> 6) & 0x7,
        (packed >> 9) & 0x7,
        (packed >> 12) & 0x7,
    )


def _duration_from_step_count(step_count: int) -> DurationClass:
    return DurationClass.LONG if step_count >= 3 else DurationClass.SHORT


def _is_taste_extension_word(word: int) -> bool:
    mode, version, payload = _word_fields(word)
    return mode == Mode.EXTENSION.value and version == DEFAULT_VERSION and (payload & TASTE_TYPE_BIT) != 0


def _decode_header_fields(word: int) -> tuple[int, int]:
    _mode, version, payload = _word_fields(word)
    if version != VERSION_HEADER or (payload & TASTE_TYPE_BIT) == 0:
        raise ValueError("not a taste header word")
    data = payload & 0xFF
    dominant_quality = (data >> 5) & 0x7
    dominant_intensity = (data >> 2) & 0x7
    return dominant_quality, dominant_intensity


def _decode_step_fields(word: int) -> tuple[int, int, int]:
    _mode, version, payload = _word_fields(word)
    if version != VERSION_STEP or (payload & TASTE_TYPE_BIT) == 0:
        raise ValueError("not a taste step word")
    data = payload & 0xFF
    direction = (data >> 5) & 0x7
    phase = (data >> 3) & 0x3
    duration = (data >> 2) & 0x1
    return direction, phase, duration


def pack_taste_strokes(
    strokes: Iterable[TasteStroke],
    metadata: Optional[dict] = None,
) -> List[int]:
    """Pack taste strokes into extension words with 0x0400 type bit."""

    del metadata  # reserved for future stream metadata words

    words: List[int] = []

    for stroke in strokes:
        if not isinstance(stroke, TasteStroke):
            raise TypeError(f"expected TasteStroke, got {type(stroke)!r}")
        if not stroke.commands:
            continue
        if not isinstance(stroke.commands[0], MoveTo):
            raise ValueError("each stroke must begin with MoveTo")

        quality_vector = validate_quality_vector(stroke.quality_vector)
        directions = [cmd.direction for cmd in stroke.commands[1:] if isinstance(cmd, DrawDir)]

        dominant_quality = (
            stroke.dominant_quality
            if isinstance(stroke.dominant_quality, TasteQuality)
            else dominant_quality_from_vector(quality_vector)
        )
        dominant_intensity = dominant_intensity_from_vector(quality_vector)
        duration = _duration_from_step_count(len(directions))

        header_data = ((int(dominant_quality) & 0x7) << 5) | ((dominant_intensity & 0x7) << 2)
        words.append(_ext_word(VERSION_HEADER, _payload_from_byte(header_data)))

        profile_low8, profile_high7 = _encode_profile_vector(quality_vector)
        words.append(_ext_word(VERSION_PROFILE_A, _payload_from_byte(profile_low8)))

        profile_b_data = ((int(duration) & 0x1) << 7) | (profile_high7 & 0x7F)
        words.append(_ext_word(VERSION_PROFILE_B, _payload_from_byte(profile_b_data)))

        for idx, direction in enumerate(directions):
            phase = min(idx, 3)
            step_data = ((direction & 0x7) << 5) | ((phase & 0x3) << 3) | ((int(duration) & 0x1) << 2)
            words.append(_ext_word(VERSION_STEP, _payload_from_byte(step_data)))

    return words


def unpack_taste_words(
    words: Iterable[int],
) -> tuple[dict | None, List[TasteStroke]]:
    """Unpack extension words with 0x0400 type bit into TasteStroke objects."""

    word_list = list(words)
    if not word_list:
        return None, []

    strokes: List[TasteStroke] = []
    dominant_intensities: List[int] = []
    phase_sequences: List[List[int]] = []
    duration_classes: List[int] = []

    consumed = 0
    ignored = 0

    idx = 0
    while idx < len(word_list):
        word = word_list[idx]
        if not isinstance(word, int):
            ignored += 1
            idx += 1
            continue

        mode, version, payload = _word_fields(word)
        if mode != Mode.EXTENSION.value or version != VERSION_HEADER or (payload & TASTE_TYPE_BIT) == 0:
            ignored += 1
            idx += 1
            continue

        if idx + 2 >= len(word_list):
            break

        word_a = word_list[idx + 1]
        word_b = word_list[idx + 2]
        if not isinstance(word_a, int) or not isinstance(word_b, int):
            ignored += 1
            idx += 1
            continue

        mode_a, version_a, payload_a = _word_fields(word_a)
        mode_b, version_b, payload_b = _word_fields(word_b)

        if (
            mode_a != Mode.EXTENSION.value
            or version_a != VERSION_PROFILE_A
            or (payload_a & TASTE_TYPE_BIT) == 0
            or mode_b != Mode.EXTENSION.value
            or version_b != VERSION_PROFILE_B
            or (payload_b & TASTE_TYPE_BIT) == 0
        ):
            ignored += 1
            idx += 1
            continue

        dominant_quality_raw, dominant_intensity = _decode_header_fields(word)
        profile_low8 = payload_a & 0xFF
        profile_b_data = payload_b & 0xFF
        duration = (profile_b_data >> 7) & 0x1
        profile_high7 = profile_b_data & 0x7F

        quality_vector = _decode_profile_vector(profile_low8, profile_high7)

        if dominant_quality_raw in range(5):
            dominant_quality = TasteQuality(dominant_quality_raw)
        else:
            dominant_quality = dominant_quality_from_vector(quality_vector)

        start = quality_vector_to_taste_time_point(quality_vector, time_index=1)
        commands: List[MoveTo | DrawDir] = [MoveTo(*start)]

        phases: List[int] = []
        j = idx + 3
        while j < len(word_list):
            step_word = word_list[j]
            if not isinstance(step_word, int):
                break

            s_mode, s_version, s_payload = _word_fields(step_word)
            if s_mode != Mode.EXTENSION.value or s_version != VERSION_STEP or (s_payload & TASTE_TYPE_BIT) == 0:
                break

            direction, phase, _duration = _decode_step_fields(step_word)
            commands.append(DrawDir(direction))
            phases.append(phase)
            j += 1

        strokes.append(
            TasteStroke(
                commands=commands,
                dominant_quality=dominant_quality,
                quality_vector=quality_vector,
            )
        )
        dominant_intensities.append(dominant_intensity)
        phase_sequences.append(phases)
        duration_classes.append(duration)

        consumed += j - idx
        idx = j

    if not strokes:
        return None, []

    metadata = {
        "consumed_words": consumed,
        "duration_classes": duration_classes,
        "dominant_intensities": dominant_intensities,
        "ignored_words": ignored,
        "phase_sequences": phase_sequences,
        "stroke_count": len(strokes),
    }
    return metadata, strokes


def pack_taste_zlevel_word(z_level: TasteZLevel, data_byte: int) -> int:
    """Pack one z-layer payload byte into a taste extension word.

    Z-level is encoded in the extension version bits [17:16] so all low byte bits
    remain available for semantic payload while preserving type-bit dispatch.
    """
    if not isinstance(z_level, TasteZLevel):
        raise TypeError("z_level must be a TasteZLevel")
    if not 0 <= int(data_byte) <= 0xFF:
        raise ValueError("data_byte must be in [0, 255]")
    payload = _payload_from_byte(int(data_byte))
    return _ext_word(int(z_level), payload)


def unpack_taste_zlevel_word(word: int) -> tuple[TasteZLevel, int] | None:
    """Decode one z-layer word into (z_level, data_byte) or None if not applicable."""
    if not isinstance(word, int):
        return None
    mode, version, payload = _word_fields(word)
    if mode != Mode.EXTENSION.value or (payload & TASTE_TYPE_BIT) == 0:
        return None
    try:
        z_level = TasteZLevel(version & 0x3)
    except ValueError:
        return None
    return z_level, payload & 0xFF


def _pack_temporal_directions(directions: tuple[int, ...]) -> tuple[int, int, int]:
    return encode_temporal_fine(directions)


def _unpack_temporal_directions(chunk0: int, chunk1: int, chunk2: int) -> tuple[int, ...]:
    return decode_temporal_fine(chunk0, chunk1, chunk2)


def pack_taste_zlayered(
    events: Iterable[ZLayeredTasteEvent],
    metadata: Optional[dict] = None,
    adaptive: bool = False,
) -> List[int]:
    """Pack Z-layered taste events (QUALITY/INTENSITY/TEMPORAL/optional FLAVOR)."""
    del metadata  # Reserved for future stream-level metadata.

    words: List[int] = []
    for event in events:
        if not isinstance(event, ZLayeredTasteEvent):
            raise TypeError(f"expected ZLayeredTasteEvent, got {type(event)!r}")

        temporal_mode = FINE_MODE
        if adaptive:
            temporal_mode = auto_select_resolution(event.temporal_directions)
        use_coarse = temporal_mode == COARSE_MODE

        quality_byte = ((int(event.dominant_quality) & 0x7) << 3) | (int(event.secondary_quality) & 0x7)
        intensity_byte = ((int(event.intensity) & 0x7) << 3) | (int(event.intensity_direction) & 0x7)
        if use_coarse:
            intensity_byte |= ADAPTIVE_COARSE_FLAG
            t0, t1 = encode_temporal_coarse(event.temporal_directions)
            t2 = None
        else:
            t0, t1, t2 = encode_temporal_fine(event.temporal_directions)

        words.append(pack_taste_zlevel_word(TasteZLevel.QUALITY, quality_byte))
        words.append(pack_taste_zlevel_word(TasteZLevel.INTENSITY, intensity_byte))
        words.append(pack_taste_zlevel_word(TasteZLevel.TEMPORAL, t0))
        words.append(pack_taste_zlevel_word(TasteZLevel.TEMPORAL, t1))
        if t2 is not None:
            words.append(pack_taste_zlevel_word(TasteZLevel.TEMPORAL, t2))

        if event.flavor_link is not None:
            flavor_byte = ((int(event.flavor_link[0]) & 0x7) << 3) | (int(event.flavor_link[1]) & 0x7)
            words.append(pack_taste_zlevel_word(TasteZLevel.FLAVOR, flavor_byte))

    return words


def unpack_taste_zlayered(
    words: Iterable[int],
) -> tuple[dict | None, List[ZLayeredTasteEvent]]:
    """Unpack Z-layered taste extension words into ZLayeredTasteEvent objects."""
    word_list = list(words)
    if not word_list:
        return None, []

    events: List[ZLayeredTasteEvent] = []
    ignored = 0
    coarse_events = 0
    fine_events = 0
    idx = 0

    while idx < len(word_list):
        first = unpack_taste_zlevel_word(word_list[idx])
        if first is None or first[0] != TasteZLevel.QUALITY:
            ignored += 1
            idx += 1
            continue

        if idx + 3 >= len(word_list):
            break

        second = unpack_taste_zlevel_word(word_list[idx + 1])
        tword0 = unpack_taste_zlevel_word(word_list[idx + 2])
        tword1 = unpack_taste_zlevel_word(word_list[idx + 3])
        if (
            second is None
            or second[0] != TasteZLevel.INTENSITY
            or tword0 is None
            or tword1 is None
            or tword0[0] != TasteZLevel.TEMPORAL
            or tword1[0] != TasteZLevel.TEMPORAL
        ):
            ignored += 1
            idx += 1
            continue

        quality_byte = first[1]
        intensity_byte = second[1]
        use_coarse = (intensity_byte & ADAPTIVE_COARSE_FLAG) != 0

        tword2 = None
        if not use_coarse:
            if idx + 4 >= len(word_list):
                break
            tword2 = unpack_taste_zlevel_word(word_list[idx + 4])
            if tword2 is None or tword2[0] != TasteZLevel.TEMPORAL:
                ignored += 1
                idx += 1
                continue

        dominant = (quality_byte >> 3) & 0x7
        secondary = quality_byte & 0x7
        if dominant not in range(5) or secondary not in range(5):
            ignored += 4 if use_coarse else 5
            idx += 4 if use_coarse else 5
            continue

        intensity = (intensity_byte >> 3) & 0x7
        trend = intensity_byte & 0x7
        if use_coarse:
            temporal_directions = decode_temporal_coarse(tword0[1], tword1[1])
            consumed = 4
            coarse_events += 1
        else:
            temporal_directions = decode_temporal_fine(tword0[1], tword1[1], tword2[1])
            consumed = 5
            fine_events += 1

        flavor_link: tuple[int, int] | None = None
        if idx + consumed < len(word_list):
            maybe_flavor = unpack_taste_zlevel_word(word_list[idx + consumed])
            if maybe_flavor is not None and maybe_flavor[0] == TasteZLevel.FLAVOR:
                flavor_data = maybe_flavor[1]
                flavor_link = ((flavor_data >> 3) & 0x7, flavor_data & 0x7)
                consumed += 1

        events.append(
            ZLayeredTasteEvent(
                dominant_quality=TasteQuality(dominant),
                secondary_quality=TasteQuality(secondary),
                intensity=intensity,
                intensity_direction=trend,
                temporal_directions=temporal_directions,
                duration=DurationClass.LONG if intensity >= 4 else DurationClass.SHORT,
                flavor_link=flavor_link,
            )
        )
        idx += consumed

    if not events:
        return None, []

    metadata = {
        "coarse_events": coarse_events,
        "event_count": len(events),
        "fine_events": fine_events,
        "ignored_words": ignored,
        "zlayer_word_count": len(word_list),
    }
    return metadata, events


def pack_fused_multimodal(
    taste_events: Sequence[ZLayeredTasteEvent],
    smell_packets: Sequence[Sequence[int]],
    touch_packets: Sequence[Sequence[int]],
    adaptive: bool = True,
) -> List[int]:
    """Pack a deterministic multimodal fused stream in taste->smell->touch order."""
    fused: List[int] = []
    frame_count = max(len(taste_events), len(smell_packets), len(touch_packets))

    for index in range(frame_count):
        if index < len(taste_events):
            fused.extend(pack_taste_zlayered([taste_events[index]], adaptive=adaptive))
        if index < len(smell_packets):
            fused.extend(int(word) for word in smell_packets[index])
        if index < len(touch_packets):
            fused.extend(int(word) for word in touch_packets[index])

    return fused


def decode_zlayer_words(words: Iterable[int], z_level: TasteZLevel) -> List[int]:
    """Extract raw payload bytes for the requested z-level."""
    if not isinstance(z_level, TasteZLevel):
        raise TypeError("z_level must be a TasteZLevel")
    extracted: List[int] = []
    for word in words:
        decoded = unpack_taste_zlevel_word(word)
        if decoded is None:
            continue
        level, data_byte = decoded
        if level == z_level:
            extracted.append(data_byte)
    return extracted
