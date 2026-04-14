# RUNBOOK: BIO WAVE-1 MASTER

## Scope
- Repo root: `/Users/zer0pa-build/ZPE Bio/zpe-bio`
- PRD source: `docs/PRD_BIO_WAVE1_RELEASE_REFINEMENT.md`

## Execution Order (Strict)
1. Phase 0: baseline freeze + IMC freeze preflight verification
2. Phase 1: repo hygiene and version canonicalization
3. Phase 2: runtime surface hardening
4. Phase 3: parity and compatibility reinforcement
5. Phase 4: CI + release workflow finalization
6. Phase 5: IMC alignment publication
7. Phase 6: RC rehearsal and readiness report

## Global Rules
1. Runbook-first and gate-first execution.
2. If a phase gate fails: patch only that phase scope, rerun full phase gate, then continue.
3. No IMC runtime import coupling; use IMC files as static reference artifacts only.
4. Preserve deterministic behavior and Python/Rust parity requirements.
5. Write phase evidence into `validation/results/`.

## Pinned IMC Freeze
1. `contract_version` must be `wave1.0`.
2. `IMC_COMPATIBILITY_VECTOR.json` sha256 must be:
   `9c8b905f6c1d30d057955aa9adf0f7ff9139853494dca673e5fbe69f24fba10e`.
3. Canonical metric authority: compatibility vector (`total_words=844`).

## Rollback Policy
1. No destructive cleanup of unrelated user changes.
2. Keep changes minimal and phase-local.
3. Record exact rerun commands in phase logs.
