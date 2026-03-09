"""Regression tests for transplanted taste codec modules."""

from __future__ import annotations

from zpe_bio.multimodal.taste import (
    TasteQuality,
    TasteZLevel,
    pack_taste_strokes,
    pack_taste_zlayered,
    synthetic_quality_profiles,
    synthetic_taste_stroke,
    unpack_taste_words,
    unpack_taste_zlayered,
    unpack_taste_zlevel_word,
    zlayered_event_from_vector,
)


def test_taste_pack_unpack_roundtrip_and_type_bits() -> None:
    strokes = [synthetic_taste_stroke(quality) for quality in TasteQuality]
    words = pack_taste_strokes(strokes)
    metadata, recovered = unpack_taste_words(words)

    assert metadata is not None
    assert len(recovered) == len(strokes)
    assert pack_taste_strokes(strokes) == words

    for src, dst in zip(strokes, recovered):
        assert src.dominant_quality == dst.dominant_quality
        assert src.quality_vector == dst.quality_vector
        assert [cmd.direction for cmd in src.commands[1:]] == [cmd.direction for cmd in dst.commands[1:]]

    for word in words:
        assert (word & 0x0400) != 0
        assert (word & (0x8000 | 0x4000 | 0x2000 | 0x1000 | 0x0800)) == 0


def test_taste_adaptive_temporal_codebook_selects_coarse_and_fine() -> None:
    vector = synthetic_quality_profiles()[TasteQuality.SWEET]
    coarse_event = zlayered_event_from_vector(
        quality_vector=vector,
        temporal_directions=(0, 0, 2, 2, 4, 4, 6, 6),
    )
    fine_event = zlayered_event_from_vector(
        quality_vector=vector,
        temporal_directions=(1, 3, 5, 7, 1, 3, 5, 7),
    )

    coarse_words = pack_taste_zlayered([coarse_event], adaptive=True)
    fine_words = pack_taste_zlayered([fine_event], adaptive=True)
    _coarse_meta, coarse_decoded = unpack_taste_zlayered(coarse_words)
    _fine_meta, fine_decoded = unpack_taste_zlayered(fine_words)

    assert coarse_decoded[0].temporal_directions == coarse_event.temporal_directions
    assert fine_decoded[0].temporal_directions == fine_event.temporal_directions

    coarse_level, coarse_intensity = unpack_taste_zlevel_word(coarse_words[1])  # intensity word
    fine_level, fine_intensity = unpack_taste_zlevel_word(fine_words[1])  # intensity word
    assert coarse_level == TasteZLevel.INTENSITY
    assert fine_level == TasteZLevel.INTENSITY
    assert (coarse_intensity & 0x80) != 0
    assert (fine_intensity & 0x80) == 0
