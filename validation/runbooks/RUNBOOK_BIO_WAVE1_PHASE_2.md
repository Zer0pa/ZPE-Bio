# RUNBOOK: BIO WAVE-1 PHASE 2 (Runtime Surface Hardening)

## Commands
1. CLI contract and install smoke:
   - `.venv/bin/python -m zpe_bio --help`
   - `.venv/bin/zpe-bio --help`
   - `.venv/bin/python -m pytest -q tests/test_cli_biosignal_commands.py tests/test_multimodal_cli.py`
2. Dependency lane check:
   - `.venv/bin/python -m zpe_bio encode-eeg --synthetic-eeg --json`
   - `.venv/bin/python -m zpe_bio encode-eeg --edf validation/datasets/eeg/SC4001E0-PSG.edf --json`
3. Unsupported-version decode behavior:
   - run packet compatibility test targeting malformed/unsupported version words.

## Outputs
1. `validation/results/bio_wave1_phase2_cli_contract.txt`
2. `validation/results/bio_wave1_phase2_dependency_lanes.txt`

## Gate
1. CLI contract stable and parseable.
2. Optional dependency lanes are explicit and tested.
3. Unsupported version decode path returns controlled error behavior (no uncaught crash).

## Rollback
1. Patch CLI/decode handlers and rerun full Phase 2 checks.
