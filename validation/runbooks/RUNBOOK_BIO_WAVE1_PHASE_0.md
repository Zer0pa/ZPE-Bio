# RUNBOOK: BIO WAVE-1 PHASE 0 (Baseline Freeze)

## Commands
1. Verify IMC freeze:
   - `shasum -a 256 '/Users/prinivenpillay/ZPE Multimodality/ZPE-IMC/v0.0/docs/family/IMC_COMPATIBILITY_VECTOR.json'`
   - Parse `contract_version` from IMC vector and IMC interface contract.
2. Capture baseline inventory:
   - `python -m pip show zpe-bio`
   - `.venv/bin/python -m zpe_bio --help`
   - `find .github/workflows -maxdepth 1 -type f`
3. Baseline chain:
   - `scripts/run_repro_falsification.sh`
   - `.venv/bin/python -m pytest -q`
   - `cd core/rust && cargo test --release`

## Outputs
1. `validation/results/bio_wave1_phase0_inventory.txt`
2. `validation/results/bio_wave1_phase0_baseline.txt`

## Gate
1. IMC hash/version match pinned values.
2. Baseline chain commands pass.

## Rollback
1. If any baseline command fails: patch environment/code as needed, rerun full Phase 0 chain.
