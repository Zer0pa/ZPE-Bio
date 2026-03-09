# RUNBOOK: BIO WAVE-2 PHASE 4 (Unified Multimodal Stream)

## Commands
1. `.venv/bin/python -m zpe_bio multimodal-stream --record-id 100 --synthetic-eeg --json`
2. `.venv/bin/python -m pytest -q tests/test_multimodal_stream_ecg_eeg.py`

## Outputs
- `validation/results/bio_wave2_phase4_multimodal_stream.json`
- `tests/test_multimodal_stream_ecg_eeg.py`

## Gate
- Unified stream roundtrip and stable deterministic replay hash.

## Rollback
- Patch stream container encode/decode and rerun.
