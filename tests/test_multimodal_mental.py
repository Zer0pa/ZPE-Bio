"""Regression tests for transplanted mental codec modules."""

from __future__ import annotations

from zpe_bio.multimodal.mental import (
    DirectionProfile,
    DrawDir,
    FormClass,
    MentalStroke,
    MoveTo,
    SymmetryOrder,
    ingest_clinical_dataset,
    pack_mental_strokes,
    unpack_mental_words,
    unpack_mental_words_rle,
)


def _stroke(profile: DirectionProfile, delta_ms: int, frame_index: int | None = None) -> MentalStroke:
    if profile == DirectionProfile.COMPASS_8:
        directions = [0, 2, 4, 6]
        symmetry = SymmetryOrder.D4
    else:
        directions = [0, 2, 4, 6, 8, 10]
        symmetry = SymmetryOrder.D6

    return MentalStroke(
        commands=[MoveTo(10, 10)] + [DrawDir(direction, profile=profile) for direction in directions],
        form_class=FormClass.LATTICE,
        symmetry=symmetry,
        direction_profile=profile,
        spatial_frequency=4,
        drift_speed=1,
        frame_index=frame_index,
        delta_ms=delta_ms,
    )


def test_mental_roundtrip_raw_and_rle_with_profile_integrity() -> None:
    strokes = [
        _stroke(DirectionProfile.COMPASS_8, delta_ms=12, frame_index=3),
        _stroke(DirectionProfile.D6_12, delta_ms=24, frame_index=7),
    ]

    rle_words = pack_mental_strokes(strokes, metadata={"use_rle": True})
    raw_words = pack_mental_strokes(strokes, metadata={"use_rle": False})
    rle_meta, rle_recovered = unpack_mental_words(rle_words)
    raw_meta, raw_recovered = unpack_mental_words(raw_words)

    assert rle_meta is not None
    assert raw_meta is not None
    assert rle_meta["encoding"] == "rle"
    assert raw_meta["encoding"] == "raw"
    assert len(rle_recovered) == len(strokes)
    assert len(raw_recovered) == len(strokes)
    assert [stroke.direction_profile for stroke in rle_recovered] == [
        DirectionProfile.COMPASS_8,
        DirectionProfile.D6_12,
    ]
    assert [stroke.delta_ms for stroke in rle_recovered] == [12, 24]
    assert [stroke.frame_index for stroke in rle_recovered] == [3, 7]
    assert rle_words != raw_words

    for word in [*rle_words, *raw_words]:
        mode = (word >> 18) & 0x3
        payload = word & 0x0FFF
        assert mode in (0b10, 0b11)
        assert (payload & 0x0100) != 0


def test_mental_ingest_pipeline_generates_decodable_strokes() -> None:
    entries = [
        {"description": "hexagonal lattice aura"},
        {"description": "rotating spiral tunnel"},
        {"description": "branching cobweb pattern"},
    ]
    results = ingest_clinical_dataset(entries)

    assert len(results) == len(entries)
    assert all(result.stroke.commands for result in results)

    words = pack_mental_strokes([result.stroke for result in results], metadata={"use_rle": True})
    _meta, recovered = unpack_mental_words_rle(words)
    assert len(recovered) == len(entries)


def test_mental_dirty_stream_is_ignored_without_crash() -> None:
    clean_words = pack_mental_strokes(
        [_stroke(DirectionProfile.COMPASS_8, delta_ms=8)],
        metadata={"use_rle": True},
    )
    dirty_words = [0, 1, 3, -1, 0x3FFFFF, "bad", None, *clean_words, 0x200000]

    metadata, recovered = unpack_mental_words(dirty_words)
    rle_metadata, rle_recovered = unpack_mental_words_rle(dirty_words)

    assert metadata is not None
    assert rle_metadata is not None
    assert len(recovered) >= 1
    assert len(rle_recovered) >= 1
