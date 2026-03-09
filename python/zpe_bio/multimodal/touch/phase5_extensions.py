from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from .pack import pack_touch_strokes, unpack_touch_words
from .types import BodyRegion, TouchStroke

MODE_EXTENSION = 0b10
TOUCH_TYPE_BIT = 0x0800

VERSION_CONTROL = 2
VERSION_RAII = 3

CONTROL_TAG_SHIFT = 8
CONTROL_TAG_MASK = 0x7

CONTROL_FRAME_START = 1
CONTROL_ANCHOR = 2

FRAME_COUNT_SHIFT = 4
FRAME_ID_MASK = 0xF

ANCHOR_X_SHIFT = 4
ANCHOR_MASK = 0xF

RAII_TAG_SHIFT = 8
RAII_TAG_MASK = 0x7
RAII_FREQ_TAG = 1
RAII_BAND_SHIFT = 4
RAII_BAND_MASK = 0xF
RAII_REGION_MASK = 0xF


@dataclass
class SimultaneousFrame:
    frame_id: int
    contacts: List[TouchStroke]


@dataclass(frozen=True)
class RAIIFrequencySample:
    region: BodyRegion
    band: int


@dataclass(frozen=True)
class AnchoredTouch:
    region: BodyRegion
    anchor: Tuple[int, int]
    stroke: TouchStroke


# Coarse 2D centroid map on a normalized 16x16 skin-topology grid.
REGION_CENTROIDS: Dict[BodyRegion, Tuple[int, int]] = {
    BodyRegion.THUMB_TIP: (3, 2),
    BodyRegion.INDEX_TIP: (5, 1),
    BodyRegion.MIDDLE_TIP: (7, 1),
    BodyRegion.RING_TIP: (9, 2),
    BodyRegion.PINKY_TIP: (11, 3),
    BodyRegion.PALM_THENAR: (4, 6),
    BodyRegion.PALM_HYPOTHENAR: (10, 7),
    BodyRegion.PALM_CENTER: (7, 7),
    BodyRegion.DORSAL_HAND: (7, 10),
    BodyRegion.WRIST_FOREARM: (7, 12),
    BodyRegion.LIPS: (8, 2),
    BodyRegion.TONGUE: (8, 3),
    BodyRegion.FACE: (8, 4),
    BodyRegion.TORSO: (8, 9),
    BodyRegion.ARM_LEG: (8, 11),
    BodyRegion.FOOT_SOLE: (8, 14),
}


def _clamp_nibble(value: int) -> int:
    return max(0, min(15, int(value)))


def _pack_extension_word(version: int, payload: int) -> int:
    return (MODE_EXTENSION << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)


def _is_touch_ext_word(word: int) -> bool:
    return ((word >> 18) & 0x3) == MODE_EXTENSION and (word & TOUCH_TYPE_BIT) != 0


def _version(word: int) -> int:
    return (word >> 16) & 0x3


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
    return _pack_extension_word(VERSION_CONTROL, payload)


def parse_frame_start_word(word: int) -> Tuple[int, int]:
    if not (_is_touch_ext_word(word) and _version(word) == VERSION_CONTROL):
        raise ValueError("word is not a touch control word")
    if _control_tag(word) != CONTROL_FRAME_START:
        raise ValueError("control word is not FRAME_START")

    contact_count = (word >> FRAME_COUNT_SHIFT) & 0xF
    frame_id = word & FRAME_ID_MASK
    return contact_count, frame_id


def pack_simultaneous_frame(frame: SimultaneousFrame) -> List[int]:
    words = [build_frame_start_word(contact_count=len(frame.contacts), frame_id=frame.frame_id)]
    words.extend(pack_touch_strokes(frame.contacts))
    return words


def unpack_simultaneous_frame(words: Sequence[int]) -> Tuple[dict, SimultaneousFrame]:
    if not words:
        raise ValueError("empty word stream")

    expected_count, frame_id = parse_frame_start_word(words[0])
    meta, contacts = unpack_touch_words(words[1:])

    metadata = {
        "frame_id": frame_id,
        "expected_contacts": expected_count,
        "decoded_contacts": len(contacts),
        "cooccurrence_preserved": len(contacts) == expected_count,
        "decode_meta": meta,
    }
    return metadata, SimultaneousFrame(frame_id=frame_id, contacts=contacts)


def build_raii_frequency_word(region: BodyRegion | int, band: int) -> int:
    region_val = int(region.value) if isinstance(region, BodyRegion) else int(region)
    if not 0 <= region_val <= 15:
        raise ValueError(f"region must be in [0, 15], got {region_val}")
    if not 0 <= band <= 15:
        raise ValueError(f"band must be in [0, 15], got {band}")

    payload = TOUCH_TYPE_BIT
    payload |= (RAII_FREQ_TAG & RAII_TAG_MASK) << RAII_TAG_SHIFT
    payload |= (band & RAII_BAND_MASK) << RAII_BAND_SHIFT
    payload |= region_val & RAII_REGION_MASK
    return _pack_extension_word(VERSION_RAII, payload)


def parse_raii_frequency_word(word: int) -> RAIIFrequencySample:
    if not (_is_touch_ext_word(word) and _version(word) == VERSION_RAII):
        raise ValueError("word is not a RA-II extension word")
    if ((word >> RAII_TAG_SHIFT) & RAII_TAG_MASK) != RAII_FREQ_TAG:
        raise ValueError("RA-II tag mismatch")

    band = (word >> RAII_BAND_SHIFT) & RAII_BAND_MASK
    region = BodyRegion(word & RAII_REGION_MASK)
    return RAIIFrequencySample(region=region, band=band)


def pack_raii_frequency_sequence(
    region: BodyRegion,
    bands: Iterable[int],
) -> List[int]:
    return [build_raii_frequency_word(region=region, band=band) for band in bands]


def unpack_raii_frequency_words(words: Iterable[int]) -> List[RAIIFrequencySample]:
    decoded: List[RAIIFrequencySample] = []
    for word in words:
        if not _is_touch_ext_word(word):
            continue
        if _version(word) != VERSION_RAII:
            continue
        if ((word >> RAII_TAG_SHIFT) & RAII_TAG_MASK) != RAII_FREQ_TAG:
            continue
        decoded.append(parse_raii_frequency_word(word))
    return decoded


def build_anchor_word(anchor_x: int, anchor_y: int) -> int:
    payload = TOUCH_TYPE_BIT
    payload |= (CONTROL_ANCHOR & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload |= (_clamp_nibble(anchor_x) & ANCHOR_MASK) << ANCHOR_X_SHIFT
    payload |= _clamp_nibble(anchor_y) & ANCHOR_MASK
    return _pack_extension_word(VERSION_CONTROL, payload)


def parse_anchor_word(word: int) -> Tuple[int, int]:
    if not (_is_touch_ext_word(word) and _version(word) == VERSION_CONTROL):
        raise ValueError("word is not a touch control word")
    if _control_tag(word) != CONTROL_ANCHOR:
        raise ValueError("control word is not ANCHOR")

    anchor_x = (word >> ANCHOR_X_SHIFT) & ANCHOR_MASK
    anchor_y = word & ANCHOR_MASK
    return anchor_x, anchor_y


def pack_anchored_touch(
    stroke: TouchStroke,
    offset: Tuple[int, int],
) -> List[int]:
    centroid = REGION_CENTROIDS[stroke.region]
    anchor = (_clamp_nibble(centroid[0] + offset[0]), _clamp_nibble(centroid[1] + offset[1]))
    words = [build_anchor_word(anchor_x=anchor[0], anchor_y=anchor[1])]
    words.extend(pack_touch_strokes([stroke]))
    return words


def unpack_anchored_touch(words: Sequence[int]) -> Tuple[dict, AnchoredTouch | None]:
    if not words:
        return {"decoded": False, "reason": "empty"}, None

    anchor_x, anchor_y = parse_anchor_word(words[0])
    _, strokes = unpack_touch_words(words[1:])
    if not strokes:
        return {
            "decoded": False,
            "reason": "no_touch_stroke_after_anchor",
            "anchor": (anchor_x, anchor_y),
        }, None

    anchored = AnchoredTouch(region=strokes[0].region, anchor=(anchor_x, anchor_y), stroke=strokes[0])
    return {"decoded": True, "anchor": (anchor_x, anchor_y)}, anchored
