"""Python/Rust token parity checks via FFI."""

from __future__ import annotations

import ctypes
from pathlib import Path

import numpy as np
import pytest

from zpe_bio.codec import CodecMode, encode as python_encode

ROOT = Path(__file__).resolve().parents[1]


class RustToken(ctypes.Structure):
    _fields_ = [
        ("direction", ctypes.c_uint8),
        ("magnitude", ctypes.c_uint8),
        ("count", ctypes.c_uint16),
    ]


def _library_candidates() -> list[Path]:
    return [
        ROOT / "core" / "rust" / "target" / "x86_64-apple-darwin" / "release" / "libzpe_bio_codec.dylib",
        ROOT / "core" / "rust" / "target" / "release" / "libzpe_bio_codec.dylib",
        ROOT / "core" / "rust" / "target" / "release" / "libzpe_bio_codec.so",
    ]


def _load_rust_library() -> ctypes.CDLL | None:
    for candidate in _library_candidates():
        if candidate.exists():
            try:
                return ctypes.CDLL(str(candidate))
            except OSError:
                continue
    return None


LIB = _load_rust_library()

if LIB is not None:
    LIB.zpe_encode.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_uint8,
        ctypes.c_uint8,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(RustToken),
        ctypes.c_size_t,
    ]
    LIB.zpe_encode.restype = ctypes.c_int32


def _rust_encode(
    samples: np.ndarray,
    mode: CodecMode,
    thr_mode: str,
    threshold: float,
    step: float,
) -> list[tuple[int, int, int]]:
    if LIB is None:
        raise RuntimeError("Rust library is not available")

    n_samples = len(samples)
    mode_idx = 0 if mode == CodecMode.TRANSPORT else 1
    thr_mode_idx = 1 if thr_mode == "adaptive_rms" else 0
    capacity = 2048
    out_tokens = (RustToken * capacity)()
    samples_ptr = samples.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    n_tokens = LIB.zpe_encode(
        samples_ptr,
        n_samples,
        mode_idx,
        thr_mode_idx,
        threshold,
        step,
        out_tokens,
        capacity,
    )
    if n_tokens < 0:
        raise RuntimeError(f"Rust encoding failed with error {n_tokens}")

    return [(out_tokens[i].direction, out_tokens[i].magnitude, out_tokens[i].count) for i in range(n_tokens)]


@pytest.mark.skipif(LIB is None, reason="Rust dynamic library not built")
def test_python_rust_parity() -> None:
    rng = np.random.default_rng(42)

    for _ in range(100):
        length = int(rng.integers(50, 500))
        signal = np.cumsum(rng.normal(0, 0.1, size=length))

        mode = CodecMode.TRANSPORT if rng.integers(0, 2) == 0 else CodecMode.CLINICAL
        thr_mode = "adaptive_rms" if rng.integers(0, 2) == 0 else "fixed"
        threshold = 0.05
        step = 0.05

        python_tokens = python_encode(
            signal, mode=mode, thr_mode=thr_mode, threshold=threshold, step=step
        ).tokens
        rust_tokens = _rust_encode(
            signal, mode=mode, thr_mode=thr_mode, threshold=threshold, step=step
        )

        assert python_tokens == rust_tokens
