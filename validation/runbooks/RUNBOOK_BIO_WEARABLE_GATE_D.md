# RUNBOOK: BIO WEARABLE GATE D (Falsification + Determinism)

## Commands
1. Adversarial malformed packet campaign (DT-BIO-WEAR-1).
2. Motion-artifact stress campaign for ECG/PPG alignment (DT-BIO-WEAR-2).
3. AF/fall imbalance stress campaign (DT-BIO-WEAR-3).
4. Determinism replay 5/5 hash-consistency (DT-BIO-WEAR-4).
5. Dependency/resource failure simulation (DT-BIO-WEAR-5).
6. Map DT outcomes into maximalization gates M2 and M3.

## Expected Artifacts
1. `falsification_results.md`
2. `determinism_replay_results.json`
3. `net_new_gap_closure_matrix.json` (updated with DT outcomes)
4. `claim_status_delta.md` (intermediate draft with C006/C007 stress results)

## Fail Signatures
1. Any uncaught crash in stress campaign.
2. Determinism hash mismatch.
3. Missing failure-mode evidence for unavailable resources.
4. AF/fall thresholds reported without class-balance stress evidence.

## Rollback
1. Patch failure handling/determinism path and rerun Gate D fully.
