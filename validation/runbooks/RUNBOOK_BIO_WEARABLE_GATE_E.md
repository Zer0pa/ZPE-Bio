# RUNBOOK: BIO WEARABLE GATE E (Regression + Packaging + Adjudication)

## Commands
1. Full regression:
   - `.venv/bin/python -m pytest -q`
   - `scripts/run_repro_falsification.sh`
2. Packaging smoke:
   - `.venv/bin/python -m pip install .`
   - `.venv/bin/zpe-bio --help`
3. Build final adjudication docs:
   - `claim_status_delta.md`
   - `handoff_manifest.json`
   - Appendix C/E integration artifacts
4. Enforce rubric and hard-gate adjudication:
   - non-negotiables, M1..M4, E-G1..E-G5
   - GO only when no non-negotiable failure.

## Expected Artifacts
1. `regression_results.txt`
2. `claim_status_delta.md`
3. `handoff_manifest.json`
4. `integration_readiness_contract.json`
5. `residual_risk_register.md`
6. `innovation_delta_report.md`
7. `concept_open_questions_resolution.md`
8. `clinical_proxy_limitations.md`
9. `quality_gate_scorecard.json` (final rubric scoring + gate outcomes)
10. `concept_resource_traceability.json` and `max_claim_resource_map.json` finalized.

## Fail Signatures
1. Regression failure in legacy Bio wave guarantees.
2. Missing evidence path for any claim adjudication.
3. Required artifact set incomplete.
4. GO recommendation emitted despite failed hard gate or unresolved mandatory `IMP-*` bookkeeping.

## Rollback
1. Patch minimal failing component and rerun Gate E + failed prior dependencies.
