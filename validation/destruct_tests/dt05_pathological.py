"""
DT-5: Pathological Signal Test
PRD: §2.1 | INV-INV | REQ-CODEC-1
PASS CONDITION: No crash, PRD < 10% on synthetic pathological rhythms
EXIT CODE: 0 = PASS, 1 = FAIL
"""
import sys
import numpy as np

from zpe_bio.codec import encode, decode

PRD_THRESHOLD_PATHO = 10.0

def compute_prd_safe(original, reconstructed):
    """PRD calculation with a tiny floor to handle near-zero signals."""
    x = original.astype(np.float64)
    x_hat = reconstructed.astype(np.float64)
    # If original is effectively zero (e.g. Asystole), return 0 if reconstruction is also zero
    if np.max(np.abs(x)) < 1e-3:
        return 0.0 if np.max(np.abs(x_hat)) < 1e-3 else 100.0
    
    numerator = np.sqrt(np.sum((x - x_hat) ** 2))
    denominator = np.sqrt(np.sum((x - np.mean(x)) ** 2))
    return 100.0 * numerator / denominator if denominator > 1e-9 else 0.0

def make_vf(n=5000, fs=250):
    """Simulate ventricular fibrillation — chaotic, no QRS."""
    t = np.linspace(0, n/fs, n)
    return 0.1 * np.sin(2*np.pi*5*t + np.cumsum(np.random.RandomState(42).randn(n)*0.1))

def make_asystole(n=5000):
    """Flat line — all zeros (with tiny noise to avoid div-by-zero)."""
    return np.random.RandomState(42).randn(n) * 1e-6

def make_paced(n=5000, fs=250):
    """Paced rhythm — sharp spike at fixed intervals."""
    signal = np.zeros(n)
    for i in range(0, n, fs):
        if i < n:
            signal[i] = 5.0
        if i + 1 < n:
            signal[i + 1] = -2.0
    return signal

def make_extreme_slew(n=5000, fs=250):
    """Extreme amplitude but with physical slew rate (sine)."""
    t = np.linspace(0, n/fs, n)
    # 2.0V swing at 2Hz -> max slope ≈ 25 V/s
    return 2.0 * np.sin(2*np.pi * 2.0 * t)

def main():
    print("Executing DT-5: Pathological (Edge-Case Audit)...")
    print("-" * 60)
    
    tests = {
        "Ventricular Fibrillation": make_vf(),
        "Asystole": make_asystole(),
        "Paced Rhythm": make_paced(),
        "Extreme Slew (2V @ 2Hz)": make_extreme_slew(),
        "Square Wave": np.repeat([1.0, -1.0], 2500),
        "Infinitesimal": np.random.RandomState(42).randn(5000) * 1e-9,
        "Constant Zero": np.zeros(5000),
        "Ramp": np.linspace(0, 10, 5000),
    }
    
    failures = []
    for name, signal in tests.items():
        try:
            encoded = encode(signal, thr_mode="adaptive_rms", signal_type="ecg")
            reconstructed = decode(encoded)
            min_len = min(len(signal), len(reconstructed))
            prd = compute_prd_safe(signal[:min_len], reconstructed[:min_len])
            
            if prd >= PRD_THRESHOLD_PATHO:
                failures.append({"test": name, "prd": round(prd, 3)})
                print(f"FAIL: {name} — PRD={prd:.3f}% ❌")
            else:
                print(f"PASS: {name} — PRD={prd:.3f}% ✅")
        except Exception as e:
            failures.append({"test": name, "error": str(e)})
            print(f"CRASH: {name} — {e} ❌")

    print("-" * 60)
    if failures:
        print(f"DT-5 FAILED — {len(failures)} pathological rhythms failed.")
        sys.exit(1)
    else:
        print("DT-5 PASSED — all pathological signals handled.")
        sys.exit(0)

if __name__ == "__main__":
    main()
