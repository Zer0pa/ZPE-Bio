# RUNBOOK: BIO WAVE-2 PHASE 3 (EEG + Mental Lane)

## Commands
1. `.venv/bin/python -m zpe_bio encode-eeg --edf validation/datasets/eeg/SC4001E0-PSG.edf --json`
2. `.venv/bin/python -m zpe_bio encode-eeg --synthetic-eeg --json`
3. `.venv/bin/python -m pytest -q tests/test_eeg_mental_mapping.py`

## Outputs
- `validation/results/bio_wave2_phase3_eeg_contract.txt`
- `validation/results/bio_wave2_phase3_eeg_roundtrip.json`
- `validation/results/bio_wave2_phase3_eeg_realfile_smoke.txt`
- `tests/test_eeg_mental_mapping.py`

## Gate
- Real EEG file path works when deps+files available.
- Synthetic fallback always succeeds.

## Rollback
- Patch optional dependency and fallback handling then rerun.
