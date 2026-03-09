"""Unit tests for core Python codec behavior."""

import numpy as np

from zpe_bio.codec import CodecMode, compute_prd, compute_rmse, decode, encode, quantise_ecg


def test_quantise_ecg_stable_signal() -> None:
    assert quantise_ecg(0.0005, 0.001) == 0


def test_quantise_ecg_moderate_increase() -> None:
    assert quantise_ecg(0.0015, 0.001) == 1


def test_quantise_ecg_acute_increase() -> None:
    assert quantise_ecg(0.005, 0.001) == 2


def test_roundtrip_clinical_high_fidelity() -> None:
    signal = np.sin(2 * np.pi * np.linspace(0, 1, 250))
    encoded = encode(signal, mode=CodecMode.CLINICAL)
    reconstructed = decode(encoded)

    prd = compute_prd(signal, reconstructed)
    rmse = compute_rmse(signal, reconstructed)
    assert prd < 1.0
    assert rmse < 0.01


def test_transport_mode_compression() -> None:
    signal = np.sin(2 * np.pi * np.linspace(0, 1, 250))
    encoded = encode(signal, mode=CodecMode.TRANSPORT)
    assert encoded.compression_ratio > 3.0


def test_clinical_mode_determinism() -> None:
    signal = np.random.default_rng(42).normal(size=100)
    first = encode(signal, mode=CodecMode.CLINICAL)
    second = encode(signal, mode=CodecMode.CLINICAL)
    assert first.tokens == second.tokens
    assert first.start_value == second.start_value
