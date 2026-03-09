from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from .types import (
    BodyRegion,
    DrawDir,
    MoveTo,
    RAIIDescriptor,
    ReceptorType,
    TouchZLevel,
    TouchStroke,
    ensure_body_region,
    ensure_receptor_type,
)
from .proprioception import (
    ProprioSample,
    dequantize_proprio_sample,
    quantize_proprio_sample,
)

MODE_EXTENSION = 0b10
DATA_VERSION = 0
HEADER_VERSION = 1
CONTROL_VERSION = 2
RAII_VERSION = 3

TOUCH_TYPE_BIT = 0x0800
OTHER_MODALITY_BITS = 0x8000 | 0x4000 | 0x2000 | 0x1000

HEADER_RECEPTOR_SHIFT = 9
HEADER_REGION_SHIFT = 5
HEADER_TAG = 0x001F  # low 5 bits mark stroke header words

DIRECTION_SHIFT = 3

CONTROL_TAG_SHIFT = 8
CONTROL_TAG_MASK = 0x7
CONTROL_FRAME_START = 1
CONTROL_TIME_HIGH = 3
CONTROL_TIME_LOW = 4
CONTROL_ZLAYER = 5

FRAME_COUNT_SHIFT = 4
FRAME_ID_MASK = 0xF

TIME_CHUNK_MASK = 0x3F

Z_LEVEL_SHIFT = 6
Z_LEVEL_MASK = 0x3
Z_VALUE_MASK = 0x3F

RAII_TAG_SHIFT = 8
RAII_TAG_MASK = 0x7
RAII_COMPLETE_A_TAG = 2
RAII_COMPLETE_B_TAG = 3
RAII_NIBBLE_SHIFT = 4
RAII_NIBBLE_MASK = 0xF
RAII_REGION_MASK = 0xF


def _coerce_word(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _pack_extension_word(version: int, payload: int) -> int:
    return (MODE_EXTENSION << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)


def _build_header_word(receptor: int, region: int) -> int:
    if not 0 <= receptor <= 3:
        raise ValueError(f"receptor out of range: {receptor}")
    if not 0 <= region <= 15:
        raise ValueError(f"region out of range: {region}")

    payload = TOUCH_TYPE_BIT
    payload |= (receptor & 0x3) << HEADER_RECEPTOR_SHIFT
    payload |= (region & 0xF) << HEADER_REGION_SHIFT
    payload |= HEADER_TAG
    return _pack_extension_word(HEADER_VERSION, payload)


def _build_step_word(direction: int, pressure: int) -> int:
    if not 0 <= direction <= 7:
        raise ValueError(f"direction out of range: {direction}")
    if not 0 <= pressure <= 7:
        raise ValueError(f"pressure out of range: {pressure}")

    payload = TOUCH_TYPE_BIT
    payload |= (direction & 0x7) << DIRECTION_SHIFT
    payload |= pressure & 0x7
    return _pack_extension_word(DATA_VERSION, payload)


def _word_mode(word: int) -> int:
    return (word >> 18) & 0x3


def _word_version(word: int) -> int:
    return (word >> 16) & 0x3


def _is_touch_extension_word(word: int) -> bool:
    return _word_mode(word) == MODE_EXTENSION and (word & TOUCH_TYPE_BIT) != 0


def _is_header_word(word: int) -> bool:
    return _word_version(word) == HEADER_VERSION and (word & HEADER_TAG) == HEADER_TAG


def _control_tag(word: int) -> int:
    return (word >> CONTROL_TAG_SHIFT) & CONTROL_TAG_MASK


def build_frame_start_word(contact_count: int, frame_id: int) -> int:
    if not 0 <= contact_count <= 15:
        raise ValueError(f"contact_count must be in [0, 15], got {contact_count}")
    if not 0 <= frame_id <= 15:
        raise ValueError(f"frame_id must be in [0, 15], got {frame_id}")

    payload = TOUCH_TYPE_BIT
    payload |= (CONTROL_FRAME_START & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload |= (contact_count & 0xF) << FRAME_COUNT_SHIFT
    payload |= frame_id & FRAME_ID_MASK
    return _pack_extension_word(CONTROL_VERSION, payload)


def parse_frame_start_word(word: int) -> Tuple[int, int]:
    if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
        raise ValueError("word is not a touch control word")
    if _control_tag(word) != CONTROL_FRAME_START:
        raise ValueError("control word is not FRAME_START")
    contact_count = (word >> FRAME_COUNT_SHIFT) & 0xF
    frame_id = word & FRAME_ID_MASK
    return contact_count, frame_id


def pack_timestamp_delta(delta_ms: int) -> List[int]:
    """Encode a 12-bit timestamp delta using exactly 2 words."""
    if not 0 <= delta_ms <= 0xFFF:
        raise ValueError(f"delta_ms must be in [0, 4095], got {delta_ms}")

    high_chunk = (delta_ms >> 6) & TIME_CHUNK_MASK
    low_chunk = delta_ms & TIME_CHUNK_MASK

    payload_high = TOUCH_TYPE_BIT
    payload_high |= (CONTROL_TIME_HIGH & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload_high |= high_chunk

    payload_low = TOUCH_TYPE_BIT
    payload_low |= (CONTROL_TIME_LOW & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload_low |= low_chunk

    return [
        _pack_extension_word(CONTROL_VERSION, payload_high),
        _pack_extension_word(CONTROL_VERSION, payload_low),
    ]


def unpack_timestamp_delta(words: Sequence[int]) -> int:
    if len(words) != 2:
        raise ValueError("timestamp delta must be exactly 2 words")

    high_word, low_word = words
    if not (_is_touch_extension_word(high_word) and _word_version(high_word) == CONTROL_VERSION):
        raise ValueError("high timestamp word is not touch control")
    if not (_is_touch_extension_word(low_word) and _word_version(low_word) == CONTROL_VERSION):
        raise ValueError("low timestamp word is not touch control")
    if _control_tag(high_word) != CONTROL_TIME_HIGH:
        raise ValueError("high timestamp word tag mismatch")
    if _control_tag(low_word) != CONTROL_TIME_LOW:
        raise ValueError("low timestamp word tag mismatch")

    high_chunk = high_word & TIME_CHUNK_MASK
    low_chunk = low_word & TIME_CHUNK_MASK
    return (high_chunk << 6) | low_chunk


def pack_timed_simultaneous_frame(
    frame_id: int,
    contacts: Sequence[TouchStroke],
    deltas_ms: Sequence[int],
) -> List[int]:
    if len(contacts) != len(deltas_ms):
        raise ValueError("contacts and deltas_ms must have identical lengths")

    words = [build_frame_start_word(contact_count=len(contacts), frame_id=frame_id)]
    for delta_ms, contact in zip(deltas_ms, contacts):
        words.extend(pack_timestamp_delta(delta_ms))
        words.extend(pack_touch_strokes([contact]))
    return words


def unpack_timed_simultaneous_frame(
    words: Sequence[int],
) -> tuple[dict, List[Tuple[int, TouchStroke]]]:
    if not words:
        raise ValueError("empty timed frame stream")

    expected_contacts, frame_id = parse_frame_start_word(words[0])
    index = 1
    decoded: List[Tuple[int, TouchStroke]] = []

    for _ in range(expected_contacts):
        if index + 2 > len(words):
            raise ValueError("incomplete timestamp delta in timed frame")
        delta_ms = unpack_timestamp_delta(words[index:index + 2])
        index += 2

        if index >= len(words):
            raise ValueError("missing touch stroke after timestamp")
        if not _is_header_word(words[index]):
            raise ValueError("timed contact does not begin with a touch header")

        stroke_start = index
        index += 1
        while index < len(words):
            word = words[index]
            if not _is_touch_extension_word(word):
                break
            if _is_header_word(word):
                break
            if _word_version(word) != DATA_VERSION:
                break
            index += 1

        _, strokes = unpack_touch_words(words[stroke_start:index])
        if len(strokes) != 1:
            raise ValueError("expected exactly one stroke per timed contact")
        decoded.append((delta_ms, strokes[0]))

    metadata = {
        "frame_id": frame_id,
        "expected_contacts": expected_contacts,
        "decoded_contacts": len(decoded),
        "cooccurrence_preserved": len(decoded) == expected_contacts,
        "remaining_words": len(words) - index,
    }
    return metadata, decoded


def pack_raii_complete(region: BodyRegion | int, descriptor: RAIIDescriptor) -> List[int]:
    region_val = int(region.value) if isinstance(region, BodyRegion) else int(region)
    if not 0 <= region_val <= 15:
        raise ValueError(f"region must be in [0, 15], got {region_val}")

    payload_a = TOUCH_TYPE_BIT
    payload_a |= (RAII_COMPLETE_A_TAG & RAII_TAG_MASK) << RAII_TAG_SHIFT
    payload_a |= (descriptor.frequency_band & RAII_NIBBLE_MASK) << RAII_NIBBLE_SHIFT
    payload_a |= descriptor.amplitude & RAII_NIBBLE_MASK

    payload_b = TOUCH_TYPE_BIT
    payload_b |= (RAII_COMPLETE_B_TAG & RAII_TAG_MASK) << RAII_TAG_SHIFT
    payload_b |= (descriptor.envelope & RAII_NIBBLE_MASK) << RAII_NIBBLE_SHIFT
    payload_b |= region_val & RAII_REGION_MASK

    return [
        _pack_extension_word(RAII_VERSION, payload_a),
        _pack_extension_word(RAII_VERSION, payload_b),
    ]


def unpack_raii_complete(words: Iterable[int]) -> List[Tuple[BodyRegion, RAIIDescriptor]]:
    stream = list(words)
    decoded: List[Tuple[BodyRegion, RAIIDescriptor]] = []
    index = 0

    while index + 1 < len(stream):
        first = stream[index]
        second = stream[index + 1]

        is_first_valid = (
            _is_touch_extension_word(first)
            and _word_version(first) == RAII_VERSION
            and ((first >> RAII_TAG_SHIFT) & RAII_TAG_MASK) == RAII_COMPLETE_A_TAG
        )
        is_second_valid = (
            _is_touch_extension_word(second)
            and _word_version(second) == RAII_VERSION
            and ((second >> RAII_TAG_SHIFT) & RAII_TAG_MASK) == RAII_COMPLETE_B_TAG
        )

        if not (is_first_valid and is_second_valid):
            index += 1
            continue

        descriptor = RAIIDescriptor(
            frequency_band=(first >> RAII_NIBBLE_SHIFT) & RAII_NIBBLE_MASK,
            amplitude=first & RAII_NIBBLE_MASK,
            envelope=(second >> RAII_NIBBLE_SHIFT) & RAII_NIBBLE_MASK,
        )
        region = BodyRegion(second & RAII_REGION_MASK)
        decoded.append((region, descriptor))
        index += 2

    return decoded


def pack_zlayer_word(z_level: TouchZLevel | int, value: int) -> int:
    z_level_int = int(z_level.value) if isinstance(z_level, TouchZLevel) else int(z_level)
    if not 0 <= z_level_int <= 3:
        raise ValueError(f"z_level must be in [0, 3], got {z_level_int}")
    if not 0 <= value <= Z_VALUE_MASK:
        raise ValueError(f"value must be in [0, {Z_VALUE_MASK}], got {value}")

    payload = TOUCH_TYPE_BIT
    payload |= (CONTROL_ZLAYER & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload |= (z_level_int & Z_LEVEL_MASK) << Z_LEVEL_SHIFT
    payload |= value & Z_VALUE_MASK
    return _pack_extension_word(CONTROL_VERSION, payload)


def unpack_zlayer_word(word: int) -> tuple[TouchZLevel, int]:
    if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
        raise ValueError("word is not a z-layer control word")
    if _control_tag(word) != CONTROL_ZLAYER:
        raise ValueError("control word is not z-layer data")

    z_level = TouchZLevel((word >> Z_LEVEL_SHIFT) & Z_LEVEL_MASK)
    value = word & Z_VALUE_MASK
    return z_level, value


def pack_touch_zlayers(
    directions: Sequence[int],
    pressures: Sequence[int],
    region: BodyRegion,
) -> List[int]:
    words: List[int] = []

    for direction in directions:
        if not 0 <= direction <= 7:
            raise ValueError(f"direction must be in [0, 7], got {direction}")
        words.append(pack_zlayer_word(TouchZLevel.SURFACE, direction))

    for pressure in pressures:
        if not 0 <= pressure <= 7:
            raise ValueError(f"pressure must be in [0, 7], got {pressure}")
        words.append(pack_zlayer_word(TouchZLevel.DERMAL, pressure))

    words.append(pack_zlayer_word(TouchZLevel.ANATOMICAL, int(region.value)))
    return words


def unpack_touch_zlayers(words: Iterable[int]) -> dict:
    surface: List[int] = []
    dermal: List[int] = []
    anatomical_values: List[int] = []
    proprioceptive_values: List[int] = []
    ignored = 0

    for raw_word in words:
        word = _coerce_word(raw_word)
        if word is None:
            ignored += 1
            continue
        if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
            ignored += 1
            continue
        if _control_tag(word) != CONTROL_ZLAYER:
            ignored += 1
            continue

        try:
            z_level, value = unpack_zlayer_word(word)
        except ValueError:
            ignored += 1
            continue

        if z_level == TouchZLevel.SURFACE:
            surface.append(value)
        elif z_level == TouchZLevel.DERMAL:
            dermal.append(value)
        elif z_level == TouchZLevel.ANATOMICAL:
            anatomical_values.append(value)
        elif z_level == TouchZLevel.PROPRIOCEPTIVE:
            proprioceptive_values.append(value)
        else:
            ignored += 1

    anatomical_region = None
    if anatomical_values:
        anatomical_region = BodyRegion(anatomical_values[-1] & 0xF)

    return {
        "surface": surface,
        "dermal": dermal,
        "anatomical_values": anatomical_values,
        "anatomical_region": anatomical_region,
        "proprioceptive_values": proprioceptive_values,
        "ignored_words": ignored,
    }


def pack_proprioception_samples(samples: Sequence[ProprioSample]) -> List[int]:
    words: List[int] = []

    for sample in samples:
        joint_id, angle_q, tension = quantize_proprio_sample(sample)
        high_angle = (angle_q >> 2) & Z_VALUE_MASK
        low_angle_with_tension = ((angle_q & 0x3) << 4) | (tension & 0xF)

        words.append(pack_zlayer_word(TouchZLevel.PROPRIOCEPTIVE, joint_id))
        words.append(pack_zlayer_word(TouchZLevel.PROPRIOCEPTIVE, high_angle))
        words.append(pack_zlayer_word(TouchZLevel.PROPRIOCEPTIVE, low_angle_with_tension))

    return words


def unpack_proprioception_samples(words: Iterable[int]) -> List[ProprioSample]:
    raw_values: List[int] = []

    for raw_word in words:
        word = _coerce_word(raw_word)
        if word is None:
            continue
        if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
            continue
        if _control_tag(word) != CONTROL_ZLAYER:
            continue
        z_level_raw = (word >> Z_LEVEL_SHIFT) & Z_LEVEL_MASK
        if z_level_raw != int(TouchZLevel.PROPRIOCEPTIVE):
            continue
        raw_values.append(word & Z_VALUE_MASK)

    decoded: List[ProprioSample] = []
    group_size = 3
    for index in range(0, len(raw_values) - (group_size - 1), group_size):
        joint_id = raw_values[index]
        high_angle = raw_values[index + 1]
        low_angle_with_tension = raw_values[index + 2]

        angle_q = ((high_angle & Z_VALUE_MASK) << 2) | ((low_angle_with_tension >> 4) & 0x3)
        tension = low_angle_with_tension & 0xF

        decoded.append(dequantize_proprio_sample(joint_id=joint_id, angle_q=angle_q, tension=tension))

    return decoded


def pack_touch_strokes(
    strokes: Iterable[TouchStroke],
    metadata: Optional[dict] = None,
) -> List[int]:
    del metadata  # reserved for future stream-level metadata packing

    words: List[int] = []
    for stroke in strokes:
        directions = [
            command.direction
            for command in stroke.commands
            if isinstance(command, DrawDir)
        ]
        if not directions:
            continue

        receptor = int(ensure_receptor_type(stroke.receptor).value)
        region = int(ensure_body_region(stroke.region).value)
        words.append(_build_header_word(receptor=receptor, region=region))

        for index, direction in enumerate(directions):
            pressure = stroke.pressure_profile[index] if index < len(stroke.pressure_profile) else 0
            words.append(_build_step_word(direction=direction, pressure=pressure))

    return words


def unpack_touch_words(
    words: Iterable[int],
) -> tuple[dict | None, List[TouchStroke]]:
    decoded: List[TouchStroke] = []
    current: TouchStroke | None = None

    consumed = 0
    headers = 0
    ignored = 0

    for raw_word in words:
        word = _coerce_word(raw_word)
        if word is None:
            ignored += 1
            continue
        if not _is_touch_extension_word(word):
            ignored += 1
            continue

        if _is_header_word(word):
            receptor_val = (word >> HEADER_RECEPTOR_SHIFT) & 0x3
            region_val = (word >> HEADER_REGION_SHIFT) & 0xF

            if current is not None and current.draw_count > 0:
                decoded.append(current)

            current = TouchStroke(
                commands=[MoveTo(0, 0)],
                receptor=ReceptorType(receptor_val),
                region=BodyRegion(region_val),
                pressure_profile=[],
            )
            headers += 1
            consumed += 1
            continue

        if _word_version(word) != DATA_VERSION:
            ignored += 1
            continue

        if current is None:
            # Touch step with no active stroke header.
            ignored += 1
            continue

        direction = (word >> DIRECTION_SHIFT) & 0x7
        pressure = word & 0x7
        current.commands.append(DrawDir(direction))
        current.pressure_profile.append(pressure)
        consumed += 1

    if current is not None and current.draw_count > 0:
        decoded.append(current)

    metadata = {
        "consumed_touch_words": consumed,
        "header_words": headers,
        "ignored_words": ignored,
    }
    return metadata, decoded
