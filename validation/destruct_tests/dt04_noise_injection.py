"""
DT-4: Noise Injection Test
PRD: §2.1 | INV-INV | REQ-CODEC-4
PASS CONDITION: PRD < 7.5% under 10dB SNR noise on MIT-BIH
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np
import wfdb
from pathlib import Path

from zpe_bio.codec import encode, decode, compute_prd

MIT_BIH_DIR = Path(__file__).resolve().parents[1] / "datasets" / "mitdb"
PRD_THRESHOLD_NOISY = 7.5  # relaxed threshold for noisy signals
SNR_DB = 10 

# Use representative records
TEST_RECORDS = ["100", "103", "105", "108", "114", "200", "207", "210", "223", "233"]

def add_noise(signal, snr_db):
    """Add Gaussian noise at specified SNR."""
    sig_power = np.mean(signal ** 2)
    noise_power = sig_power / (10 ** (snr_db / 10))
    noise = np.random.RandomState(42).randn(len(signal)) * np.sqrt(noise_power)
    return signal + noise

def main():
    print("Executing DT-4: Noise Injection (Robustness Audit)...")
    print(f"SNR: {SNR_DB}dB | Threshold: {PRD_THRESHOLD_NOISY}% PRD")
    print("-" * 60)
    
    failures = []
    for rec_id in TEST_RECORDS:
        try:
            record = wfdb.rdrecord(str(MIT_BIH_DIR / rec_id))
            signal = record.p_signal[:, 0]
            noisy = add_noise(signal, SNR_DB)
            
            encoded = encode(noisy, thr_mode="adaptive_rms", signal_type="ecg")
            reconstructed = decode(encoded)
            
            min_len = min(len(noisy), len(reconstructed))
            prd = compute_prd(noisy[:min_len], reconstructed[:min_len])
            
            if prd >= PRD_THRESHOLD_NOISY:
                failures.append({"record": rec_id, "prd": round(prd, 3)})
                print(f"FAIL: {rec_id} PRD={prd:.3f}% ❌")
            else:
                print(f"PASS: {rec_id} PRD={prd:.3f}% ✅")
        except Exception as e:
            print(f"ERROR: {rec_id} — {e} ❌")
            failures.append({"record": rec_id, "error": str(e)})

    print("-" * 60)
    if failures:
        print(f"DT-4 FAILED — {len(failures)}/{len(TEST_RECORDS)} records fragile under noise.")
        sys.exit(1)
    else:
        print(f"DT-4 PASSED — noise robust at {SNR_DB}dB.")
        sys.exit(0)

if __name__ == "__main__":
    main()
