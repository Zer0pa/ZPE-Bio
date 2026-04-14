# Phase 4 External Blockers

## Blocker 1: Human Equivalence Labels

- Status: `SUSPENDED_BY_OWNER` (2026-02-12)
- Missing artifact: completed cardiologist evaluation labels for 100 blinded trace pairs.
- Expected input files:
  - completed form based on `docs/regulatory/templates/cardiologist_eval_form.md`
  - machine-readable labels (`label_original`, `label_compressed`) for kappa calculation
- Owner: clinical/cardiology evaluation team
- Unblocks:
  - `docs/regulatory/DOC-012_HUMAN_EQUIVALENCE_GATE_REPORT.md`
  - Phase 4 completion gate `kappa >= 0.85`

## Blocker 2: Regulatory Pathway Final Sign-Off

- Status: `SUSPENDED_BY_OWNER` (2026-02-12)
- Missing artifact: formal decision memo with accountable sign-off for 510(k) vs De Novo pathway.
- Current state: provisional memo exists at `docs/regulatory/PATHWAY_DECISION.md`.
- Owner: regulatory affairs + legal
- Unblocks:
  - finalization of submission package checklist
  - Phase 4 gate line `Regulatory pathway determined`

## Suspension Directive

By owner instruction (2026-02-12), these blockers are parked and do not halt internal execution tracks.  
They remain mandatory for final regulatory closeout and can be resumed when external artifacts arrive.
