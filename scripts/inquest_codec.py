import wfdb
import numpy as np
import matplotlib.pyplot as plt
from zpe_bio.codec import encode, decode, compute_prd
import os

# Record 100
rec_id = "100"
db_dir = "validation/datasets/mitdb"
record = wfdb.rdrecord(os.path.join(db_dir, rec_id))
signal = record.p_signal[:1000, 0] # First 1000 samples

encoded = encode(signal, threshold=0.015, signal_type="ecg", thr_mode="fixed")
reconstructed = decode(encoded)

prd = compute_prd(signal, reconstructed)
print(f"Record {rec_id} (1000 samples)")
print(f"PRD: {prd:.2f}%")
print(f"CR: {encoded.compression_ratio:.2f}×")
print(f"Num Tokens: {encoded.num_tokens}")
print(f"Start Value: {encoded.start_value:.4f}")
print(f"Threshold: {encoded.threshold:.4f}, Step: {encoded.step:.4f}")

print("\nFirst 10 samples comparison (Raw vs Rec):")
for i in range(10):
    print(f"  {i}: {signal[i]:.4f} vs {reconstructed[i]:.4f} (err: {signal[i]-reconstructed[i]:.4f})")

# Check if signal is flat
print(f"\nSignal Std: {np.std(signal):.4f}")
print(f"Rec Std: {np.std(reconstructed):.4f}")
plt.plot(signal, label="Original", alpha=0.7)
plt.plot(reconstructed, label="Reconstructed", linestyle="--")
plt.title(f"ZPE-Bio Inquest: Record {rec_id} (PRD={prd:.1f}%)")
plt.legend()
plt.savefig("validation/results/inquest_100.png")
plt.close()
