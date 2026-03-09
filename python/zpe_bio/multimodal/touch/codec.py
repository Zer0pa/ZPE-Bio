from __future__ import annotations

from typing import Iterable, List, Optional

from .pack import pack_touch_strokes, unpack_touch_words
from .types import TouchStroke


def encode_touch(
    strokes: Iterable[TouchStroke],
    metadata: Optional[dict] = None,
) -> List[int]:
    return pack_touch_strokes(strokes=strokes, metadata=metadata)


def decode_touch(
    words: Iterable[int],
) -> tuple[dict | None, List[TouchStroke]]:
    return unpack_touch_words(words=words)
