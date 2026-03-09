# RUNBOOK: BIO WEARABLE GATE A (Baseline + Resource Lock)

## Commands
1. Environment bootstrap:
   - `set -a; [ -f .env ] && source .env; set +a`
   - validate presence/failure signatures in command log.
2. Baseline lock:
   - `python -m json.tool validation/results/bio_wave2_phase2_ecg_benchmark.json`
   - `python -m json.tool validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json`
3. Resource lock attempts:
   - appendices B/E dataset/resource probes with command evidence.
   - `wfdb.get_record_list('ptb-xl/1.0.3')`
   - `wfdb.rdrecord('00001_lr', pn_dir='ptb-xl/1.0.3/records100/00000')`
   - `wfdb.rdrecord('100', pn_dir='mitdb')` or local MIT-BIH mirror
   - `wfdb.rdrecord('s1_walk', pn_dir='pulse-transit-time-ppg/1.1.0')`
   - `curl -fL https://physionet.org/files/wearable-device-dataset/1.0.1/...`
   - `wfdb.get_record_list('mimic-iv-ecg/1.0/files/p1000')` + record fetch attempt
   - comparator/document probes for OpenECG, MERIT, Rhythm-SNN, and Biosignal Compression Toolbox
   - hardware-proxy probe for HealthyPi Move references.

## Expected Artifacts
1. `max_resource_lock.json`
2. `max_resource_validation_log.md`
3. `credential_status_log.json`
4. `impracticality_decisions.json`
5. `concept_resource_traceability.json` (initial lock section)
6. `max_claim_resource_map.json` (initial mapping)
7. `net_new_gap_closure_matrix.json` (initial gap state)

## Fail Signatures
1. Missing baseline lock files.
2. `.env` missing or malformed export failures.
3. No command evidence for Appendix B/E resources.
4. Resource attempt missing fallback/comparability note when impractical.

## Rollback
1. Fix lock path/env issues; rerun Gate A fully before proceeding.
