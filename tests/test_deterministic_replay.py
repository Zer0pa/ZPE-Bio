"""Wave-1 deterministic replay checks for core and multimodal lanes."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from zpe_bio.bio_wave2 import build_multimodal_stream
from zpe_bio.codec import CodecMode, encode
from zpe_bio.multimodal.taste import FusionScheduler


def test_seeded_core_encode_replay_deterministic() -> None:
    rng = np.random.default_rng(20260220)
    signal = np.cumsum(rng.normal(0.0, 0.2, size=1024))

    first = encode(
        signal,
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
        threshold=0.05,
        step=0.05,
        signal_type="ecg",
    ).tokens
    second = encode(
        signal,
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
        threshold=0.05,
        step=0.05,
        signal_type="ecg",
    ).tokens
    assert first == second


def test_fusion_scheduler_replay_deterministic() -> None:
    words = [
        525344,
        590904,
        656457,
        656384,
        656600,
        721938,
        524827,
        524908,
        524944,
        524945,
        524962,
        524979,
        591903,
        526368,
        526384,
    ]

    first = FusionScheduler()
    first.ingest_stream(words, strict_versions=True)
    first.fuse_zlayer_events()
    first_emit = first.emit_fused_words()

    second = FusionScheduler()
    second.ingest_stream(words, strict_versions=True)
    second.fuse_zlayer_events()
    second_emit = second.emit_fused_words()

    assert first_emit == second_emit


def test_multimodal_stream_hash_replay_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    first = build_multimodal_stream(
        ecg_record_id="100",
        lead_index=0,
        ecg_samples=512,
        eeg_path=None,
        eeg_channels=2,
        eeg_samples=256,
        synthetic_eeg=True,
    )
    second = build_multimodal_stream(
        ecg_record_id="100",
        lead_index=0,
        ecg_samples=512,
        eeg_path=None,
        eeg_channels=2,
        eeg_samples=256,
        synthetic_eeg=True,
    )

    assert (root / "validation" / "datasets" / "mitdb").exists()
    assert first["stream_hash"] == second["stream_hash"]
    assert first["replay_hash_stable"] is True
    assert second["replay_hash_stable"] is True
