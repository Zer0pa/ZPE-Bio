"""
DT-1: Shape Destruction Test
PRD: §2.1 | INV-INV | REQ-CODEC-1
PASS CONDITION: PRD < 5.0% on ALL 48 MIT-BIH records
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import wfdb
from pathlib import Path

from zpe_bio.codec import encode, decode, compute_prd

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
PRD_THRESHOLD = 5.0  # percent — from PRD §1.4

MIT_BIH_RECORDS = [
    "100", "101", "102", "103", "104", "105", "106", "107",
    "108", "109", "111", "112", "113", "114", "115", "116",
    "117", "118", "119", "121", "122", "123", "124",
    "200", "201", "202", "203", "205", "207", "208",
    "209", "210", "212", "213", "214", "215", "217",
    "219", "220", "221", "222", "223", "228", "230",
    "231", "232", "233", "234",
]

def main():
    print("Executing DT-1: Shape Destruction (Fidelity Audit)...")
    print(f"Threshold: {PRD_THRESHOLD}% PRD")
    print("-" * 60)
    
    failures = []
    for rec_id in MIT_BIH_RECORDS:
        try:
            record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
            signal = record.p_signal[:, 0]
            # Use CLINICAL mode for fidelity audit
            encoded = encode(signal, thr_mode="adaptive_rms", signal_type="ecg")
            reconstructed = decode(encoded)
            
            min_len = min(len(signal), len(reconstructed))
            prd = compute_prd(signal[:min_len], reconstructed[:min_len])
            
            if prd >= PRD_THRESHOLD:
                failures.append({"record": rec_id, "prd": round(prd, 3)})
                print(f"FAIL: {rec_id} PRD={prd:.3f}% ❌")
            else:
                print(f"PASS: {rec_id} PRD={prd:.3f}% ✅")
        except Exception as e:
            print(f"ERROR: {rec_id} — {e} ❌")
            failures.append({"record": rec_id, "error": str(e)})

    print("-" * 60)
    if failures:
        print(f"DT-1 FAILED — {len(failures)}/{len(MIT_BIH_RECORDS)} records failed.")
        sys.exit(1)
    else:
        print(f"DT-1 PASSED — all {len(MIT_BIH_RECORDS)} records meet the gate.")
        sys.exit(0)

if __name__ == "__main__":
    main()
