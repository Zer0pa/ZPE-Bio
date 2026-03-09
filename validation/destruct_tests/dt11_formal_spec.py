"""
DT-11: Formal Spec Test (Bounded Model Proxy)
PRD: §2.1 | INV-DET
PASS CONDITION: Bounded exhaustive checks satisfy invariants
EXIT CODE: 0 = PASS, 1 = FAIL

This is a bounded host-side proxy when full TLA+/Kani execution is unavailable.
"""
import itertools
import sys

import numpy as np

from zpe_bio.codec import encode, decode, CodecMode


def check_signal(signal: np.ndarray, mode: CodecMode, thr_mode: str) -> None:
    # INV-DET: same input -> same encoding
    e1 = encode(signal, mode=mode, thr_mode=thr_mode, signal_type="ecg")
    e2 = encode(signal, mode=mode, thr_mode=thr_mode, signal_type="ecg")
    if e1.tokens != e2.tokens:
        raise AssertionError("Non-deterministic token stream")

    # INV-INV (bounded): decode has same length and finite values
    rec = decode(e1)
    if len(rec) != len(signal):
        raise AssertionError("Length mismatch on decode")
    if not np.all(np.isfinite(rec)):
        raise AssertionError("Non-finite decode output")

    # INV-NOFLOW (bounded): no run length exceeds u16 max
    if any(count > 65535 for _, _, count in e1.tokens):
        raise AssertionError("RLE overflow detected")


def main():
    print("Executing DT-11: Formal Spec (Bounded Model Proxy)...")
    print("-" * 60)

    alphabet = [-0.2, -0.05, 0.0, 0.05, 0.2]
    length = 5
    total = 0

    for tup in itertools.product(alphabet, repeat=length):
        signal = np.array(tup, dtype=np.float64)
        # Prevent constant all-zero degenerate for coverage diversity.
        if np.all(signal == 0.0):
            signal = signal.copy()
            signal[0] = 0.01

        for mode in (CodecMode.TRANSPORT, CodecMode.CLINICAL):
            for thr_mode in ("fixed", "adaptive_rms"):
                check_signal(signal, mode, thr_mode)
                total += 1

    print(f"PASS: verified {total} bounded invariant checks ✅")
    sys.exit(0)


if __name__ == "__main__":
    main()
