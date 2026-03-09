"""
DT-3: Determinism Test
PRD: §2.1 | INV-DET
PASS CONDITION: encode(x) == encode(x) for 10,000 random seeds
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np

from zpe_bio.codec import encode

SEEDS = 10_000
SIGNAL_LENGTH = 500

def main():
    print("Executing DT-3: Determinism (Repeatability Audit)...")
    print(f"Iterations: {SEEDS}")
    print("-" * 60)
    
    failures = 0
    for seed in range(SEEDS):
        rng = np.random.RandomState(seed)
        signal = rng.randn(SIGNAL_LENGTH)
        
        e1 = encode(signal, signal_type="ecg", thr_mode="adaptive_rms")
        e2 = encode(signal, signal_type="ecg", thr_mode="adaptive_rms")
        
        # Compare tokens and metadata
        if e1.tokens != e2.tokens or e1.start_value != e2.start_value or e1.threshold != e2.threshold:
            failures += 1
            if failures <= 5:
                print(f"FAIL: seed={seed} — non-deterministic output")

        if (seed + 1) % 2000 == 0:
            print(f"  {seed + 1}/{SEEDS} seeds verified...")

    print("-" * 60)
    if failures:
        print(f"DT-3 FAILED — {failures}/{SEEDS} non-deterministic encodings.")
        sys.exit(1)
    else:
        print(f"DT-3 PASSED — all {SEEDS} seeds matched byte-for-byte.")
        sys.exit(0)

if __name__ == "__main__":
    main()
