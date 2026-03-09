# RUNBOOK: BIO WAVE-1 PHASE 1 (Hygiene + Version Canonicalization)

## Commands
1. Inspect build/release artifact state:
   - `git status --short`
   - `ls -la build dist`
2. Validate version consistency:
   - `rg -n '__version__|version\\s*=\\s*\"' python pyproject.toml`
   - `.venv/bin/python -m zpe_bio version`

## Outputs
1. `validation/results/bio_wave1_phase1_hygiene.txt`
2. `validation/results/bio_wave1_phase1_version_consistency.txt`

## Gate
1. Version references are consistent for the current target package version.
2. No ambiguous mixed-version release metadata in tracked package files.

## Rollback
1. Patch inconsistent metadata and rerun Phase 1 checks.
