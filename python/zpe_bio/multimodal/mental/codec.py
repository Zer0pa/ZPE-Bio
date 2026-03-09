from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from .pack import pack_mental_strokes, unpack_mental_words
from .types import MentalStroke


def encode_mental(
    strokes: Iterable[MentalStroke], metadata: Optional[dict] = None
) -> List[int]:
    """High-level encode helper for mental modality streams."""

    return pack_mental_strokes(strokes, metadata=metadata)


def decode_mental(words: Iterable[int]) -> Tuple[dict | None, List[MentalStroke]]:
    """High-level decode helper for mental modality streams."""

    return unpack_mental_words(words)
