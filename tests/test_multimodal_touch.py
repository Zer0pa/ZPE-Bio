"""Regression tests for transplanted touch codec modules."""

from __future__ import annotations

from zpe_bio.multimodal.touch import (
    BodyRegion,
    DrawDir,
    JointID,
    MoveTo,
    ProprioSample,
    ReceptorType,
    TouchStroke,
    max_angle_error,
    pack_proprioception_samples,
    pack_timed_simultaneous_frame,
    pack_touch_strokes,
    pack_touch_zlayers,
    unpack_proprioception_samples,
    unpack_timed_simultaneous_frame,
    unpack_touch_words,
    unpack_touch_zlayers,
)


def _stroke(
    region: BodyRegion,
    directions: list[int],
    pressures: list[int],
    receptor: ReceptorType = ReceptorType.SA_I,
) -> TouchStroke:
    return TouchStroke(
        commands=[MoveTo(0, 0)] + [DrawDir(direction) for direction in directions],
        receptor=receptor,
        region=region,
        pressure_profile=pressures,
    )


def _directions(stroke: TouchStroke) -> list[int]:
    return [cmd.direction for cmd in stroke.commands if isinstance(cmd, DrawDir)]


def test_touch_pack_unpack_roundtrip_and_type_bits() -> None:
    strokes = [
        _stroke(BodyRegion.THUMB_TIP, [0, 1, 2, 3], [1, 2, 3, 4]),
        _stroke(BodyRegion.PALM_CENTER, [4, 5, 6, 7], [4, 3, 2, 1], ReceptorType.SA_II),
    ]
    words = pack_touch_strokes(strokes)
    metadata, recovered = unpack_touch_words(words)

    assert metadata is not None
    assert metadata["header_words"] == len(strokes)
    assert len(recovered) == len(strokes)

    for src, dst in zip(strokes, recovered):
        assert src.receptor == dst.receptor
        assert src.region == dst.region
        assert src.pressure_profile == dst.pressure_profile
        assert _directions(src) == _directions(dst)

    for word in words:
        assert ((word >> 18) & 0x3) == 0b10
        assert (word & 0x0800) != 0


def test_touch_timed_frame_zlayer_and_proprio_roundtrip() -> None:
    contacts = [
        _stroke(BodyRegion.INDEX_TIP, [0, 4], [2, 2]),
        _stroke(BodyRegion.MIDDLE_TIP, [2, 6], [3, 3]),
    ]
    frame_words = pack_timed_simultaneous_frame(frame_id=3, contacts=contacts, deltas_ms=[5, 9])
    frame_meta, frame_decoded = unpack_timed_simultaneous_frame(frame_words)

    assert frame_meta["cooccurrence_preserved"] is True
    assert [delta for delta, _ in frame_decoded] == [5, 9]
    assert [stroke.region for _, stroke in frame_decoded] == [BodyRegion.INDEX_TIP, BodyRegion.MIDDLE_TIP]

    zlayer_words = pack_touch_zlayers(
        directions=[0, 6, 4],
        pressures=[2, 3, 2],
        region=BodyRegion.PALM_CENTER,
    )
    zlayer_decoded = unpack_touch_zlayers(zlayer_words)
    assert zlayer_decoded["surface"] == [0, 6, 4]
    assert zlayer_decoded["dermal"] == [2, 3, 2]
    assert zlayer_decoded["anatomical_region"] == BodyRegion.PALM_CENTER

    proprio_samples = [
        ProprioSample(joint=JointID.LEFT_ELBOW, angle_deg=30.0, tension_level=2),
        ProprioSample(joint=JointID.RIGHT_ELBOW, angle_deg=36.0, tension_level=3),
        ProprioSample(joint=JointID.SPINE, angle_deg=18.0, tension_level=1),
    ]
    proprio_words = pack_proprioception_samples(proprio_samples)
    proprio_decoded = unpack_proprioception_samples(proprio_words)

    assert [sample.joint for sample in proprio_decoded] == [sample.joint for sample in proprio_samples]
    assert [sample.tension_level for sample in proprio_decoded] == [
        sample.tension_level for sample in proprio_samples
    ]
    assert max_angle_error(proprio_samples, proprio_decoded) <= 2.0


def test_touch_dirty_stream_is_ignored_without_crash() -> None:
    clean_words = pack_touch_strokes([_stroke(BodyRegion.PALM_CENTER, [0, 6, 4], [2, 3, 2])])
    dirty_words = [0, 1, 7, -1, 0x3FFFFF, "bad", None, *clean_words, 0x200000]

    metadata, recovered = unpack_touch_words(dirty_words)
    zlayer_decoded = unpack_touch_zlayers(dirty_words)
    proprio_decoded = unpack_proprioception_samples(dirty_words)

    assert metadata is not None
    assert len(recovered) == 1
    assert recovered[0].region == BodyRegion.PALM_CENTER
    assert isinstance(zlayer_decoded["ignored_words"], int)
    assert isinstance(proprio_decoded, list)
