from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .pack import unpack_taste_zlayered, unpack_taste_zlevel_word
from .types import TasteZLevel, ZLayeredTasteEvent

TASTE_TYPE_BIT = 0x0400
SMELL_TYPE_BIT = 0x0200
TOUCH_TYPE_BIT = 0x0800

MODE_EXTENSION = 0b10
DEFAULT_VERSION = 0
TOUCH_HEADER_VERSION = 1
TOUCH_DATA_VERSION = 0
TOUCH_HEADER_TAG = 0x001F


class UnsupportedPacketVersionError(ValueError):
    """Raised when a packet uses a known marker with unsupported version bits."""

    def __init__(self, marker: str, version: int, index: int) -> None:
        super().__init__(
            f"unsupported {marker} packet version={version} at word_index={index}"
        )
        self.marker = marker
        self.version = version
        self.index = index


@dataclass(frozen=True)
class FlavorEvent:
    index: int
    taste_words: tuple[int, ...]
    smell_words: tuple[int, ...]
    touch_words: tuple[int, ...]
    taste_event: ZLayeredTasteEvent

    def signature(self) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        return (self.taste_words, self.smell_words, self.touch_words)


class FusionScheduler:
    """Deterministic multimodal fusion scheduler for taste+smell+touch streams."""

    def __init__(self) -> None:
        self._raw_stream: list[int] = []
        self._taste_packets: list[list[int]] = []
        self._smell_packets: list[list[int]] = []
        self._touch_packets: list[list[int]] = []
        self._fused_events: list[FlavorEvent] = []

    def ingest_stream(self, words: Iterable[int], strict_versions: bool = False) -> dict[str, int]:
        new_words: list[int] = []
        for word in words:
            try:
                new_words.append(int(word))
            except (TypeError, ValueError):
                continue
        if strict_versions:
            validate_packet_versions(new_words)
        self._raw_stream.extend(new_words)

        self._taste_packets = _extract_taste_packets(self._raw_stream)
        self._smell_packets = _extract_smell_packets(self._raw_stream)
        self._touch_packets = _extract_touch_packets(self._raw_stream)

        return {
            "total_words": len(self._raw_stream),
            "taste_packets": len(self._taste_packets),
            "smell_packets": len(self._smell_packets),
            "touch_packets": len(self._touch_packets),
        }

    def fuse_zlayer_events(self) -> list[FlavorEvent]:
        fused: list[FlavorEvent] = []
        boundary = min(len(self._taste_packets), len(self._smell_packets), len(self._touch_packets))

        for index in range(boundary):
            taste_words = self._taste_packets[index]
            _meta, decoded_taste = unpack_taste_zlayered(taste_words)
            if not decoded_taste:
                continue

            fused.append(
                FlavorEvent(
                    index=index,
                    taste_words=tuple(taste_words),
                    smell_words=tuple(self._smell_packets[index]),
                    touch_words=tuple(self._touch_packets[index]),
                    taste_event=decoded_taste[0],
                )
            )

        self._fused_events = fused
        return list(fused)

    def emit_fused_words(self) -> list[int]:
        emitted: list[int] = []
        for event in self._fused_events:
            emitted.extend(event.taste_words)
            emitted.extend(event.smell_words)
            emitted.extend(event.touch_words)
        return emitted

    @property
    def fused_events(self) -> list[FlavorEvent]:
        return list(self._fused_events)



def _word_mode(word: int) -> int:
    return (word >> 18) & 0x3


def _word_version(word: int) -> int:
    return (word >> 16) & 0x3


def _word_payload(word: int) -> int:
    return word & 0xFFFF


def _is_extension(word: int) -> bool:
    return _word_mode(word) == MODE_EXTENSION


def _is_smell_word(word: int) -> bool:
    return _is_extension(word) and (word & SMELL_TYPE_BIT) != 0


def _is_touch_word(word: int) -> bool:
    return _is_extension(word) and (word & TOUCH_TYPE_BIT) != 0


def _is_touch_header(word: int) -> bool:
    return _is_touch_word(word) and _word_version(word) == TOUCH_HEADER_VERSION and (word & TOUCH_HEADER_TAG) == TOUCH_HEADER_TAG


def _extract_taste_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        first = unpack_taste_zlevel_word(words[index])
        if first is None or first[0] != TasteZLevel.QUALITY:
            index += 1
            continue

        if index + 3 >= len(words):
            break

        second = unpack_taste_zlevel_word(words[index + 1])
        t0 = unpack_taste_zlevel_word(words[index + 2])
        t1 = unpack_taste_zlevel_word(words[index + 3])
        if (
            second is None
            or second[0] != TasteZLevel.INTENSITY
            or t0 is None
            or t0[0] != TasteZLevel.TEMPORAL
            or t1 is None
            or t1[0] != TasteZLevel.TEMPORAL
        ):
            index += 1
            continue

        use_coarse = (second[1] & 0x80) != 0
        consumed = 4

        if not use_coarse:
            if index + 4 >= len(words):
                break
            t2 = unpack_taste_zlevel_word(words[index + 4])
            if t2 is None or t2[0] != TasteZLevel.TEMPORAL:
                index += 1
                continue
            consumed = 5

        maybe_flavor_index = index + consumed
        if maybe_flavor_index < len(words):
            maybe_flavor = unpack_taste_zlevel_word(words[maybe_flavor_index])
            if maybe_flavor is not None and maybe_flavor[0] == TasteZLevel.FLAVOR:
                consumed += 1

        packets.append(words[index:index + consumed])
        index += consumed

    return packets


def _extract_smell_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        word = words[index]
        if not _is_smell_word(word) or _word_version(word) != DEFAULT_VERSION:
            index += 1
            continue

        payload = _word_payload(word)
        op = (payload >> 6) & 0x3
        if op != 0:  # smell header A
            index += 1
            continue

        if index + 1 >= len(words):
            break

        second_word = words[index + 1]
        if not _is_smell_word(second_word) or _word_version(second_word) != DEFAULT_VERSION:
            index += 1
            continue

        payload_b = _word_payload(second_word)
        op_b = (payload_b >> 6) & 0x3
        if op_b != 1:  # smell header B
            index += 1
            continue

        step_count = payload_b & 0x7
        consumed = 2
        cursor = index + 2

        while consumed < 2 + step_count and cursor < len(words):
            step_word = words[cursor]
            if not _is_smell_word(step_word) or _word_version(step_word) != DEFAULT_VERSION:
                break
            step_op = (_word_payload(step_word) >> 6) & 0x3
            if step_op != 2:
                break
            consumed += 1
            cursor += 1

        # Do not emit partial packets. Keep a tail fragment for later ingestion.
        if consumed != 2 + step_count:
            break

        packets.append(words[index:index + consumed])
        index += consumed

    return packets


def _extract_touch_packets(words: list[int]) -> list[list[int]]:
    packets: list[list[int]] = []
    index = 0

    while index < len(words):
        header = words[index]
        if not _is_touch_header(header):
            index += 1
            continue

        cursor = index + 1
        while cursor < len(words):
            word = words[cursor]
            if not _is_touch_word(word):
                break
            if _is_touch_header(word):
                break
            if _word_version(word) != TOUCH_DATA_VERSION:
                break
            cursor += 1

        # Header-only touch fragments are not valid packets.
        if cursor == index + 1:
            if cursor >= len(words):
                break
            index += 1
            continue

        packets.append(words[index:cursor])
        index = cursor

    return packets


def validate_packet_versions(words: Iterable[int]) -> None:
    """Validate extension-word versions for known packet markers.

    Raises UnsupportedPacketVersionError on known markers with unsupported version.
    """
    for index, raw in enumerate(words):
        if not isinstance(raw, int):
            continue
        word = int(raw)
        if not _is_extension(word):
            continue
        version = _word_version(word)
        payload = _word_payload(word)

        if payload & SMELL_TYPE_BIT:
            if version != DEFAULT_VERSION:
                raise UnsupportedPacketVersionError("smell", version, index)
            continue

        if payload & TOUCH_TYPE_BIT:
            # Touch header packets are versioned separately from touch data words.
            if (payload & TOUCH_HEADER_TAG) == TOUCH_HEADER_TAG:
                if version != TOUCH_HEADER_VERSION:
                    raise UnsupportedPacketVersionError("touch_header", version, index)
            elif version != TOUCH_DATA_VERSION:
                raise UnsupportedPacketVersionError("touch_data", version, index)
            continue

        if payload & TASTE_TYPE_BIT:
            # Taste z-level words occupy the 2-bit version field (0..3).
            if version not in (0, 1, 2, 3):  # pragma: no cover - defensive
                raise UnsupportedPacketVersionError("taste", version, index)
