# RUNBOOK: BIO WAVE-2 PHASE 6 (Falsification + Hardening)

## Commands
1. Run dirty-input campaign against all new commands.
2. Run determinism replay (>=5 repeats per command/case).
3. Run package smoke:
   - `.venv/bin/python -m pip install .`
   - `.venv/bin/zpe-bio --help`
4. `.venv/bin/python -m pytest -q`

## Outputs
- `validation/results/bio_wave2_phase6_falsification.md`
- `validation/results/bio_wave2_phase6_dirty_campaign.json`
- `validation/results/bio_wave2_phase6_determinism.json`
- `validation/results/bio_wave2_phase6_package_smoke.txt`
- `validation/results/BIO_WAVE2_EXECUTION_READINESS_REPORT.md`
- `validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json`

## Gate
- Zero uncaught crashes in dirty campaign.
- Determinism and package smoke pass.

## Rollback
- Patch parser/error handling/hashing issues and rerun failing checks.
