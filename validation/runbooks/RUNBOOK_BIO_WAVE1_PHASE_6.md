# RUNBOOK: BIO WAVE-1 PHASE 6 (RC Rehearsal + Readiness)

## Commands
1. Full local gates:
   - `scripts/run_repro_falsification.sh`
   - `.venv/bin/python -m pytest -q`
   - `cd core/rust && cargo test --release`
2. Packaging smoke:
   - `.venv/bin/python -m pip install .`
   - `.venv/bin/zpe-bio --help`

## Outputs
1. `validation/results/bio_wave1_phase6_rc_rehearsal.txt`
2. `validation/results/BIO_WAVE1_RELEASE_READINESS_REPORT.md`

## Gate
1. All P0 gates pass.
2. Parity and golden compatibility checks remain green after RC rehearsal.

## Rollback
1. Patch failing gate and rerun full Phase 6 rehearsal.
