# RUNBOOK: GATE B (External Baseline Comparator)

## Commands
1. Generate comparator artifact for ECG and EEG lanes with required fields:
   - `raw_bytes`, `gzip_bytes`, `zpe_bytes_est`, `prd_percent` (ECG), `encode_ms`, `decode_ms`
2. Validate comparator schema and non-empty rows.

## Gate Criteria
1. `bio_external_baseline_results.json` exists and is schema-complete.
2. ECG and EEG comparator rows are both present.

## Rollback
1. If schema/field coverage fails, patch metrics extraction logic and rerun Gate B.
