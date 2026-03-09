# RUNBOOK: GATE E (Regression + Determinism + Packaging)

## Commands
1. Full tests: `.venv/bin/python -m pytest -q`
2. DT/repro: `scripts/run_repro_falsification.sh`
3. Determinism replay command(s) from fidelity runner.
4. Packaging smoke:
   - `.venv/bin/python -m pip install .`
   - `.venv/bin/zpe-bio --help`

## Gate Criteria
1. No DT regression.
2. Determinism checks pass.
3. Packaging and CLI smoke pass.

## Rollback
1. If any regression appears, stop and report NO-GO with failing gate evidence.
