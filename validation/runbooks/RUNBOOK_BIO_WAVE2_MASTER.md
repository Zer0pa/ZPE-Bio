# RUNBOOK: BIO WAVE-2 MASTER

## Scope
- Repo root: `/Users/zer0pa-build/ZPE Bio/zpe-bio`
- PRD source: `docs/PRD_BIO_WAVE2_BIOSIGNAL_MULTIMODAL_EXECUTION.md`

## Execution Order (Strict)
1. Phase 0: preflight + baseline freeze
2. Phase 1: CLI surface expansion
3. Phase 2: ECG productization and benchmark lane
4. Phase 3: EEG ingest + mental-lane mapping
5. Phase 4: unified ECG+EEG multimodal stream
6. Phase 5: chemosense-bio hardening
7. Phase 6: falsification + determinism + package smoke

## Global Rules
1. Execute only inside this repo.
2. If a phase gate fails, patch and rerun that phase before continuing.
3. Preserve conservative claim language and measured metrics only.
4. Record all required evidence artifacts under `validation/results/`.

## Gate Matrix
- Phase 0 gate: baseline complete, preflight attempts logged, blocker map written.
- Phase 1 gate: new commands visible in `zpe-bio --help`, CLI contract artifact written.
- Phase 2 gate: >=5 MIT-BIH records process end-to-end with PRD+CR metrics.
- Phase 3 gate: real EEG path works when deps+file exist, synthetic fallback always works.
- Phase 4 gate: unified stream roundtrip succeeds, deterministic replay hash stable.
- Phase 5 gate: combined smell+taste command deterministic and parseable.
- Phase 6 gate: dirty campaign has zero uncaught crashes; determinism and package smoke pass.

## Rollback Policy
- Keep edits scoped by phase.
- On gate failure: patch minimal code path; rerun failing phase gate + dependent smoke.
- Do not claim GO until all phase gates and required artifacts are complete.
