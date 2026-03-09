from enum import IntEnum


class Mode(IntEnum):
    NORMAL = 0
    ESCAPE = 1
    EXTENSION = 2
    RESERVED = 3


class StrokeState(IntEnum):
    ABSENT = 0
    SHORT = 1
    LONG = 2
    DOUBLE = 3  # doubled stroke or dotted/dashed variant


# Style bits (b0..b3)
STYLE_CURVE = 1 << 0
STYLE_DOT = 1 << 1
STYLE_SERIF = 1 << 2
STYLE_LOOP = 1 << 3


DEFAULT_VERSION = 0
WORD_BITS = 20
WORD_MASK = (1 << WORD_BITS) - 1
PAYLOAD_16_MASK = 0xFFFF
# Deprecated alias: this is a full 20-bit word mask, not a 16-bit payload mask.
PAYLOAD_MASK = WORD_MASK
