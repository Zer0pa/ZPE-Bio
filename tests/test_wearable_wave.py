"""Unit tests for wearable-wave helper functions."""

from __future__ import annotations

import numpy as np

from zpe_bio.codec import CodecMode
from zpe_bio.wearable_wave import confusion_metrics, multiaxis_imu_metrics, roundtrip_metrics


def test_roundtrip_metrics_contract() -> None:
    signal = np.sin(np.linspace(0.0, 8.0 * np.pi, num=512, dtype=np.float64))
    _encoded, reconstructed, payload = roundtrip_metrics(
        signal,
        signal_type="ecg",
        mode=CodecMode.CLINICAL,
        thr_mode="adaptive_rms",
    )

    assert reconstructed.shape[0] == signal.shape[0]
    assert payload["samples"] == signal.shape[0]
    assert payload["raw_bytes"] > 0
    assert payload["zpe_bytes_est"] > 0
    assert payload["compression_ratio"] > 0
    assert payload["snr_db"] >= 0


def test_multiaxis_imu_metrics_contract() -> None:
    t = np.linspace(0.0, 6.0 * np.pi, num=1024, dtype=np.float64)
    axes = np.stack(
        [
            np.sin(t),
            np.cos(t),
            0.5 * np.sin(2.0 * t),
            0.5 * np.cos(2.0 * t),
            0.25 * np.sin(4.0 * t),
            0.25 * np.cos(4.0 * t),
        ],
        axis=1,
    )
    payload = multiaxis_imu_metrics(axes, threshold=0.1, step=0.1)

    assert payload["axes"] == 6
    assert payload["samples"] == 1024
    assert payload["aggregate"]["raw_bytes_float32"] == 1024 * 6 * 4
    assert payload["aggregate"]["zpe_bytes_est"] > 0
    assert payload["aggregate"]["compression_ratio_vs_float32"] > 0


def test_confusion_metrics_values() -> None:
    labels = np.array([1, 1, 1, 0, 0, 0], dtype=np.int32)
    preds = np.array([1, 1, 0, 0, 1, 0], dtype=np.int32)
    payload = confusion_metrics(labels, preds)

    assert payload["tp"] == 2
    assert payload["tn"] == 2
    assert payload["fp"] == 1
    assert payload["fn"] == 1
    assert payload["sensitivity"] == 0.666667
    assert payload["specificity"] == 0.666667
    assert payload["precision"] == 0.666667
    assert payload["recall"] == 0.666667

