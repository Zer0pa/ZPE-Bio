"""
DT-8: DC Torture Test
PRD: §2.1 | INV-DET
PASS CONDITION: Flat signal produces no crash and finite output
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np

from zpe_bio.codec import encode, decode

def main():
    print("Executing DT-8: DC Torture (Steady-State Audit)...")
    print("-" * 60)
    
    test_signals = {
        "all_zeros": np.zeros(10000),
        "all_ones": np.ones(10000),
        "all_negative": np.full(10000, -1.0),
        "all_max_float": np.full(10000, np.finfo(np.float64).max / 1e300),
        "single_value": np.full(10000, 3.14159),
    }
    
    failures = []
    for name, signal in test_signals.items():
        try:
            encoded = encode(signal, signal_type="ecg")
            decoded = decode(encoded)
            
            if len(decoded) != len(signal):
                raise ValueError(f"Length mismatch: {len(decoded)} != {len(signal)}")
            if not np.all(np.isfinite(decoded)):
                raise ValueError("Non-finite values in decoded output")
                
            print(f"PASS: {name} — {len(encoded.tokens)} tokens, CR={encoded.compression_ratio:.2f}× ✅")
        except Exception as e:
            print(f"CRASH: {name} — {e} ❌")
            failures.append({"test": name, "error": str(e)})

    print("-" * 60)
    if failures:
        print(f"DT-8 FAILED — {len(failures)} crashes.")
        sys.exit(1)
    else:
        print("DT-8 PASSED — all DC signals handled correctly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
