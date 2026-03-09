"""Compute Cohen's kappa for DOC-012 once evaluator labels are available."""
from sklearn.metrics import cohen_kappa_score

# Replace with actual extracted labels from blinded evaluation sheet.
label_original = []
label_compressed = []

if len(label_original) != len(label_compressed) or not label_original:
    raise SystemExit("Populate label_original and label_compressed with equal non-zero lengths.")

kappa = cohen_kappa_score(label_original, label_compressed)
print(f"Cohen's kappa = {kappa:.3f}")
print("PASS" if kappa >= 0.85 else "FAIL")
