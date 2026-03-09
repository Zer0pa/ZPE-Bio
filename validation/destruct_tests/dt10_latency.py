"""
DT-10: Latency Test
PRD: §2.1 | REQ-EMBED-3
PASS CONDITION: Rust encode() < 1ms for a 250-sample window
EXIT CODE: 0 = PASS, 1 = FAIL

Host-side proxy: benchmarks the release Rust core through FFI.
"""
import ctypes
import sys
import time
from pathlib import Path

import numpy as np


class RustToken(ctypes.Structure):
    _fields_ = [
        ("direction", ctypes.c_uint8),
        ("magnitude", ctypes.c_uint8),
        ("count", ctypes.c_uint16),
    ]


def find_library(project_root: Path) -> Path:
    candidates = [
        project_root / "core" / "rust" / "target" / "x86_64-apple-darwin" / "release" / "libzpe_bio_codec.dylib",
        project_root / "core" / "rust" / "target" / "release" / "libzpe_bio_codec.dylib",
        project_root / "core" / "rust" / "target" / "release" / "libzpe_bio_codec.so",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Rust codec library not found; build core/rust in release mode first")


def main() -> None:
    print("Executing DT-10: Latency (Rust Core Audit)...")
    print("-" * 60)

    project_root = Path(__file__).resolve().parents[2]
    lib_path = find_library(project_root)
    lib = ctypes.CDLL(str(lib_path))

    lib.zpe_encode.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_size_t,
        ctypes.c_uint8,
        ctypes.c_uint8,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.POINTER(RustToken),
        ctypes.c_size_t,
    ]
    lib.zpe_encode.restype = ctypes.c_int32

    signal = np.random.RandomState(42).randn(250).astype(np.float64)
    samples_ptr = signal.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    out_capacity = 1024
    out_tokens = (RustToken * out_capacity)()

    mode_idx = 1       # Clinical
    thr_mode_idx = 0   # Fixed
    threshold = 0.001
    step = 0.001

    for _ in range(50):
        n_tokens = lib.zpe_encode(
            samples_ptr,
            signal.size,
            mode_idx,
            thr_mode_idx,
            threshold,
            step,
            out_tokens,
            out_capacity,
        )
        if n_tokens < 0:
            print(f"FAIL: Rust warmup encode returned {n_tokens}")
            sys.exit(1)

    iterations = 5000
    latencies_ms = np.empty(iterations, dtype=np.float64)

    for i in range(iterations):
        t0 = time.perf_counter_ns()
        n_tokens = lib.zpe_encode(
            samples_ptr,
            signal.size,
            mode_idx,
            thr_mode_idx,
            threshold,
            step,
            out_tokens,
            out_capacity,
        )
        t1 = time.perf_counter_ns()

        if n_tokens < 0:
            print(f"FAIL: Rust encode returned {n_tokens}")
            sys.exit(1)

        latencies_ms[i] = (t1 - t0) / 1_000_000.0

    avg_latency_ms = float(np.mean(latencies_ms))
    p99_latency_ms = float(np.percentile(latencies_ms, 99))
    gate_ms = 1.0

    print(f"Library:      {lib_path}")
    print(f"Mean latency: {avg_latency_ms:.4f} ms")
    print(f"P99 latency:  {p99_latency_ms:.4f} ms")

    if avg_latency_ms < gate_ms and p99_latency_ms < gate_ms:
        print(f"PASS: Latency gate satisfied (< {gate_ms:.1f}ms)")
        sys.exit(0)

    print(f"FAIL: Latency gate violated (mean/p99 must be < {gate_ms:.1f}ms)")
    sys.exit(1)


if __name__ == "__main__":
    main()
