# Startup Prompt: Bio Wave-2 Biosignal Multimodal Agent

Execute only against:
1. PRD: `/Users/prinivenpillay/ZPE Bio/zpe-bio/docs/PRD_BIO_WAVE2_BIOSIGNAL_MULTIMODAL_EXECUTION.md`
2. Scope root: `/Users/prinivenpillay/ZPE Bio/zpe-bio`

## Mission
Implement code-first Bio Wave-2 execution: productized ECG/EEG CLI lanes, unified multimodal ECG+EEG stream demo, chemosense command hardening, and full falsification bundle.

## Hard Rules
1. Runbook-first is mandatory.
2. Do not work outside `/Users/prinivenpillay/ZPE Bio/zpe-bio`.
3. Do not modify IMC repo or other modality repos.
4. No clinical claim inflation; emit only measured metrics.
5. If a gate fails, patch and rerun that phase before proceeding.

## Required Sequence
1. Create runbooks:
   - `validation/runbooks/RUNBOOK_BIO_WAVE2_MASTER.md`
   - `validation/runbooks/RUNBOOK_BIO_WAVE2_PHASE_<N>.md`
2. Execute Phase 0 preflight with hard gap-closure attempts:
   - install deps (`.[validation]`, `mne`, `pyedflib`)
   - fetch EEG EDF samples from PhysioNet
   - record provenance and blocker map
3. Execute phases 0..6 in strict order.
4. Implement/verify CLI commands:
   - `encode-ecg`
   - `encode-eeg`
   - `benchmark`
   - `multimodal-stream`
   - `chemosense-bio`
5. Produce complete evidence artifacts and handoff manifest.

## Dependency and Data Rules
1. Use local MIT-BIH at `validation/datasets/mitdb` first.
2. EEG path must support:
   - real file mode (when deps + files available)
   - synthetic fallback mode (always available)
3. Missing optional dependencies are not acceptable without an install attempt.
4. Missing EEG files are not acceptable without a download attempt.
5. Any unresolved failure must be returned as blocker code with evidence:
   - `BLOCKER_ENV_NETWORK`
   - `BLOCKER_DEP_INSTALL`
   - `BLOCKER_SOURCE_UNAVAILABLE`
   - `BLOCKER_IO_PERMISSION`

## Required Artifacts (must exist)
1. `validation/results/bio_wave2_phase0_inventory.txt`
2. `validation/results/bio_wave2_phase0_baseline.txt`
3. `validation/results/bio_wave2_phase1_cli_contract.txt`
4. `validation/results/bio_wave2_phase2_ecg_benchmark.json`
5. `validation/results/bio_wave2_phase3_eeg_roundtrip.json`
6. `validation/results/bio_wave2_phase4_multimodal_stream.json`
7. `validation/results/bio_wave2_phase5_chemosense.json`
8. `validation/results/bio_wave2_phase6_falsification.md`
9. `validation/results/bio_wave2_phase6_dirty_campaign.json`
10. `validation/results/bio_wave2_phase6_determinism.json`
11. `validation/results/BIO_WAVE2_EXECUTION_READINESS_REPORT.md`
12. `validation/results/BIO_WAVE2_HANDOFF_MANIFEST.json` with `required_files_complete=true`
13. `validation/results/bio_wave2_resource_manifest.json`
14. `validation/results/bio_wave2_preflight_blockers.json`

## Completion Contract
Return only when:
1. all phase gates are green,
2. required artifact list is complete,
3. final summary includes:
   - gate-by-gate PASS/FAIL,
   - command list executed,
   - residual risks,
   - explicit GO/NO-GO recommendation.

If blocked, return:
1. exact blocker,
2. evidence/log snippet,
3. minimum remediation command to unblock,
4. confirmation that install/download retries were attempted.
