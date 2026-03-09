from __future__ import annotations

from typing import Iterable, List, Optional

from ..core.constants import DEFAULT_VERSION, Mode
from ..diagram.quantize import DrawDir, MoveTo

from .types import OdorCategory, OdorStroke

SMELL_TYPE_BIT = 0x0200

# Keep all non-type data in low byte so modality high bits remain collision-free.
OP_HEADER_A = 0
OP_HEADER_B = 1
OP_STEP = 2
OP_META = 3

OP_SHIFT = 6
OP_MASK = 0x3
DATA_MASK = 0x3F

HIGH_TYPE_COLLISION_MASK = 0x8000 | 0x4000 | 0x2000 | 0x1000 | 0x0800 | 0x0400 | 0x0100


def _ext_word(payload: int) -> int:
    return (Mode.EXTENSION.value << 18) | (DEFAULT_VERSION << 16) | (payload & 0xFFFF)


def _payload(op: int, data: int) -> int:
    return SMELL_TYPE_BIT | ((op & OP_MASK) << OP_SHIFT) | (data & DATA_MASK)


def _assert_no_collision(payload: int) -> None:
    if payload & HIGH_TYPE_COLLISION_MASK:
        raise ValueError(f"payload collides with another modality bit: {payload:#06x}")


def pack_odor_strokes(
    strokes: Iterable[OdorStroke],
    metadata: Optional[dict] = None,
) -> List[int]:
    """Pack olfactory strokes into extension words with 0x0200 type bit."""
    words: List[int] = []

    if metadata:
        meta_value = int(metadata.get("sniff_hz", 0))
        if not 0 <= meta_value <= DATA_MASK:
            raise ValueError("metadata sniff_hz must be in [0, 63]")
        payload = _payload(OP_META, meta_value)
        _assert_no_collision(payload)
        words.append(_ext_word(payload))

    for stroke in strokes:
        if not stroke.commands:
            continue
        if not isinstance(stroke.commands[0], MoveTo):
            raise ValueError("each stroke must begin with MoveTo")

        draw_cmds = [cmd for cmd in stroke.commands[1:] if isinstance(cmd, DrawDir)]
        if len(draw_cmds) > 7:
            raise ValueError("smell v1 supports at most 7 steps per stroke")

        category = int(stroke.category) & 0x7
        pleasantness = stroke.pleasantness_start & 0x7
        intensity = stroke.intensity_start & 0x7
        step_count = len(draw_cmds) & 0x7

        header_a = _payload(OP_HEADER_A, (category << 3) | pleasantness)
        header_b = _payload(OP_HEADER_B, (intensity << 3) | step_count)
        _assert_no_collision(header_a)
        _assert_no_collision(header_b)

        words.append(_ext_word(header_a))
        words.append(_ext_word(header_b))

        for idx, cmd in enumerate(draw_cmds):
            direction = cmd.direction & 0x7
            phase = min(idx, 3)
            step_payload = _payload(OP_STEP, (direction << 3) | phase)
            _assert_no_collision(step_payload)
            words.append(_ext_word(step_payload))

    return words


def _word_payload(word: int) -> tuple[int, int, int]:
    mode = (word >> 18) & 0x3
    version = (word >> 16) & 0x3
    payload = word & 0xFFFF
    return mode, version, payload


def _is_smell_payload(payload: int) -> bool:
    return (payload & SMELL_TYPE_BIT) != 0


def unpack_odor_words(words: Iterable[int]) -> tuple[dict | None, List[OdorStroke]]:
    """Unpack extension words with 0x0200 type bit into OdorStroke objects."""
    word_list = list(words)
    if not word_list:
        return None, []

    metadata: dict | None = None
    strokes: List[OdorStroke] = []

    idx = 0
    while idx < len(word_list):
        word = word_list[idx]
        if not isinstance(word, int):
            idx += 1
            continue

        mode, version, payload = _word_payload(word)
        if mode != Mode.EXTENSION.value or version != DEFAULT_VERSION or not _is_smell_payload(payload):
            idx += 1
            continue

        op = (payload >> OP_SHIFT) & OP_MASK
        data = payload & DATA_MASK

        if op == OP_META:
            metadata = {"sniff_hz": data}
            idx += 1
            continue

        if op != OP_HEADER_A:
            idx += 1
            continue

        if idx + 1 >= len(word_list):
            break

        word_b = word_list[idx + 1]
        if not isinstance(word_b, int):
            idx += 1
            continue

        mode_b, version_b, payload_b = _word_payload(word_b)
        if mode_b != Mode.EXTENSION.value or version_b != DEFAULT_VERSION or not _is_smell_payload(payload_b):
            idx += 1
            continue

        op_b = (payload_b >> OP_SHIFT) & OP_MASK
        data_b = payload_b & DATA_MASK
        if op_b != OP_HEADER_B:
            idx += 1
            continue

        category_raw = (data >> 3) & 0x7
        pleasantness = data & 0x7
        intensity = (data_b >> 3) & 0x7
        expected_steps = data_b & 0x7

        try:
            category = OdorCategory(category_raw)
        except ValueError:
            idx += 2
            continue

        commands: List[MoveTo | DrawDir] = [MoveTo(pleasantness, 7 - intensity)]
        consumed = 0
        j = idx + 2
        while consumed < expected_steps and j < len(word_list):
            step_word = word_list[j]
            if not isinstance(step_word, int):
                break

            mode_s, version_s, payload_s = _word_payload(step_word)
            if mode_s != Mode.EXTENSION.value or version_s != DEFAULT_VERSION or not _is_smell_payload(payload_s):
                break

            op_s = (payload_s >> OP_SHIFT) & OP_MASK
            if op_s != OP_STEP:
                break

            data_s = payload_s & DATA_MASK
            direction = (data_s >> 3) & 0x7
            commands.append(DrawDir(direction))
            consumed += 1
            j += 1

        strokes.append(
            OdorStroke(
                commands=commands,
                category=category,
                pleasantness_start=pleasantness,
                intensity_start=intensity,
            )
        )
        idx = idx + 2 + consumed

    return metadata, strokes
