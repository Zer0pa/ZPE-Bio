"""
DT-7: Latch Freedom Test
PRD: §2.1 | INV-LATCH
PASS CONDITION: No hang on 1M sample stream
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np
import time

from zpe_bio.codec import encode

def main():
    print("Executing DT-7: Latch Freedom (Saturation Audit)...")
    print("-" * 60)
    
    # 1 million samples
    signal = np.random.RandomState(42).randn(1_000_000)
    
    start_time = time.time()
    try:
        # We use fixed threshold to emphasize RLE runs
        encode(signal, threshold=0.1, mode="transport")
        duration = time.time() - start_time
        print(f"PASS: 1M samples encoded in {duration:.2f}s ✅")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: Hang or crash — {e} ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
