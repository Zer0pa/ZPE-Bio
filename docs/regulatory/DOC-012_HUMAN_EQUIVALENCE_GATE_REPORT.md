# DOC-012: Human Equivalence Gate Report

**Document ID:** DOC-012  
**Version:** 1.0  
**Date:** 2026-02-12  
**Classification:** Custom regulatory gate

## 1. Gate Definition

Pass criterion: Cohen's kappa >= 0.85 between cardiologist classifications of original vs reconstructed traces.

## 2. Current Status

**SUSPENDED_BY_OWNER**

Reason: owner-directed park (2026-02-12) for cardiologist-labeled evaluation execution.

## 3. Required Inputs

1. 100 randomized paired MIT-BIH segments with blinded presentation.
2. Completed evaluator form from credentialed cardiologist.
3. Per-pair labels for original and reconstructed signals.

## 4. Computation Procedure

```python
from sklearn.metrics import cohen_kappa_score

kappa = cohen_kappa_score(label_original, label_compressed)
print(f"Cohen's kappa = {kappa:.3f}")
```

## 5. Decision Block

- kappa value: `PENDING`
- Gate outcome: `PENDING`
- Reviewer: `PENDING`
- Date: `PENDING`

## 6. Follow-up Actions After Data Arrival

- Populate final kappa value and confidence notes.
- Update `RUNBOOK_00_MASTER.md` Phase 4 status.
- Update `DOCUMENT_INDEX.md` status for DOC-012 to `COMPLETE`.
