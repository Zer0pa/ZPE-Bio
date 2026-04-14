# RUNBOOK: BIO EXTERNAL BASELINE + FIDELITY MASTER

## Scope
- Repo root: `<repo-root>`
- PRD source: `docs/PRD_BIO_EXTERNAL_BASELINE_AND_FIDELITY_2026-02-20.md`

## Execution Order (Strict)
1. Gate A: baseline replay and lock current benchmark artifacts.
2. Gate B: external baseline comparator generation.
3. Gate C: fidelity-optimization sweep (reproducible).
4. Gate D: chemosense claim-status runtime/test alignment.
5. Gate E: full regression + deterministic replay + packaging.

## Global Rules
1. Evidence-first: no closure claim without artifact.
2. Reproducibility-first: fixed seeds and command logging.
3. Stop on regressions in DT or crash safety.
4. Keep runtime path logic relative/env-driven (no machine-specific absolute paths).

## Required Artifact Root
- `validation/results/<DATE>_bio_external_baseline_fidelity/`

## Required Files
1. `handoff_manifest.json`
2. `before_after_metrics.json`
3. `bio_external_baseline_results.json`
4. `fidelity_sweep_results.json`
5. `falsification_results.md`
6. `claim_status_delta.md`
7. `command_log.txt`

## Rollback Policy
1. If gate fails, patch minimal failing path and rerun the same gate.
2. If DT regressions appear, halt and report NO-GO with evidence.
