"""
DT-14: Side-Channel Timing Variance Test
PRD: §2.1 | REQ-SEC-1
PASS CONDITION: No extreme data-dependent timing spread
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import time

import numpy as np

from zpe_bio.codec import encode, CodecMode


def sample_timing(signal: np.ndarray, n: int = 500) -> np.ndarray:
    times = np.zeros(n, dtype=np.float64)
    for i in range(n):
        t0 = time.perf_counter_ns()
        encode(signal, mode=CodecMode.CLINICAL, thr_mode="adaptive_rms", signal_type="ecg")
        t1 = time.perf_counter_ns()
        times[i] = (t1 - t0) / 1e6
    return times


def main():
    print("Executing DT-14: Side-Channel (Timing Variance Audit)...")
    print("-" * 60)

    rng = np.random.RandomState(42)
    low_amp = rng.randn(250) * 0.01
    high_amp = rng.randn(250) * 1.00

    # Warm-up
    for _ in range(50):
        encode(low_amp, mode=CodecMode.CLINICAL, thr_mode="adaptive_rms", signal_type="ecg")
        encode(high_amp, mode=CodecMode.CLINICAL, thr_mode="adaptive_rms", signal_type="ecg")

    low_t = sample_timing(low_amp)
    high_t = sample_timing(high_amp)

    low_mean = float(np.mean(low_t))
    high_mean = float(np.mean(high_t))
    rel_diff = abs(high_mean - low_mean) / max(low_mean, 1e-9)

    print(f"Low amplitude mean:  {low_mean:.4f} ms")
    print(f"High amplitude mean: {high_mean:.4f} ms")
    print(f"Relative difference: {rel_diff:.4f}")

    # Conservative host threshold for "no extreme data-dependent timing".
    if rel_diff <= 0.35:
        print("PASS: No extreme timing variance detected ✅")
        sys.exit(0)

    print("FAIL: Timing variance exceeds threshold ❌")
    sys.exit(1)


if __name__ == "__main__":
    main()
