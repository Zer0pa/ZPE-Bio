"""
DT-2: Compression Regret Test
PRD: §2.1 | REQ-CODEC-3
PASS CONDITION: CR > 1.0 on ALL MIT-BIH records
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np
import wfdb
from pathlib import Path

from zpe_bio.codec import encode, CodecMode

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
MIN_CR = 1.0
TARGET_CR = 5.0

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
    print("Executing DT-2: Compression Regret (Negative Value Audit)...")
    print("-" * 60)
    
    failures = []
    crs = []
    for rec_id in MIT_BIH_RECORDS:
        try:
            record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
            signal = record.p_signal[:, 0]
            # Compression gate should be tested in TRANSPORT mode.
            encoded = encode(signal, mode=CodecMode.TRANSPORT, thr_mode="adaptive_rms", signal_type="ecg")
            cr = encoded.compression_ratio
            crs.append(cr)
            
            if cr < MIN_CR:
                failures.append({"record": rec_id, "cr": round(cr, 3)})
                print(f"FAIL: {rec_id} CR={cr:.2f}× (Expansion) ❌")
            else:
                status = "✓" if cr >= TARGET_CR else "⚠️"
                print(f"PASS: {rec_id} CR={cr:.2f}× {status} ✅")
        except Exception as e:
            print(f"ERROR: {rec_id} — {e} ❌")
            failures.append({"record": rec_id, "error": str(e)})

    mean_cr = np.mean(crs) if crs else 0
    print("-" * 60)
    print(f"Mean CR: {mean_cr:.2f}×")
    
    if failures:
        print(f"DT-2 FAILED — {len(failures)} records expanded.")
        sys.exit(1)
    else:
        print("DT-2 PASSED — no compression regret observed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
