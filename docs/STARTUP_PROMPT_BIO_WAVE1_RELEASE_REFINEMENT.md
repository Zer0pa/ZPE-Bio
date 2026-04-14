# Startup Prompt: Bio Wave-1 Coordinated Release Refinement Agent

Execute only against:
- PRD: `docs/PRD_BIO_WAVE1_RELEASE_REFINEMENT.md`
- Scope root: `<repo-root>`

## Mission
Execute Bio release refinement end-to-end, enforce deterministic parity, and publish IMC alignment artifacts for coordinated family release.

## Hard Rules
1. Runbook-first required.
2. Code execution required; do not stop at planning.
3. Modify only inside `<repo-root>`.
4. Maintain sector separation (no importing IMC runtime code).
5. IMC coordination is artifact-level only.
6. On any failed gate: patch and rerun full phase gates.

## Required Sequence
1. Create:
   - `validation/runbooks/RUNBOOK_BIO_WAVE1_MASTER.md`
   - `validation/runbooks/RUNBOOK_BIO_WAVE1_PHASE_<N>.md`
2. Execute Phases 0..6 in strict order.
3. Read IMC family contract artifacts when Phase 5 is reached.
4. Generate Bio compatibility outputs.
5. Produce final readiness report.

## Required Artifacts
1. `validation/results/BIO_WAVE1_RELEASE_READINESS_REPORT.md`
2. `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
3. `docs/family/BIO_COMPATIBILITY_VECTOR.json`
4. `docs/family/BIO_RELEASE_NOTE_FOR_COORDINATION.md`
5. Phase logs in `validation/results`.

## Completion Contract
Return only when:
1. all P0 gates pass,
2. parity + golden compatibility checks are green,
3. unresolved issues include owner + exact next command.
