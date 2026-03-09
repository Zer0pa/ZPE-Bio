# RUNBOOK: BIO WAVE-2 PHASE 1 (CLI Surface)

## Commands
1. Implement CLI commands: `encode-ecg`, `encode-eeg`, `benchmark`, `multimodal-stream`, `chemosense-bio`.
2. `.venv/bin/python -m pytest -q tests/test_cli_biosignal_commands.py`
3. `.venv/bin/python -m zpe_bio --help`

## Outputs
- `validation/results/bio_wave2_phase1_cli_contract.txt`
- `tests/test_cli_biosignal_commands.py`

## Gate
- All new commands listed in help and CLI contract artifact.

## Rollback
- Patch parser/validation errors and rerun command + tests.
