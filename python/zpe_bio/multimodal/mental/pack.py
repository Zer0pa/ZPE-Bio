from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from .types import (
    DrawDir,
    DirectionProfile,
    FormClass,
    MentalStroke,
    MoveTo,
    SymmetryOrder,
    direction_modulus,
)

# 20-bit word fields
MODE_DRAW = 2
MODE_CONTROL = 3
DRAW_VERSION_RAW = 0
DRAW_VERSION_RLE = 1
VERSION_HEADER = 0
VERSION_X = 1
VERSION_Y = 2
VERSION_LEN = 3
# Logical extension control version. On-wire it is represented using VERSION_LEN
# plus a payload flag to preserve compatibility with 2-bit version fields.
VERSION_FRAME = 4
VERSION_DELTA = 5

MENTAL_TYPE_BIT = 0x0100
WORD_MASK = (1 << 20) - 1
FRAME_WORD_FLAG = 0x0800
# Legacy RLE marker used by earlier augmentation drops. It collides with the
# image family marker and is decode-only for backward compatibility.
LEGACY_RLE_RUN_FLAG = 0x0400
DELTA_WORD_FLAG = 0x0200
PROFILE_12_FLAG = 0x0002


def _coerce_int_words(words: Iterable[int]) -> List[int]:
    coerced: List[int] = []
    for value in words:
        try:
            coerced.append(int(value))
        except (TypeError, ValueError):
            continue
    return coerced


def _build_word(mode: int, version: int, payload: int) -> int:
    word = ((mode & 0x3) << 18) | ((version & 0x3) << 16) | (payload & 0x0FFF)
    return word & WORD_MASK


def _extract_fields(word: int) -> Tuple[int, int, int]:
    mode = (word >> 18) & 0x3
    version = (word >> 16) & 0x3
    payload = word & 0x0FFF
    return mode, version, payload


def _wire_control_version(version: int) -> int:
    if version in (VERSION_FRAME, VERSION_DELTA):
        return VERSION_LEN
    return version


def _command_is_move(cmd: object) -> bool:
    return hasattr(cmd, "x") and hasattr(cmd, "y") and not hasattr(cmd, "direction")


def _command_is_draw(cmd: object) -> bool:
    return hasattr(cmd, "direction")


def _header_payload(stroke: MentalStroke) -> int:
    form_bits = (int(stroke.form_class) & 0x3) << 10
    sym = int(stroke.symmetry) & 0x3
    sym_bits = ((sym >> 1) & 0x1) << 9
    sym_bits |= (sym & 0x1) << 7
    freq_bits = (int(stroke.spatial_frequency) & 0x7) << 4
    speed_bits = (int(stroke.drift_speed) & 0x3) << 2
    profile_bits = (
        PROFILE_12_FLAG
        if stroke.direction_profile == DirectionProfile.D6_12
        else 0
    )
    return MENTAL_TYPE_BIT | form_bits | sym_bits | freq_bits | speed_bits | profile_bits


def _parse_header_payload(
    payload: int,
) -> tuple[FormClass, SymmetryOrder, DirectionProfile, int, int]:
    form_class = FormClass((payload >> 10) & 0x3)
    sym_hi = (payload >> 9) & 0x1
    sym_lo = (payload >> 7) & 0x1
    symmetry = SymmetryOrder((sym_hi << 1) | sym_lo)
    profile = (
        DirectionProfile.D6_12
        if (payload & PROFILE_12_FLAG) != 0
        else DirectionProfile.COMPASS_8
    )
    spatial_frequency = (payload >> 4) & 0x7
    drift_speed = (payload >> 2) & 0x3
    return form_class, symmetry, profile, spatial_frequency, drift_speed


def _draw_payload(direction: int, profile: DirectionProfile) -> int:
    if profile == DirectionProfile.D6_12:
        return MENTAL_TYPE_BIT | ((direction & 0xF) << 4)
    return MENTAL_TYPE_BIT | ((direction & 0x7) << 5)


def _frame_payload(frame_index: int) -> int:
    return MENTAL_TYPE_BIT | FRAME_WORD_FLAG | (frame_index & 0xFF)


def _delta_payload(delta_ms: int) -> int:
    return MENTAL_TYPE_BIT | DELTA_WORD_FLAG | (delta_ms & 0xFF)


def _is_frame_word(mode: int, version: int, payload: int) -> bool:
    return (
        mode == MODE_CONTROL
        and version == _wire_control_version(VERSION_FRAME)
        and (payload & MENTAL_TYPE_BIT) != 0
        and (payload & FRAME_WORD_FLAG) != 0
    )


def _is_delta_word(mode: int, version: int, payload: int) -> bool:
    return (
        mode == MODE_CONTROL
        and version == _wire_control_version(VERSION_DELTA)
        and (payload & MENTAL_TYPE_BIT) != 0
        and (payload & DELTA_WORD_FLAG) != 0
    )


def _run_length_encode(directions: List[int], max_run: int = 32) -> List[tuple[int, int]]:
    if not directions:
        return []

    runs: List[tuple[int, int]] = []
    current = directions[0]
    length = 1

    for direction in directions[1:]:
        if direction == current and length < max_run:
            length += 1
            continue
        runs.append((current, length))
        current = direction
        length = 1
    runs.append((current, length))

    return runs


def _extract_stroke_fields(
    stroke: MentalStroke,
) -> tuple[int, int, DirectionProfile, List[int]]:
    move_x = 0
    move_y = 0
    profile = stroke.direction_profile
    modulus = direction_modulus(profile)
    draw_dirs: List[int] = []

    for cmd in stroke.commands:
        if _command_is_move(cmd):
            move_x = int(getattr(cmd, "x")) & 0xFF
            move_y = int(getattr(cmd, "y")) & 0xFF
        elif _command_is_draw(cmd):
            direction = int(getattr(cmd, "direction"))
            cmd_profile = getattr(cmd, "profile", profile)
            if cmd_profile != profile:
                raise ValueError(
                    "draw command profile does not match stroke profile: "
                    f"{cmd_profile} != {profile}"
                )
            if direction < 0 or direction >= modulus:
                raise ValueError(
                    f"direction must be in [0,{modulus - 1}] for profile {profile.name}, got {direction}"
                )
            draw_dirs.append(direction)
        else:
            raise TypeError(f"unsupported stroke command: {cmd!r}")

    return move_x, move_y, profile, draw_dirs


def _pack_mental_strokes_raw(
    strokes: Iterable[MentalStroke], metadata: Optional[dict] = None
) -> List[int]:
    """Pack mental strokes as per-step draw words (legacy/raw transport)."""

    words: List[int] = []
    global_frame_index = None
    global_delta_ms = None
    if metadata is not None:
        global_frame_index = metadata.get("frame_index")
        global_delta_ms = metadata.get("delta_ms")

    for stroke in strokes:
        if not isinstance(stroke, MentalStroke):
            raise TypeError(f"expected MentalStroke, got {type(stroke)!r}")

        move_x, move_y, profile, draw_dirs = _extract_stroke_fields(stroke)

        if len(draw_dirs) > 255:
            raise ValueError("stroke too long for v1 length field (max 255 draw commands)")

        frame_index = stroke.frame_index
        if frame_index is None:
            frame_index = global_frame_index
        if frame_index is not None and not 0 <= int(frame_index) <= 255:
            raise ValueError(f"frame_index must be in [0,255], got {frame_index}")

        delta_ms = stroke.delta_ms
        if metadata is not None and "delta_ms" in metadata and stroke.delta_ms == 0:
            delta_ms = int(global_delta_ms)
        if not 0 <= int(delta_ms) <= 255:
            raise ValueError(f"delta_ms must be in [0,255], got {delta_ms}")

        words.append(_build_word(MODE_CONTROL, VERSION_HEADER, _header_payload(stroke)))
        words.append(_build_word(MODE_CONTROL, VERSION_X, MENTAL_TYPE_BIT | move_x))
        words.append(_build_word(MODE_CONTROL, VERSION_Y, MENTAL_TYPE_BIT | move_y))
        words.append(
            _build_word(MODE_CONTROL, VERSION_LEN, MENTAL_TYPE_BIT | len(draw_dirs))
        )

        if frame_index is not None:
            words.append(
                _build_word(
                    MODE_CONTROL,
                    _wire_control_version(VERSION_FRAME),
                    _frame_payload(int(frame_index)),
                )
            )

        words.append(
            _build_word(
                MODE_CONTROL,
                _wire_control_version(VERSION_DELTA),
                _delta_payload(int(delta_ms)),
            )
        )

        for direction in draw_dirs:
            words.append(
                _build_word(MODE_DRAW, DRAW_VERSION_RAW, _draw_payload(direction, profile))
            )

    return words


def pack_mental_strokes(
    strokes: Iterable[MentalStroke], metadata: Optional[dict] = None
) -> List[int]:
    """Pack mental strokes; RLE is default transport for Augmentation Phase 2."""

    use_rle = True
    if metadata is not None and "use_rle" in metadata:
        use_rle = bool(metadata["use_rle"])
    if use_rle:
        return pack_mental_strokes_rle(strokes, metadata=metadata)
    return _pack_mental_strokes_raw(strokes, metadata=metadata)


def unpack_mental_words(words: Iterable[int]) -> tuple[dict | None, List[MentalStroke]]:
    """Unpack mental words, auto-detecting raw vs RLE draw encoding."""

    data = _coerce_int_words(words)
    if not data:
        return None, []

    strokes: List[MentalStroke] = []
    frame_indices: List[int | None] = []
    delta_values: List[int] = []
    encodings: List[str] = []
    i = 0

    while i < len(data):
        mode, version, payload = _extract_fields(int(data[i]))

        if mode != MODE_CONTROL or version != VERSION_HEADER:
            i += 1
            continue
        if (payload & MENTAL_TYPE_BIT) == 0:
            i += 1
            continue

        if i + 3 >= len(data):
            break

        (
            form_class,
            symmetry,
            direction_profile,
            spatial_frequency,
            drift_speed,
        ) = _parse_header_payload(payload)

        mx_mode, mx_version, mx_payload = _extract_fields(int(data[i + 1]))
        my_mode, my_version, my_payload = _extract_fields(int(data[i + 2]))
        ln_mode, ln_version, ln_payload = _extract_fields(int(data[i + 3]))

        if (
            mx_mode != MODE_CONTROL
            or mx_version != VERSION_X
            or (mx_payload & MENTAL_TYPE_BIT) == 0
            or my_mode != MODE_CONTROL
            or my_version != VERSION_Y
            or (my_payload & MENTAL_TYPE_BIT) == 0
            or ln_mode != MODE_CONTROL
            or ln_version != VERSION_LEN
            or (ln_payload & MENTAL_TYPE_BIT) == 0
        ):
            # malformed control run; resync by moving forward one word
            i += 1
            continue

        x = mx_payload & 0xFF
        y = my_payload & 0xFF
        unit_count = ln_payload & 0xFF

        cursor = i + 4
        frame_index: int | None = None
        delta_ms = 0
        seen_frame = False
        seen_delta = False
        while cursor < len(data):
            c_mode, c_version, c_payload = _extract_fields(int(data[cursor]))
            if not seen_frame and _is_frame_word(c_mode, c_version, c_payload):
                frame_index = c_payload & 0xFF
                seen_frame = True
                cursor += 1
                continue
            if not seen_delta and _is_delta_word(c_mode, c_version, c_payload):
                delta_ms = c_payload & 0xFF
                seen_delta = True
                cursor += 1
                continue
            break

        commands = [MoveTo(x, y)]
        available = min(unit_count, len(data) - cursor)
        consumed_units = 0
        encoding = "raw"
        for j in range(available):
            d_mode, d_version, d_payload = _extract_fields(int(data[cursor + j]))
            if d_mode != MODE_DRAW or (d_payload & MENTAL_TYPE_BIT) == 0:
                break

            is_rle = d_version == DRAW_VERSION_RLE or (d_payload & LEGACY_RLE_RUN_FLAG) != 0
            if is_rle:
                encoding = "rle"
                if direction_profile == DirectionProfile.D6_12:
                    direction = (d_payload >> 4) & 0xF
                    if direction >= 12:
                        break
                    run_length = (d_payload & 0x0F) + 1
                else:
                    direction = (d_payload >> 5) & 0x7
                    run_length = (d_payload & 0x1F) + 1
                commands.extend(
                    [DrawDir(direction, profile=direction_profile)] * run_length
                )
            else:
                if direction_profile == DirectionProfile.D6_12:
                    direction = (d_payload >> 4) & 0xF
                    if direction >= 12:
                        break
                else:
                    direction = (d_payload >> 5) & 0x7
                commands.append(DrawDir(direction, profile=direction_profile))
            consumed_units += 1

        strokes.append(
            MentalStroke(
                commands=commands,
                form_class=form_class,
                symmetry=symmetry,
                direction_profile=direction_profile,
                spatial_frequency=spatial_frequency,
                drift_speed=drift_speed,
                frame_index=frame_index,
                delta_ms=delta_ms,
            )
        )
        frame_indices.append(frame_index)
        delta_values.append(delta_ms)
        encodings.append(encoding)

        i = cursor + consumed_units

    metadata: dict[str, object] = {"stroke_count": len(strokes)}
    if any(idx is not None for idx in frame_indices):
        metadata["frame_indices"] = frame_indices
    if any(delta != 0 for delta in delta_values):
        metadata["delta_ms"] = delta_values
    if encodings:
        metadata["encoding"] = encodings[0] if len(set(encodings)) == 1 else "mixed"
    return metadata, strokes


def pack_mental_strokes_rle(
    strokes: Iterable[MentalStroke], metadata: Optional[dict] = None
) -> List[int]:
    """Pack mental strokes using run-length encoding for draw directions."""

    words: List[int] = []
    global_frame_index = None
    global_delta_ms = None
    if metadata is not None:
        global_frame_index = metadata.get("frame_index")
        global_delta_ms = metadata.get("delta_ms")

    for stroke in strokes:
        if not isinstance(stroke, MentalStroke):
            raise TypeError(f"expected MentalStroke, got {type(stroke)!r}")

        move_x, move_y, profile, draw_dirs = _extract_stroke_fields(stroke)
        max_run = 16 if profile == DirectionProfile.D6_12 else 32
        runs = _run_length_encode(draw_dirs, max_run=max_run)

        if len(runs) > 255:
            raise ValueError("stroke too long for v1 RLE run-count field (max 255 runs)")

        frame_index = stroke.frame_index
        if frame_index is None:
            frame_index = global_frame_index
        if frame_index is not None and not 0 <= int(frame_index) <= 255:
            raise ValueError(f"frame_index must be in [0,255], got {frame_index}")

        delta_ms = stroke.delta_ms
        if metadata is not None and "delta_ms" in metadata and stroke.delta_ms == 0:
            delta_ms = int(global_delta_ms)
        if not 0 <= int(delta_ms) <= 255:
            raise ValueError(f"delta_ms must be in [0,255], got {delta_ms}")

        words.append(_build_word(MODE_CONTROL, VERSION_HEADER, _header_payload(stroke)))
        words.append(_build_word(MODE_CONTROL, VERSION_X, MENTAL_TYPE_BIT | move_x))
        words.append(_build_word(MODE_CONTROL, VERSION_Y, MENTAL_TYPE_BIT | move_y))
        words.append(_build_word(MODE_CONTROL, VERSION_LEN, MENTAL_TYPE_BIT | len(runs)))

        if frame_index is not None:
            words.append(
                _build_word(
                    MODE_CONTROL,
                    _wire_control_version(VERSION_FRAME),
                    _frame_payload(int(frame_index)),
                )
            )
        words.append(
            _build_word(
                MODE_CONTROL,
                _wire_control_version(VERSION_DELTA),
                _delta_payload(int(delta_ms)),
            )
        )

        for direction, run_length in runs:
            if profile == DirectionProfile.D6_12:
                payload = (
                    MENTAL_TYPE_BIT
                    | ((direction & 0xF) << 4)
                    | ((run_length - 1) & 0x0F)
                )
            else:
                payload = (
                    MENTAL_TYPE_BIT
                    | ((direction & 0x7) << 5)
                    | ((run_length - 1) & 0x1F)
                )
            words.append(_build_word(MODE_DRAW, DRAW_VERSION_RLE, payload))

    return words


def unpack_mental_words_rle(words: Iterable[int]) -> tuple[dict | None, List[MentalStroke]]:
    """Unpack words intended for RLE transport (auto-detected parser)."""

    metadata, strokes = unpack_mental_words(words)
    if metadata is None:
        return None, []
    if "encoding" not in metadata:
        metadata["encoding"] = "rle"
    return metadata, strokes
