# RUNBOOK: BIO WEARABLE GATE B (Modality Pipeline Build)

## Commands
1. Install/verify wearable dependencies:
   - `pip install neurokit2 wfdb`
2. Build/execute wearable augmentation runner:
   - generate ECG/PPG/IMU benchmark outputs
   - generate morphology/alignment/AF/fall/latency eval outputs
3. Validate required JSON schemas and required keys.
4. Preserve synthetic fallback only as explicitly flagged bootstrap path (cannot close real-data-available claims).

## Expected Artifacts
1. `bio_wear_ecg_benchmark.json`
2. `bio_wear_ppg_benchmark.json`
3. `bio_wear_imu_benchmark.json`
4. `bio_wear_morphology_eval.json`
5. `bio_wear_alignment_eval.json`
6. `bio_wear_af_eval.json`
7. `bio_wear_fall_eval.json`
8. `bio_wear_embedded_latency.json`

## Fail Signatures
1. Missing modality artifact files.
2. Unhandled exceptions during modality encode/decode.
3. Synthetic-only closure for claims where open real resources were available.
4. Resource provenance missing from modality artifacts.

## Rollback
1. Patch modality loader/eval functions, rerun Gate B and revalidate schema.
