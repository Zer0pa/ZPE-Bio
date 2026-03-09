"""
DT-16: PPG Codec Test
PRD: §2.1 | INV-INV, REQ-CODEC-5
PASS CONDITION: PRD < 8% on synthetic PPG waveforms
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np

from zpe_bio.codec import encode, decode, compute_prd

PPG_PRD_THRESHOLD = 8.0

def make_ppg(duration_s=10, fs=100, hr=72):
    n = duration_s * fs
    t = np.linspace(0, duration_s, n)
    beat_period = 60.0 / hr
    ppg = np.zeros(n)
    for beat_start in np.arange(0, duration_s, beat_period):
        t_rel = t - beat_start
        mask = (t_rel >= 0) & (t_rel < beat_period)
        systolic = np.exp(-((t_rel - 0.12) ** 2) / 0.004) * mask
        dicrotic = 0.3 * np.exp(-((t_rel - 0.35) ** 2) / 0.008) * mask
        ppg += systolic + dicrotic
    return ppg

def main():
    print("Executing DT-16: PPG Codec (Morgue-to-Light Audit)...")
    print("-" * 60)
    
    test_signals = {
        "Normal HR 72": make_ppg(hr=72),
        "Tachycardia 130": make_ppg(hr=130),
        "Low Amplitude": make_ppg(hr=72) * 0.1,
    }
    
    failures = []
    for name, signal in test_signals.items():
        try:
            encoded = encode(signal, signal_type="ppg", thr_mode="adaptive_rms")
            reconstructed = decode(encoded)
            prd = compute_prd(signal, reconstructed)
            if prd >= PPG_PRD_THRESHOLD:
                print(f"FAIL: {name} PRD={prd:.2f}% ❌")
                failures.append(name)
            else:
                print(f"PASS: {name} PRD={prd:.2f}% ✅")
        except Exception as e:
            print(f"ERROR: {name} — {e} ❌")
            failures.append(name)

    print("-" * 60)
    if failures:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
