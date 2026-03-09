"""
DT-15: Adaptive Threshold Test
PRD: §2.1 | INV-INV, REQ-CODEC-4
PASS CONDITION: adaptive_rms PRD <= fixed-mode PRD (within tolerance)
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import wfdb
from pathlib import Path

from zpe_bio.codec import encode, decode, compute_prd

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
TOLERANCE = 1.0 

TEST_RECORDS = ["100", "103", "114", "200", "207", "223"]

def main():
    print("Executing DT-15: Adaptive Threshold (Envelope Tracking Audit)...")
    print("-" * 60)
    
    failures = []
    for rec_id in TEST_RECORDS:
        try:
            record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
            signal = record.p_signal[:, 0]
            
            # Fixed mode
            enc_fixed = encode(signal, thr_mode="fixed", signal_type="ecg")
            dec_fixed = decode(enc_fixed)
            prd_fixed = compute_prd(signal, dec_fixed)
            
            # Adaptive RMS mode
            enc_adapt = encode(signal, thr_mode="adaptive_rms", signal_type="ecg")
            dec_adapt = decode(enc_adapt)
            prd_adapt = compute_prd(signal, dec_adapt)
            
            if prd_adapt > prd_fixed + TOLERANCE:
                print(f"FAIL: {rec_id} — Adaptive PRD {prd_adapt:.2f}% significantly worse than fixed {prd_fixed:.2f}% ❌")
                failures.append(rec_id)
            else:
                print(f"PASS: {rec_id} — Adaptive {prd_adapt:.2f}% vs Fixed {prd_fixed:.2f}% ✅")
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
