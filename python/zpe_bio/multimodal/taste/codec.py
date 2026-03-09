from __future__ import annotations

from typing import Iterable, List, Optional

from .pack import pack_taste_strokes, pack_taste_zlayered, unpack_taste_words
from .taste_space import synthetic_taste_stroke, zlayered_event_from_vector
from .types import TasteQuality, TasteStroke


def encode_taste_strokes(
    strokes: Iterable[TasteStroke],
    metadata: Optional[dict] = None,
) -> List[int]:
    """High-level entrypoint for gustatory encoding."""
    return pack_taste_strokes(strokes=strokes, metadata=metadata)


def decode_taste_words(words: Iterable[int]) -> tuple[dict | None, List[TasteStroke]]:
    """High-level entrypoint for gustatory decoding."""
    return unpack_taste_words(words)


def encode_synthetic_quality_sequence(qualities: Iterable[TasteQuality]) -> List[int]:
    strokes = [synthetic_taste_stroke(q) for q in qualities]
    return pack_taste_strokes(strokes, metadata=None)


def encode_real_taste_profile(profile_dict: dict, adaptive: bool = False) -> List[int]:
    """Encode one real-data taste profile dictionary into Z-layer words."""
    if not isinstance(profile_dict, dict):
        raise TypeError("profile_dict must be a dict")

    quality_vector = profile_dict.get("quality_vector")
    temporal_directions = profile_dict.get("temporal_directions")
    intensity_end = profile_dict.get("intensity_end")
    flavor_link = profile_dict.get("flavor_link")

    if quality_vector is None:
        raise ValueError("profile_dict missing quality_vector")
    if temporal_directions is None:
        raise ValueError("profile_dict missing temporal_directions")

    event = zlayered_event_from_vector(
        quality_vector=quality_vector,
        temporal_directions=tuple(int(v) for v in temporal_directions),
        intensity_end=None if intensity_end is None else int(intensity_end),
        flavor_link=None if flavor_link is None else tuple(int(v) for v in flavor_link),
    )
    if not adaptive:
        return pack_taste_zlayered([event])

    try:
        return pack_taste_zlayered([event], adaptive=True)
    except TypeError:
        # Tier A compatibility: adaptive path is introduced in Tier B.
        return pack_taste_zlayered([event])
