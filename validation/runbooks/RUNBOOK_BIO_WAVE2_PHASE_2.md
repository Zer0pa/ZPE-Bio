# RUNBOOK: BIO WAVE-2 PHASE 2 (ECG Productization)

## Commands
1. `.venv/bin/python -m zpe_bio encode-ecg --record-id 100 --json`
2. `.venv/bin/python -m zpe_bio benchmark --lane ecg --record-ids 100,103,114,200,223 --json`

## Outputs
- `validation/results/bio_wave2_phase2_ecg_smoke.txt`
- `validation/results/bio_wave2_phase2_ecg_benchmark.json`

## Gate
- >=5 records processed with PRD + CR + latency metrics.

## Rollback
- Patch ingest/metric code and rerun benchmark gate.
