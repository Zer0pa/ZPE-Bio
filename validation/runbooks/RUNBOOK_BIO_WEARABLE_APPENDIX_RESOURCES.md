# RUNBOOK: BIO WEARABLE APPENDIX B/E RESOURCE LEDGER

## Resource Attempt Matrix (No-Skip Core)
1. PTB-XL (primary ECG source)
2. MIMIC-IV-ECG (credentialed)
3. WFDB ingest/export
4. PhysioNet provenance lock
5. HealthyPi Move path (or nearest open hardware proxy)
6. NeuroKit2 validation path
7. OpenECG comparator conventions
8. Biosignal Compression Toolbox incumbent baseline
9. MERIT motion-artifact stress alignment
10. MIT-BIH arrhythmia
11. Pulse Transit Time PPG
12. Wearable stress+exercise dataset
13. Rhythm-SNN reference
14. Synthetic biosignal bootstrap path (fallback only)

## Attempt Procedure (Per Resource)
1. Record command and UTC.
2. Record status: `PASS` or `IMP-*`.
3. If `IMP-*`, include:
   - error signature
   - fallback chosen
   - affected claims
   - comparability impact

## Provenance Lock Fields
1. source URL/path
2. retrieval timestamp
3. dataset/version identifier
4. hash/snapshot metadata (when available)
5. license/access class

## Output Mapping
1. `max_resource_lock.json`
2. `max_resource_validation_log.md`
3. `max_claim_resource_map.json`
4. `impracticality_decisions.json`
5. `credential_status_log.json`
6. `concept_resource_traceability.json`
7. `net_new_gap_closure_matrix.json`

## Gate Checks
1. `E-G1`: every listed resource has an attempt row with command evidence.
2. `E-G2`: synthetic-only evidence cannot close a claim when open real data path exists.
3. `E-G3`: credential-gated resources include explicit request/access state in `credential_status_log.json`.
4. `E-G4`: every skipped resource references a valid `IMP-*` decision object.
5. `E-G5`: if any item is `IMP-COMPUTE`, emit RunPod readiness artifacts.
