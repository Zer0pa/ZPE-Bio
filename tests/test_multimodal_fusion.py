"""Fusion scheduler regression tests for taste+smell+touch stream extraction."""

from __future__ import annotations

from zpe_bio.multimodal.smell import OdorCategory, pack_odor_strokes, synthetic_sniff_stroke
from zpe_bio.multimodal.taste import (
    FusionScheduler,
    TasteQuality,
    pack_taste_zlayered,
    synthetic_quality_profiles,
    zlayered_event_from_vector,
)


def _touch_word(version: int, payload: int) -> int:
    return (0b10 << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)


def _synthetic_touch_packet() -> list[int]:
    # Header must be extension mode + version 1 + touch type bit + 0x001F tag.
    header = _touch_word(1, 0x0800 | 0x001F)
    data_0 = _touch_word(0, 0x0800 | 0x0020)
    data_1 = _touch_word(0, 0x0800 | 0x0030)
    return [header, data_0, data_1]


def test_fusion_scheduler_extracts_trimodal_packets() -> None:
    taste_event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.UMAMI],
        flavor_link=(2, 2),
    )
    taste_words = pack_taste_zlayered([taste_event], adaptive=True)
    smell_words = pack_odor_strokes([synthetic_sniff_stroke(OdorCategory.WOODY_EARTHY)])
    touch_words = _synthetic_touch_packet()

    stream = taste_words + smell_words + touch_words
    scheduler = FusionScheduler()
    stats = scheduler.ingest_stream(stream)
    fused_events = scheduler.fuse_zlayer_events()

    assert stats["taste_packets"] == 1
    assert stats["smell_packets"] == 1
    assert stats["touch_packets"] == 1
    assert len(fused_events) == 1
    assert len(scheduler.emit_fused_words()) > 0


def test_fusion_scheduler_ignores_incomplete_tail_packets() -> None:
    scheduler = FusionScheduler()

    # Incomplete smell packet: header A + header B that claims one step, but no step word.
    incomplete_smell = [
        (0b10 << 18) | (0 << 16) | (0x0200 | (0 << 6) | 0x01),
        (0b10 << 18) | (0 << 16) | (0x0200 | (1 << 6) | 0x01),
    ]
    # Incomplete touch packet: header only.
    incomplete_touch = [(0b10 << 18) | (1 << 16) | (0x0800 | 0x001F)]

    stats = scheduler.ingest_stream(incomplete_smell + incomplete_touch)
    assert stats["smell_packets"] == 0
    assert stats["touch_packets"] == 0
    assert scheduler.fuse_zlayer_events() == []


def test_fusion_scheduler_tolerates_malformed_integer_words() -> None:
    taste_event = zlayered_event_from_vector(
        quality_vector=synthetic_quality_profiles()[TasteQuality.SWEET],
        flavor_link=(1, 1),
    )
    stream = (
        [0, 1, 3, -1, "bad", None]
        + pack_taste_zlayered([taste_event], adaptive=True)
        + pack_odor_strokes([synthetic_sniff_stroke(OdorCategory.FRUITY)])
        + _synthetic_touch_packet()
        + [0x3FFFFF]
    )

    scheduler = FusionScheduler()
    stats = scheduler.ingest_stream(stream)
    fused_events = scheduler.fuse_zlayer_events()

    assert stats["taste_packets"] == 1
    assert stats["smell_packets"] == 1
    assert stats["touch_packets"] == 1
    assert len(fused_events) == 1
