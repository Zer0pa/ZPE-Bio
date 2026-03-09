# Public Audit Limits

This repo is currently a private staged snapshot. Public-audit language must remain narrower than the committed proof history.

## Hard Limits

- Current committed readiness reports were not rerun in this phase.
- Bio Wearable remains `NO_GO` and must not be flattened into a generic Bio pass claim.
- Large EEG, SisFall, and wearable dataset mirrors are local-only and intentionally excluded from the staged git surface.
- Historical proof artifacts retain host-specific absolute paths and command traces.

## How To Read This Repo Honestly

- Read code and packaging files as current repo truth.
- Read `validation/results/` as committed historical evidence.
- Read missing reruns as unresolved, not implied green.
- Read operator-only or local-only datasets as prerequisites for later verification phases, not as shipped repo guarantees.

## Required Companion Files

- `README.md`
- `PROOF_INDEX.md`
- `AUDITOR_PLAYBOOK.md`
- `docs/ARCHITECTURE.md`
- `docs/LEGAL_BOUNDARIES.md`
