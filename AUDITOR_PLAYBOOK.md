# Auditor Playbook

This is the shortest honest audit path for the staged ZPE-Bio repo on 2026-03-09.

It is a staged private repo audit path, not a public release audit path.

## Read First

1. `README.md`
2. `PROOF_INDEX.md`
3. `PUBLIC_AUDIT_LIMITS.md`
4. `docs/README.md`

## Lowest-Cost Runtime Check

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m zpe_bio --help
python -m zpe_bio roundtrip --mode clinical --samples 250
```

This verifies the staged package surface only.

## Evidence Anchors

- `validation/results/BIO_WAVE1_RELEASE_READINESS_REPORT.md`
- `validation/results/BIO_WAVE2_EXECUTION_READINESS_REPORT.md`
- `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
- `validation/results/2026-02-21_bio_wearable_closure/quality_gate_scorecard.json`

## Required Reading Discipline

- Read Wave-1 and Wave-2 readiness reports as historical adjudications, not fresh reruns.
- Read Bio Wearable as negative/mixed evidence unless a later verified rerun supersedes it.
- Read historical absolute paths inside result artifacts as execution lineage only.

## What This Playbook Does Not Grant

- It does not grant a public-release verdict.
- It does not grant a fresh green verification verdict.
- It does not grant a wearable closure verdict.
