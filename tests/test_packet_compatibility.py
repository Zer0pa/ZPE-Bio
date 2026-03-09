"""Wave-1 packet compatibility fixtures and strict version handling tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zpe_bio.multimodal.taste.fusion_scheduler import (
    FusionScheduler,
    UnsupportedPacketVersionError,
)


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "wave1_golden_packets.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_golden_packet_fixture_contract() -> None:
    fixture = _load_fixture()
    assert fixture["contract_version"] == "wave1.0"

    for case in fixture["cases"]:
        scheduler = FusionScheduler()
        stats = scheduler.ingest_stream(case["words"], strict_versions=True)
        fused = scheduler.fuse_zlayer_events()
        expected = case["expected"]

        assert stats["taste_packets"] == expected["taste_packets"]
        assert stats["smell_packets"] == expected["smell_packets"]
        assert stats["touch_packets"] == expected["touch_packets"]
        assert len(fused) == expected["fused_events"]


def test_unsupported_packet_version_strict_error() -> None:
    # smell bit + unsupported version=1 should raise in strict mode
    bad_smell_word = (0b10 << 18) | (1 << 16) | (0x0200 | (0 << 6) | 0x01)
    scheduler = FusionScheduler()
    with pytest.raises(UnsupportedPacketVersionError):
        scheduler.ingest_stream([bad_smell_word], strict_versions=True)


def test_unsupported_packet_version_non_strict_is_tolerated() -> None:
    bad_smell_word = (0b10 << 18) | (1 << 16) | (0x0200 | (0 << 6) | 0x01)
    scheduler = FusionScheduler()
    stats = scheduler.ingest_stream([bad_smell_word], strict_versions=False)
    assert stats["smell_packets"] == 0
