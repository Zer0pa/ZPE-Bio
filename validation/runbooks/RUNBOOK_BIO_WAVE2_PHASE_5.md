# RUNBOOK: BIO WAVE-2 PHASE 5 (Chemosense Bio)

## Commands
1. `.venv/bin/python -m zpe_bio chemosense-bio --json`
2. `.venv/bin/python -m pytest -q tests/test_chemosense_bio_cli.py`

## Outputs
- `validation/results/bio_wave2_phase5_chemosense.json`
- `tests/test_chemosense_bio_cli.py`

## Gate
- Combined smell+taste deterministic output with parseable metrics.

## Rollback
- Patch smell/taste integration and rerun.
