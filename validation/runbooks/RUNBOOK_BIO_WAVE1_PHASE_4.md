# RUNBOOK: BIO WAVE-1 PHASE 4 (CI + Release Workflow)

## Commands
1. Validate workflow syntax and required jobs:
   - inspect `.github/workflows/ci-python.yml`
   - inspect `.github/workflows/ci-rust.yml`
   - inspect `.github/workflows/release-skeleton.yml`
2. Local command parity with workflows:
   - `.venv/bin/python -m ruff check python scripts validation`
   - `.venv/bin/python -m pytest -q`
   - `cd core/rust && cargo fmt --check && cargo clippy --release -- -D warnings`

## Outputs
1. `validation/results/bio_wave1_phase4_ci.txt`
2. `validation/results/bio_wave1_phase4_release_pipeline.txt`

## Gate
1. CI workflows enforce parity and quality checks.
2. Release workflow is publish-ready with integrity-verification steps.

## Rollback
1. Patch workflows and rerun Phase 4 checks.
