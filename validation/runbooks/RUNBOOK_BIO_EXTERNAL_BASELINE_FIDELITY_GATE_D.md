# RUNBOOK: GATE D (Chemosense Claim Alignment)

## Commands
1. Update runtime chemosense claim status to non-placeholder wording.
2. Update tests to match runtime output contract.
3. Run targeted tests:
   - `.venv/bin/python -m pytest -q tests/test_chemosense_bio_cli.py`

## Gate Criteria
1. Runtime output no longer includes `placeholder_governed`.
2. Updated tests pass.

## Rollback
1. If test/regression fails, patch runtime/test contract and rerun Gate D.
