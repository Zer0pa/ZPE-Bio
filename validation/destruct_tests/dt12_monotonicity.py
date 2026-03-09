"""
DT-12: Monotonicity Test
PRD: §2.1 | REQ-CODEC-2
PASS CONDITION: As threshold increases, CR monotonically increases.
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import wfdb
from pathlib import Path

from zpe_bio.codec import encode

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
TEST_RECORDS = ["100", "103", "200", "207", "223"]
THRESHOLDS = [0.01, 0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30]

def main():
    print("Executing DT-12: Monotonicity (Quantiser Behaviour Audit)...")
    print("-" * 60)
    
    failures = []
    for rec_id in TEST_RECORDS:
        try:
            record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
            signal = record.p_signal[:, 0]
            
            prev_cr = 0.0
            crs = []
            
            for thr in THRESHOLDS:
                enc = encode(signal, threshold=thr, thr_mode="fixed", signal_type="ecg")
                cr = enc.compression_ratio
                crs.append(cr)
                if cr < prev_cr - 1e-6: # Float epsilon
                    print(f"FAIL: {rec_id} @ thr={thr}: CR dropped from {prev_cr:.2f} to {cr:.2f}")
                    failures.append(rec_id)
                    break
                prev_cr = cr
            else:
                print(f"PASS: {rec_id} — CR monotonic increase: {[round(c, 2) for c in crs]} ✅")
        except Exception as e:
            print(f"ERROR: {rec_id} — {e} ❌")
            failures.append(rec_id)

    print("-" * 60)
    if failures:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
