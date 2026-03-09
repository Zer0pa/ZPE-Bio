# RUNBOOK: BIO WAVE-1 PHASE 5 (IMC Alignment Publication)

## Commands
1. Read frozen IMC artifacts:
   - `IMC_INTERFACE_CONTRACT.md`
   - `IMC_COMPATIBILITY_VECTOR.json`
   - `IMC_RELEASE_NOTE_FOR_BIO_IOT.md`
2. Generate Bio family artifacts in `docs/family/`.
3. Validate `BIO_COMPATIBILITY_VECTOR.json` required keys + pinned values.

## Outputs
1. `docs/family/BIO_IMC_ALIGNMENT_REPORT.md`
2. `docs/family/BIO_COMPATIBILITY_VECTOR.json`
3. `docs/family/BIO_RELEASE_NOTE_FOR_COORDINATION.md`
4. `validation/results/bio_wave1_phase5_alignment.txt`

## Gate
1. IMC freeze version/hash recorded exactly.
2. Machine-readable compatibility vector is valid and complete.
3. Metric authority pinned to compatibility vector (`total_words=844`).

## Rollback
1. Patch docs/vector schema and rerun Phase 5 validation.
